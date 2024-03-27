from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    
    use_partner_credit_limit = fields.Boolean(related='partner_id.use_partner_credit_limit')
