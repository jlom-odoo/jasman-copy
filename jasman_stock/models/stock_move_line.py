from datetime import timedelta

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    dot_id = fields.Char(related='lot_id.dot_id')
    lot_creation_date = fields.Date(related='lot_id.lot_creation_date')

    @api.depends('product_id', 'picking_type_use_create_lots', 'lot_id.expiration_date')
    def _compute_expiration_date(self):
    super()._compute_expiration_date()
        for move_line in self.filtered(lambda _move_line: _move_line.lot_id.expiration_date):
                move_line.expiration_date = move_line.lot_id.expiration_date
        super()._compute_expiration_date()
        for move_line in self:
            if move_line.lot_id.expiration_date:
                move_line.expiration_date = move_line.lot_id.expiration_date
