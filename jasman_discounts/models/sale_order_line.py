from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    amount_discount = fields.Float()
    promotion_ids = fields.Many2many(
        string="Promotions",
        comodel_name='loyalty.program',
        readonly=True)
    discount = fields.Float(digits=(7, 4), readonly=True, inverse='_inverse_discount')   
    delete_discounts = fields.Boolean(default=False)
    
    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'amount_discount', 'price_unit')
    def _compute_discount(self):
        super()._compute_discount()
        for line in self:
            if line.price_unit != 0 and not line.is_reward_line:
                line.discount = line.amount_discount / line.price_unit * 100
            elif line.price_unit == 0:
                line.discount = 0

                    
    @api.onchange('amount_discount')
    def _update_discount_from_amount_discount(self):
        for line in self:
            if line.product_id:
                line.discount = (line.amount_discount / line.price_unit) * 100
                    
    def _inverse_discount(self):
        for line in self:
            line.amount_discount = line.price_unit * (line.discount/100)
                
    def _remove_discounts(self):
        for line in self:
            if line.is_reward_line:
                line.with_context(unlink_rewards=True).unlink()
            else:
                line.discount = 0
                line.amount_discount = 0
                line.promotion_ids = [(5, 0, 0)] 
                
    def unlink(self):
        #The customer is trying to unlink lines manually, block deletion.
        unlink_rewards = self._context.get('unlink_rewards')
        #If there is no discount lines to unlink or lines that have a related discount: lines can be unlinked
        none_reward_line = self.filtered(lambda line: line.reward_id or line.promotion_ids)
        if not (unlink_rewards or none_reward_line):
            raise UserError(_("Discount lines cannot or lines that are linked to a promotion cannot be deleted manually, to delete please click the 'Delete discounts' button"))
        #The customer pressed the remove discount button, all discount lines can be unlinked
        return super().unlink()
    
    def _reset_loyalty(self, complete=False):
        res = super()._reset_loyalty()
        if complete and self.reward_id.discount_mode == 'percent':
            order_line = self.env['sale.order.line'].search([
                ('promotion_ids.name', '=', self.reward_id.program_id.name)
            ])
            for line in order_line:
                line.discount -= self.reward_id.discount
                line.promotion_ids = [(3, self.reward_id.program_id)]
        return res
                
