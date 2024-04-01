from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    amount_discount = fields.Float()
    promotion_ids = fields.Many2many(
        string="Promotions",
        comodel_name='loyalty.program',
        readonly=True)
    discount = fields.Float(readonly=True, inverse='_inverse_compute_discount')   
    delete_discounts = fields.Boolean(default=False)
                    
    @api.onchange('amount_discount')
    def _update_discount_from_amount_discount(self):
        for line in self:
            if line.product_id:
                line.discount = (line.amount_discount / line.price_unit) * 100
                    
    def _inverse_compute_discount(self):
        for line in self:
            if line.product_id:
                line.amount_discount = line.price_unit * (line.discount/100)
                
    def remove_discounts(self):
        for line in self:
            if line.is_reward_line:
                line.with_context(reward_line_can_be_unlinked=True).unlink()
            else:
                line.discount = 0
                line.amount_discount = 0
                line.promotion_ids = [(5, 0, 0)] 
                
    def unlink(self):
        #The customer is trying to unlink lines manually, block deletion.
        reward_line_can_be_unlinked = self._context.get('reward_line_can_be_unlinked', False)
        #If there is no discount lines to unlink or lines that have a related discount: lines can be unlinked
        none_reward_line = self.filtered(lambda line: line.reward_id or line.promotion_ids)
        if reward_line_can_be_unlinked == False and len(none_reward_line) != 0:
            raise UserError(_("Discount lines cannot or lines that are linked to a promotion cannot be deleted manually, to delete please click the 'Delete discounts' button"))
        #The customer pressed the remove discount button, all discount lines can be unlinked
        return super().unlink()
                
