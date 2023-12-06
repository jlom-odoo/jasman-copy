from odoo import models, fields


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    analytic_account_id = fields.Many2one(string='Channel', comodel_name='account.analytic.account')
