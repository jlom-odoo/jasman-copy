from odoo import fields, models

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    min_margin = fields.Float()
