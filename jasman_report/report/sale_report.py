from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    categ_id = fields.Many2one(string="Minor Group", comodel_name="product.category")
    mayor_group_id = fields.Many2one(string="Mayor Group", comodel_name="product.category", readonly=True)
    line_id = fields.Many2one(string="Line", comodel_name="product.category", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["mayor_group_id"] = "t.mayor_group_id"
        res["line_id"] = "t.line_id"
        return res
    
    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            t.mayor_group_id,
            t.line_id"""
        return res
