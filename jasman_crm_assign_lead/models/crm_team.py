from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    latitude = fields.Float("Latitude", digits=(10, 7))
    longitude = fields.Float("Longitude", digits=(10, 7))
