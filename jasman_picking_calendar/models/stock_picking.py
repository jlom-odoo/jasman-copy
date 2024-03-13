from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', domain=[('tag_ids.is_internal', '=', 'True')])

    @api.constrains('vehicle_id', 'batch_id')
    def _check_same_vehicle_id(self):
        for picking in self:
            if picking.batch_id and picking.vehicle_id:
                if picking.vehicle_id != picking.batch_id.vehicle_id or len(picking.batch_id.mapped('picking_ids.vehicle_id')) > 1:
                    raise ValidationError(_('All pickings from a batch must have the same vehicle.'))
