from datetime import datetime, timedelta

from odoo import api, fields, models

class StockMoveLot(models.Model):
    _inherit = 'stock.lot'

    dot_id = fields.Char()
    lot_creation_date = fields.Date(compute='_compute_lot_creation_date')
    name = fields.Char(compute='_compute_name', store=True)

    @api.depends('product_id','lot_creation_date')
    def _compute_expiration_date(self):
      super()._compute_expiration_date()
      for lot in self.filtered(lambda _lot: _lot.product_id.use_expiration_date and _lot.lot_creation_date):
              duration = lot.product_id.product_tmpl_id.expiration_time
              lot.expiration_date = lot.lot_creation_date + timedelta(days=duration)
        super()._compute_expiration_date()
        for lot in self:
            if lot.product_id.use_expiration_date and lot.lot_creation_date:
                duration = lot.product_id.product_tmpl_id.expiration_time
                lot.expiration_date = lot.lot_creation_date + timedelta(days=duration)

    @api.depends('dot_id', 'product_id.default_code')
    def _compute_name(self):
        for lot in self:
            lot.name = f'{lot.dot_id or "0000"}-{lot.product_id.default_code}'

    @api.depends('dot_id')
    def _compute_lot_creation_date(self):
        for lot in self:
            lot.lot_creation_date = datetime.strptime(f"{lot.dot_id}-1", "%W%y-%w") if lot.dot_id else None
