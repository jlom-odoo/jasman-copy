from odoo.addons.stock_picking_batch.tests.test_batch_picking import TestBatchPicking
from odoo.fields import Command
from odoo.exceptions import ValidationError


class TestBatchPickingVehicles(TestBatchPicking):

    def test_batch_with_vehicle(self):
        batch = self.env['stock.picking.batch'].create({
            'name': 'Batch',
            'company_id': self.env.company.id,
        })
        vehicle_brand = self.env['fleet.vehicle.model.brand'].create({
            'name': 'Brand'
        })
        vehicle_model = self.env['fleet.vehicle.model'].create({
            'name': 'Model',
            'brand_id': vehicle_brand.id,
            'vehicle_type': 'car',
        })
        vehicle_1 = self.env['fleet.vehicle'].create({
            'name': 'Vehicle 1',
            'model_id': vehicle_model.id,
            'odometer_unit': 'kilometers',
            'contract_state': 'open',
        })
        vehicle_2 = self.env['fleet.vehicle'].create({
            'name': 'Vehicle 2',
            'model_id': vehicle_model.id,
            'odometer_unit': 'kilometers',
            'contract_state': 'open',
        })
        self.picking_client_1.write({
            'vehicle_id': vehicle_1.id,
            'batch_id': False,
        })
        self.picking_client_2.write({
            'vehicle_id': vehicle_2.id,
            'batch_id': False
        })
        batch.write({
            'picking_ids': [Command.link(self.picking_client_1.id)]
        })
        self.assertEqual(batch.vehicle_id, self.picking_client_1.vehicle_id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            batch.write({
                'picking_ids': [Command.link(self.picking_client_2.id)]
            })
