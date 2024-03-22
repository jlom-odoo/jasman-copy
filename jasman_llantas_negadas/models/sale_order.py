from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    missing_tire_ids = fields.One2many(string="Missing Tires", comodel_name="missing.tire", inverse_name="order_id")
