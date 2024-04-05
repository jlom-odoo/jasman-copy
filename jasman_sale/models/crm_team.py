from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    is_vehicle_required = fields.Boolean(string='Vehicle Required')
    property_account_position_id = fields.Many2one(comodel_name='account.fiscal.position', string='Fiscal Position')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Account Journal')
    insurance_company = fields.Char(string='Insurance Company')
    policy_number = fields.Integer(string='Policy Number')
