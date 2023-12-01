from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_categ_id = fields.Many2one(string="Minor Group", comodel_name="product.category")
    mayor_group_id = fields.Many2one(string="Mayor Group", comodel_name="product.category", readonly=True)
    line_id = fields.Many2one(string="Line", comodel_name="product.category", readonly=True)

    def _select(self):
        res = super()._select()
        res += """,
            template.mayor_group_id AS mayor_group_id, 
            template.line_id AS line_id"""
        return res
