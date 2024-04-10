from odoo import api, fields, models


class L10nMxEdiDocument(models.Model):
    _inherit = "l10n_mx_edi.document"

    batch_id = fields.Many2one(comodel_name="stock.picking.batch", auto_join=True)
    state = fields.Selection(
        selection_add=[
            ("batch_sent", "Batch Sent"),
            ("batch_sent_failed", "Batch Sent In Error"),
            ("batch_cancel", "Batch Cancel"),
            ("batch_cancel_failed", "Batch Cancelled In Error"),
        ],
        ondelete={
            "batch_sent": "cascade",
            "batch_sent_failed": "cascade",
            "batch_cancel": "cascade",
            "batch_cancel_failed": "cascade",
        },
    )

    def _get_cancel_button_map(self):
        results = super()._get_cancel_button_map()
        results['batch_sent'] = (
            'batch_cancel',
            None,
            lambda x: x.batch_id._l10n_mx_edi_cfdi_try_cancel(x),
        )
        return results
    
    def _get_retry_button_map(self):
        results = super()._get_retry_button_map()
        results["batch_sent_failed"] = (
            None,
            lambda x: x.batch_id.l10n_mx_edi_action_send_batch_delivery_guide(),
        )
        results["batch_cancel_failed"] = (
            None,
            lambda x: x._action_retry_batch_try_cancel(),
        )
        return results
    
    def _action_retry_batch_try_cancel(self):
        self.ensure_one()
        source_document = self._get_source_document_from_cancel("batch_sent")
        if source_document:
            self.batch_id._l10n_mx_edi_cfdi_try_cancel(source_document)
    
    @api.model
    def _create_update_batch_document(self, batch, document_values):
        if document_values["state"] in ("batch_sent", "batch_cancel"):
            accept_method_state = f"{document_values['state']}_failed"
        else:
            accept_method_state = document_values["state"]

        document = batch.l10n_mx_edi_document_ids._create_update_document(
            batch,
            document_values,
            lambda x: x.state == accept_method_state,
        )

        batch.l10n_mx_edi_document_ids \
            .filtered(lambda x: x != document and x.state in ["batch_sent_failed", "batch_cancel_failed"]) \
            .unlink()

        if document.state in ("batch_sent", "batch_cancel"):
            batch.l10n_mx_edi_document_ids \
                .filtered(lambda x: (
                    x != document
                    and x.sat_state not in ("valid", "cancelled", "skip")
                    and x.attachment_uuid == document.attachment_uuid
                )) \
                .write({"sat_state": "skip"})

        return document
    
    def _update_sat_state(self):
        # EXTENDS "l10n_mx_edi"
        sat_results = super()._update_sat_state()

        if sat_results.get("error") and self.batch_id:
            self.batch_id._message_log(body=sat_results["error"])

        return sat_results

    @api.model
    def _get_update_sat_status_domains(self):
        # EXTENDS "l10n_mx_edi"
        return super()._get_update_sat_status_domains() + [
            [
                ("state", "in", ("batch_sent", "batch_cancel")),
                ("sat_state", "not in", ("valid", "cancelled", "skip")),
            ],
        ]
