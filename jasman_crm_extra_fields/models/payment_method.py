from odoo import models, fields


class PaymentMethod(models.Model):
    _inherit = 'l10n_mx_edi.payment.method'

    analytic_account_id = fields.Many2one(string='Payment Type D', comodel_name='account.analytic.account')
    