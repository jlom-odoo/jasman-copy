from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'


    is_vehicle_required = fields.Boolean(string='Vehicle Required')
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle')
    vehicle_odometer = fields.Float(string='Vehicle Odometer')
    
    @api.onchange('is_vehicle_required')
    def onchange_is_vehicle_required(self):
        msg = _('The vehicle required field was changed')
        for move in self:
            move_id = move._origin
            if move_id:
                if not move.is_vehicle_required:
                    vehicle_required_lines = move.invoice_line_ids.filtered(lambda l: l.product_id.is_sale_mandatory_vehicle)
                    if vehicle_required_lines:
                        raise UserError(_('The vehicle required field cannot be changed because the following products are only for sales with vehicle required: %s',\
                            ', '.join(vehicle_required_lines.mapped('product_id.name'))))
                move_id.message_post(body=msg)

