from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    amount_discount = fields.Float()
    reduced_price = fields.Float()
    promotion_ids = fields.Many2many(
        string="Promotions",
        comodel_name='loyalty.program',
        readonly=True)
    discount = fields.Float(readonly=True, inverse='_inverse_compute_discount')   
                    
    @api.onchange('amount_discount')
    def _update_discount_from_amount_discount(self):
        for line in self:
            if line.product_id:
                price = line._get_pricelist_price_before_discount()
                line.discount = (line.amount_discount / price) * 100
                line.reduced_price = price * (1 - (line.discount/100))
                    
    def _inverse_compute_discount(self):
        for line in self:
            if line.product_id:
                price = line._get_pricelist_price_before_discount()
                line.amount_discount = price * (line.discount/100)
                line.reduced_price = price * (1 - (line.discount/100))
                
    def remove_discounts(self):
        for line in self:
            if line.is_reward_line:
                line.unlink()
            else:
                line.discount = 0
                line.amount_discount = 0
                line.reduced_price = 0
                line.promotion_ids = [(5, 0, 0)] 
