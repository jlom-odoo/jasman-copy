from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    engine_number = fields.Char(string='Engine Number')

    def _get_odometer(self):
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for vehicle in self:
            vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', vehicle.id)],limit=1,order="create_date desc",)
            if vehicle_odometer:
                vehicle.odometer = vehicle_odometer.value
            else:
                vehicle.odometer = 0
