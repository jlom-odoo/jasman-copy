from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_reference = fields.Char(string='Payment Reference')
