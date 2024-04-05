from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_doc_authorization = fields.Boolean(string='Include Authorization', tracking=True)
    has_doc_survey = fields.Boolean(string='Include Survey', tracking=True)
    has_doc_identification = fields.Boolean(string="Include Identification", tracking=True)
    has_doc_circulation_card = fields.Boolean(string='Include Circulation Card', tracking=True)
    has_doc_picture_evidence = fields.Boolean(string='Include Photo Evidence', tracking=True)
    has_doc_signed_invoice = fields.Boolean(string='Include Signed Invoice', tracking=True)
