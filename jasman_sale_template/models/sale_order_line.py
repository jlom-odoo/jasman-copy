from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_order_template_id = fields.Many2one("sale.order.template", string="Sale Order Template")
