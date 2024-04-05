from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    technician_id = fields.Many2one(comodel_name='hr.employee', string="Technician", readonly=True)


    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['technician_id'] = "l.technician_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            l.technician_id"""
        return res
