from odoo import fields, models


class SignTemplate(models.Model):
    _inherit = 'sign.template'

    sale_order_id = fields.Many2one(comodel_name='sale.order')
    
class SignItemType(models.Model):
    _inherit = 'sign.item.type'

    sale_auto_field = fields.Char(string="Auto-fill Sale Field")
