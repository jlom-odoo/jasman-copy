from odoo import fields, models


class MxEdiFigure(models.Model):
    _inherit = "l10n_mx_edi.figure"

    name = fields.Char(related="operator_id.name")
