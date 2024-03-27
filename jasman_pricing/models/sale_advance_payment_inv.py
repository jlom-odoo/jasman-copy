from odoo import models, _
from odoo.exceptions import ValidationError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        for order in sale_orders:
            forbbiden_values = order.check_order_values()
            if forbbiden_values:
                raise ValidationError(_("This sale cannot be confirmed as is, please change the discounts or request a price liberation. Some products in the order, doesn't meet the requirements:  %s ", (forbbiden_values.product_template_id.mapped('name'))))
        return super()._create_invoices(sale_orders)
