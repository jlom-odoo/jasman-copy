from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sign_template_id = fields.Many2one(
        comodel_name='sign.template',
        config_parameter='sale.sign_template_id',
        string='Default Contract Template for Sales')
