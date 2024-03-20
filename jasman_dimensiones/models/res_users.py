from odoo import models, fields


class ResUser(models.Model):
    _inherit = 'res.users'

    ceco_analytic_account_id = fields.Many2one(string='CECO', comodel_name='account.analytic.account')
    zona_analytic_account_id = fields.Many2one(string='Zona', comodel_name='account.analytic.account')
    subzona_analytic_account_id = fields.Many2one(string='Sub-Zona', comodel_name='account.analytic.account')
