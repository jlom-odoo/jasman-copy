from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    dot_id = fields.Char(related='lot_id.dot_id')
    lot_creation_date = fields.Date(related='lot_id.lot_creation_date')
