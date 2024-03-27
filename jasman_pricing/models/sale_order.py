from odoo import fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_order_values(self):
        return self.order_line.filtered(lambda x: x.price_unit < x.min_price and not x.is_liberated)

    def action_confirm(self):
        forbbiden_values = self.check_order_values()
        if forbbiden_values:
            raise ValidationError(_("This sale cannot be confirmed as is, please change the discounts or request a price liberation. Some products in the order, doesn't meet the requirements:  %s ", (forbbiden_values.product_template_id.mapped('name'))))
        return super().action_confirm()
