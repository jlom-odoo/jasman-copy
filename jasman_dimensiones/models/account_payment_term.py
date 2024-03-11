from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    analytic_account_id = fields.Many2one(string='Payment Type D', comodel_name='account.analytic.account')
