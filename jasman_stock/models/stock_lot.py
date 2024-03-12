from datetime import datetime

from odoo import api, fields, models

class StockMoveLot(models.Model):
    _inherit = 'stock.lot'

    dot_id = fields.Char()
    lot_creation_date = fields.Date(compute='_compute_lot_creation_date')
    name = fields.Char(compute='_compute_name')

    @api.depends('dot_id', 'product_id.default_code')
    def _compute_name(self):
        for lot in self:
            lot.name = f'{lot.dot_id or "0000"}-{lot.product_id.default_code}'

    @api.depends('dot_id')
    def _compute_lot_creation_date(self):
        for lot in self:
            lot.lot_creation_date = datetime.strptime(f"{lot.dot_id}-1", "%W%y-%w") if lot.dot_id else None
