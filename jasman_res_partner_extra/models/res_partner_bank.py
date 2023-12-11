from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_partner_code = fields.Char(string='Customer ID')
