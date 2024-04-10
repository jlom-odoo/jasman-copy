from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    l10n_mx_edi_transport_type = fields.Selection(
        compute="_compute_delivery_guide_fields",
        store=True,
        readonly=False,
    )
    l10n_mx_edi_vehicle_id = fields.Many2one("l10n_mx_edi.vehicle",
        compute="_compute_delivery_guide_fields",
        store=True,
        readonly=False,
    )

    @api.depends("batch_id.l10n_mx_edi_transport_type",
                 "batch_id.l10n_mx_edi_vehicle_id")
    def _compute_delivery_guide_fields(self):
        for picking in self:
            picking.l10n_mx_edi_transport_type = picking.batch_id.l10n_mx_edi_transport_type
            picking.l10n_mx_edi_vehicle_id = picking.batch_id.l10n_mx_edi_vehicle_id

    def _l10n_mx_edi_cfdi_check_picking_config(self):
        # EXTENDS l10n_mx_edi_stock
        self.ensure_one()
        if not self.l10n_mx_edi_distance:
            self.l10n_mx_edi_distance = self.batch_id.l10n_mx_edi_distance
        return super()._l10n_mx_edi_cfdi_check_picking_config()
