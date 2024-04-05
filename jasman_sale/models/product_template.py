from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_sale_mandatory_vehicle = fields.Boolean(string='Sale Mandatory Vehicle')
