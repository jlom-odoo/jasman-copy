from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle', compute='_compute_vehicle_id')

    @api.depends('picking_ids')
    def _compute_vehicle_id(self):
        for batch in self:
            batch.vehicle_id = batch.mapped('picking_ids.vehicle_id')[:1]
