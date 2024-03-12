from odoo import fields, models


class FleetVehicleTag(models.Model):
    _inherit = 'fleet.vehicle.tag'

    internal = fields.Boolean(string="Internal")
