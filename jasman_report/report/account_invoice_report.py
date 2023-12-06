from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_categ_id = fields.Many2one(comodel_name="product.category", string="Minor Group")
    mayor_group_id = fields.Many2one(comodel_name="product.category", string="Mayor Group", readonly=True)
    line_id = fields.Many2one(comodel_name="product.category", string="Line", readonly=True)

    def _select(self):
        res = super()._select()
        res = ''.join((res, """,
            template.mayor_group_id AS mayor_group_id, 
            template.line_id AS line_id"""))
        return res
