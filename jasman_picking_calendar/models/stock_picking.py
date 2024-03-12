from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle', domain=[('tag_ids.name', '=', 'Interno')])
