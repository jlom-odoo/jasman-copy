from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vehicle_ref = fields.Char(string='Vehicle Reference')
