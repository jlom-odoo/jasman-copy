from odoo import fields, models


class FleetVehicleTag(models.Model):
    _inherit = 'fleet.vehicle.tag'

    is_internal = fields.Boolean()
