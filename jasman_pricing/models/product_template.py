from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_price_blocked = fields.Boolean()
