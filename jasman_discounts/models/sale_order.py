import itertools
import random

from odoo import models
from odoo import _, api, fields, models
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
from odoo.fields import Command
from collections import defaultdict

def _generate_random_reward_code():
        return str(random.getrandbits(32))

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def remove_discounts_from_sale_order(self):
        for order_line in self.order_line:
            order_line.remove_discounts()              
    
    #OVERRIDE to use sale order line filter for loyalty.rule similarly on how product filter is used
    def _program_check_compute_points(self, programs):

        self.ensure_one()

        # Prepare quantities
        order_lines = self.order_line.filtered(lambda line: line.product_id and not line.reward_id)
        products = order_lines.product_id
        products_qties = dict.fromkeys(products, 0)
        for line in order_lines:
            products_qties[line.product_id] += line.product_uom_qty
        # Contains the products that can be applied per rule
        products_per_rule = programs._get_valid_products(products)
        #PATCH begins
        valid_order_lines = programs._get_valid_order_lines(order_lines)
        #PATCH ends

        # Prepare amounts
        no_effect_lines = self._get_no_effect_on_threshold_lines()
        base_untaxed_amount = self.amount_untaxed - sum(line.price_subtotal for line in no_effect_lines)
        base_tax_amount = self.amount_tax - sum(line.price_tax for line in no_effect_lines)
        amounts_per_program = {p: {'untaxed': base_untaxed_amount, 'tax': base_tax_amount} for p in programs}
        for line in self.order_line:
            if not line.reward_id or line.reward_id.reward_type != 'discount':
                continue
            for program in programs:
                # Do not consider the program's discount + automatic discount lines for the amount to check.
                if line.reward_id.program_id.trigger == 'auto' or line.reward_id.program_id == program:
                    amounts_per_program[program]['untaxed'] -= line.price_subtotal
                    amounts_per_program[program]['tax'] -= line.price_tax

        result = {}
        for program in programs:
            untaxed_amount = amounts_per_program[program]['untaxed']
            tax_amount = amounts_per_program[program]['tax']

            # Used for error messages
            # By default False, but True if no rules and applies_on current -> misconfigured coupons program
            code_matched = not bool(program.rule_ids) and program.applies_on == 'current' # Stays false if all triggers have code and none have been activated
            minimum_amount_matched = code_matched
            product_qty_matched = code_matched
            points = 0
            # Some rules may split their points per unit / money spent
            #  (i.e. gift cards 2x50$ must result in two 50$ codes)
            rule_points = []
            program_result = result.setdefault(program, dict())
            for rule in program.rule_ids:
                if rule.mode == 'with_code' and rule not in self.code_enabled_rule_ids:
                    continue
                code_matched = True
                rule_amount = rule._compute_amount(self.currency_id)
                if rule_amount > (rule.minimum_amount_tax_mode == 'incl' and (untaxed_amount + tax_amount) or untaxed_amount):
                    continue
                minimum_amount_matched = True
                #PATCH begins
                if not valid_order_lines.get(rule):
                    continue
                #PATCH ends
                if not products_per_rule.get(rule):
                    continue
                rule_products = products_per_rule[rule]
                ordered_rule_products_qty = sum(products_qties[product] for product in rule_products)
                if ordered_rule_products_qty < rule.minimum_qty or not rule_products:
                    continue
                product_qty_matched = True
                if not rule.reward_point_amount:
                    continue
                # Count all points separately if the order is for the future and the split option is enabled
                if program.applies_on == 'future' and rule.reward_point_split and rule.reward_point_mode != 'order':
                    if rule.reward_point_mode == 'unit':
                        rule_points.extend(rule.reward_point_amount for _ in range(int(ordered_rule_products_qty)))
                    elif rule.reward_point_mode == 'money':
                        for line in self.order_line:
                            if line.is_reward_line or line.product_id not in rule_products or line.product_uom_qty <= 0:
                                continue
                            points_per_unit = float_round(
                                (rule.reward_point_amount * line.price_total / line.product_uom_qty),
                                precision_digits=2, rounding_method='DOWN')
                            if not points_per_unit:
                                continue
                            rule_points.extend([points_per_unit] * int(line.product_uom_qty))
                else:
                    # All checks have been passed we can now compute the points to give
                    if rule.reward_point_mode == 'order':
                        points += rule.reward_point_amount
                    elif rule.reward_point_mode == 'money':
                        # Compute amount paid for rule
                        # NOTE: this does not account for discounts -> 1 point per $ * (100$ - 30%) will result in 100 points
                        amount_paid = sum(max(0, line.price_total) for line in order_lines if line.product_id in rule_products)
                        points += float_round(rule.reward_point_amount * amount_paid, precision_digits=2, rounding_method='DOWN')
                    elif rule.reward_point_mode == 'unit':
                        points += rule.reward_point_amount * ordered_rule_products_qty
            # NOTE: for programs that are nominative we always allow the program to be 'applied' on the order
            #  with 0 points so that `_get_claimable_rewards` returns the rewards associated with those programs
            if not program.is_nominative:
                if not code_matched:
                    program_result['error'] = _("This program requires a code to be applied.")
                elif not minimum_amount_matched:
                    program_result['error'] = _(
                        'A minimum of %(amount)s %(currency)s should be purchased to get the reward',
                        amount=min(program.rule_ids.mapped('minimum_amount')),
                        currency=program.currency_id.name,
                    )
                elif not product_qty_matched:
                    program_result['error'] = _("You don't have the required product quantities on your sales order.")
            elif not self._allow_nominative_programs():
                program_result['error'] = _("This program is not available for public users.")
            if 'error' not in program_result:
                points_result = [points] + rule_points
                program_result['points'] = points_result
        return result
    
    #OVERRIDE to return which discounts are being applied to which lines
    def _discountable_specific(self, reward):
        self.ensure_one()
        assert reward.discount_applicability == 'specific'

        lines_to_discount = self.env['sale.order.line']
        discount_lines = defaultdict(lambda: self.env['sale.order.line'])
        order_lines = self.order_line - self._get_no_effect_on_threshold_lines()
        remaining_amount_per_line = defaultdict(int)
        for line in order_lines:
            if not line.product_uom_qty or not line.price_total:
                continue
            remaining_amount_per_line[line] = line.price_total
            domain = reward._get_discount_product_domain()
            #PATCH start
            if not line.reward_id and line.product_id.filtered_domain(domain) and reward._get_discount_sale_line_domain(line):
                lines_to_discount |= line
            #PATCH end
            elif line.reward_id.reward_type == 'discount':
                discount_lines[line.reward_identifier_code] |= line
        #PATCH start        
        if len(lines_to_discount) == 0:
            raise UserError(_('No line in this sale order satisfies the "Discount Sale Line Domain" in discount reward'))
        #PATCH end

        order_lines -= self.order_line.filtered("reward_id")
        cheapest_line = False
        for lines in discount_lines.values():
            line_reward = lines.reward_id
            discounted_lines = order_lines
            if line_reward.discount_applicability == 'cheapest':
                cheapest_line = cheapest_line or self._cheapest_line()
                discounted_lines = cheapest_line
            elif line_reward.discount_applicability == 'specific':
                discounted_lines = self._get_specific_discountable_lines(line_reward)
            if not discounted_lines:
                continue
            common_lines = discounted_lines & lines_to_discount
            if line_reward.discount_mode == 'percent':
                for line in discounted_lines:
                    if line_reward.discount_applicability == 'cheapest':
                        remaining_amount_per_line[line] *= (1 - line_reward.discount / 100 / line.product_uom_qty)
                    else:
                        remaining_amount_per_line[line] *= (1 - line_reward.discount / 100)
            else:
                non_common_lines = discounted_lines - lines_to_discount
                # Fixed prices are per tax
                discounted_amounts = {line.tax_id.filtered(lambda t: t.amount_type != 'fixed'): abs(line.price_total) for line in lines}
                for line in itertools.chain(non_common_lines, common_lines):
                    # For gift card and eWallet programs we have no tax but we can consume the amount completely
                    if lines.reward_id.program_id.is_payment_program:
                        discounted_amount = discounted_amounts[lines.tax_id.filtered(lambda t: t.amount_type != 'fixed')]
                    else:
                        discounted_amount = discounted_amounts[line.tax_id.filtered(lambda t: t.amount_type != 'fixed')]
                    if discounted_amount == 0:
                        continue
                    remaining = remaining_amount_per_line[line]
                    consumed = min(remaining, discounted_amount)
                    if lines.reward_id.program_id.is_payment_program:
                        discounted_amounts[lines.tax_id.filtered(lambda t: t.amount_type != 'fixed')] -= consumed
                    else:
                        discounted_amounts[line.tax_id.filtered(lambda t: t.amount_type != 'fixed')] -= consumed
                    remaining_amount_per_line[line] -= consumed

        discountable = 0
        discountable_per_tax = defaultdict(int)
        #PATCH start
        line_discount_dict = defaultdict(int)
        #PATCH ends

        for line in lines_to_discount:
            discountable += remaining_amount_per_line[line]
            line_discountable = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
            # line_discountable is the same as in a 'order' discount
            #  but first multiplied by a factor for the taxes to apply
            #  and then multiplied by another factor coming from the discountable
            discountable_per_tax_value = line_discountable *\
                (remaining_amount_per_line[line] / line.price_total)
            taxes = line.tax_id.filtered(lambda t: t.amount_type != 'fixed')
            discountable_per_tax[taxes] += discountable_per_tax_value
            #PATCH start
            line_discount_dict[line] =  discountable_per_tax_value
            #PATCH end
        #PATCHED returning line_discount_dict
        return discountable, discountable_per_tax, line_discount_dict
    
    #OVERRIDE: to obtain which line should the discount be applied to and specific the amount
    def _discountable_order(self, reward):
        """
        Returns the discountable and discountable_per_tax for a discount that applies to the whole order
        """
        self.ensure_one()
        assert reward.discount_applicability == 'order'

        discountable = 0
        discountable_per_tax = defaultdict(int)
        #PATCH start
        line_discount_dict = defaultdict(int)
        #PATCH end
        
        lines = self.order_line if reward.program_id.is_payment_program else (self.order_line - self._get_no_effect_on_threshold_lines())
        #PATCH start
        lines = reward._get_discount_sale_line_domain(lines)
        #PATCH end
        if len(lines) == 0:
            raise UserError(_('No line in this sale order satisfies the "Discount Sale Line Domain" in discount reward'))
        for line in lines:
            # Ignore lines from this reward
            if not line.product_uom_qty or not line.price_unit:
                continue
            tax_data = line._convert_to_tax_base_line_dict()
            # To compute the discountable amount we get the fixed tax amount and
            # subtract it from the order total. This way fixed taxes will not be discounted
            tax_data['taxes'] = tax_data['taxes'].filtered(lambda t: t.amount_type == 'fixed')
            tax_results = self.env['account.tax']._compute_taxes([tax_data])
            totals = list(tax_results['totals'].values())[0]
            discountable += line.price_total - totals['amount_tax']
            #PATCH start: line_discount_dict to store which discount applies to which line
            line_discount_dict[line] = line.price_total - totals['amount_tax']
            #PATCH end
            taxes = line.tax_id.filtered(lambda t: t.amount_type != 'fixed')
            discountable_per_tax[taxes] += totals['amount_untaxed']
        #PATCHED returning line_discount_dict
        return discountable, discountable_per_tax, line_discount_dict
    
    #OVERRIDE: Obtain which line should the discount be applied to and apply reward sale order line domain
    def _discountable_cheapest(self, reward):
        cheapest_line = self._cheapest_line()
        cheapest_line = reward._get_discount_sale_line_domain(cheapest_line)
        if len(cheapest_line) == 0:
            raise UserError(_('No line in this sale order satisfies the "Discount Sale Line Domain" in discount reward'))
        discountable, discountable_per_tax = super()._discountable_cheapest(reward)
        line_discount_dict = defaultdict(int)
        discountable = cheapest_line.price_unit * (1 - (cheapest_line.discount or 0) / 100)
        line_discount_dict[cheapest_line] = discountable
        #PATCHED returning line_discount_dict
        return discountable, discountable_per_tax, line_discount_dict
    
    def _write_order_line_discount(self, line_discount_dict, discount_factor, reward):
        self.ensure_one()
        for line in line_discount_dict:
            if line.promotion_ids == None and line.amount_discount != 0:
                line.amount_discount = 0
            if reward.program_id not in line.promotion_ids:
                line.discount += discount_factor * 100
            line.promotion_ids |= reward.program_id
    

    #OVERRIDE to write discounts in order lines and change the discount line qty to cero
    def _get_reward_values_discount(self, reward, coupon, **kwargs):
        self.ensure_one()
        assert reward.reward_type == 'discount'

        discountable = 0
        #PATCHED start
        discountable_per_tax = defaultdict(int)
        #PATCHED end
        reward_applies_on = reward.discount_applicability
        sequence = max(self.order_line.filtered(lambda x: not x.is_reward_line).mapped('sequence'), default=10) + 1
        if reward_applies_on == 'order':
            #PATCHED returning line_discount_dict
            discountable, discountable_per_tax, line_discount_dict = self._discountable_order(reward)
        elif reward_applies_on == 'specific':
            #PATCHED returning line_discount_dict
            discountable, discountable_per_tax, line_discount_dict = self._discountable_specific(reward)
        elif reward_applies_on == 'cheapest':
            #PATCHED returning line_discount_dict
            discountable, discountable_per_tax, line_discount_dict = self._discountable_cheapest(reward)
        if not discountable:
            if not reward.program_id.is_payment_program and any(line.reward_id.program_id.is_payment_program for line in self.order_line):
                return [{
                    'name': _("TEMPORARY DISCOUNT LINE"),
                    'product_id': reward.discount_line_product_id.id,
                    'price_unit': 0,
                    'product_uom_qty': 0,
                    'product_uom': reward.discount_line_product_id.uom_id.id,
                    'reward_id': reward.id,
                    'coupon_id': coupon.id,
                    'points_cost': 0,
                    'reward_identifier_code': _generate_random_reward_code(),
                    'sequence': sequence,
                    'tax_id': [(Command.CLEAR, 0, 0)]
                }]
            raise UserError(_('There is nothing to discount'))
        max_discount = reward.currency_id._convert(reward.discount_max_amount, self.currency_id, self.company_id, fields.Date.today()) or float('inf')
        # discount should never surpass the order's current total amount
        max_discount = min(self.amount_total, max_discount)
        if reward.discount_mode == 'per_point':
            points = self._get_real_points_for_coupon(coupon)
            if not reward.program_id.is_payment_program:
                # Rewards cannot be partially offered to customers
                points = points // reward.required_points * reward.required_points
            max_discount = min(max_discount,
                reward.currency_id._convert(reward.discount * points,
                    self.currency_id, self.company_id, fields.Date.today()))
        elif reward.discount_mode == 'per_order':
            max_discount = min(max_discount,
                reward.currency_id._convert(reward.discount, self.currency_id, self.company_id, fields.Date.today()))
        elif reward.discount_mode == 'percent':
            max_discount = min(max_discount, discountable * (reward.discount / 100))
        # Discount per taxes
        reward_code = _generate_random_reward_code()
        point_cost = reward.required_points if not reward.clear_wallet else self._get_real_points_for_coupon(coupon)
        if reward.discount_mode == 'per_point' and not reward.clear_wallet:
            # Calculate the actual point cost if the cost is per point
            converted_discount = self.currency_id._convert(min(max_discount, discountable), reward.currency_id, self.company_id, fields.Date.today())
            point_cost = converted_discount / reward.discount
        # Gift cards and eWallets are considered gift cards and should not have any taxes
        if reward.program_id.is_payment_program:
            return [{
                'name': reward.description,
                'product_id': reward.discount_line_product_id.id,
                'price_unit': -min(max_discount, discountable),
                'product_uom_qty': 1.0,
                'product_uom': reward.discount_line_product_id.uom_id.id,
                'reward_id': reward.id,
                'coupon_id': coupon.id,
                'points_cost': point_cost,
                'reward_identifier_code': reward_code,
                'sequence': sequence,
                'tax_id': [(Command.CLEAR, 0, 0)],
            }]
        discount_factor = min(1, (max_discount / discountable)) if discountable else 1
        mapped_taxes = {tax: self.fiscal_position_id.map_tax(tax) for tax in discountable_per_tax}
        reward_dict = {tax: {
            'name': _(
                'Discount: %(desc)s%(tax_str)s',
                desc=reward.description,
                tax_str=len(discountable_per_tax) and any(t.name for t in mapped_taxes[tax]) and _(' - On product with the following taxes: %(taxes)s', taxes=", ".join(mapped_taxes[tax].mapped('name'))) or '',
            ),
            'product_id': reward.discount_line_product_id.id,
            'price_unit': -(price * discount_factor),
            'product_uom_qty': 1.0,
            'product_uom': reward.discount_line_product_id.uom_id.id,
            'reward_id': reward.id,
            'coupon_id': coupon.id,
            'points_cost': 0,
            'reward_identifier_code': reward_code,
            'sequence': sequence,
            'tax_id': [(Command.CLEAR, 0, 0)] + [(Command.LINK, tax.id, False) for tax in mapped_taxes[tax]]
        } for tax, price in discountable_per_tax.items() if price}
        #Write line_discount_dict here to sale.order.line. This means that the best discount was the percentage
        #PATCH BEGINS
        if line_discount_dict:
            self._write_order_line_discount(line_discount_dict, discount_factor, reward)
        #PATCH ENDS
        # We only assign the point cost to one line to avoid counting the cost multiple times
        if reward_dict:
            reward_dict[next(iter(reward_dict))]['points_cost'] = point_cost
        # Returning .values() directly does not return a subscribable list
        
        #ADDED: change quantity of discount line to 0 so there is no suibstraction
        if reward.program_id.line_discount:
            for key, reward_data in reward_dict.items():
                reward_data['product_uom_qty'] = 0.0
        
        return list(reward_dict.values())
