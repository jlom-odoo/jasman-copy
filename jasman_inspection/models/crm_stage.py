from odoo import api, fields, models


class Stage(models.Model):
    _inherit = "crm.stage"

    is_inspection_stage = fields.Boolean()
