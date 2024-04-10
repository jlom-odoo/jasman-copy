import uuid
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    country_code = fields.Char(related="company_id.account_fiscal_country_id.code")
    l10n_mx_edi_document_ids = fields.One2many(
        comodel_name="l10n_mx_edi.document",
        inverse_name="batch_id",
        copy=False,
        readonly=True,
    )
    l10n_mx_edi_transport_type = fields.Selection(
        selection=[
            ("00", "No Federal Highways"),
            ("01", "Federal Transport"),
        ],
        string="Transport Type",
        copy=False
    )
    l10n_mx_edi_vehicle_id = fields.Many2one("l10n_mx_edi.vehicle",
        string="Vehicle Setup",
        ondelete="restrict",
        copy=False
    )
    l10n_mx_edi_distance = fields.Integer(
        "Distance to Destination (KM)",
        compute="_compute_l10n_mx_edi_distance",
    )
    l10n_mx_edi_cfdi_origin = fields.Char(
        string="CFDI Origin",
        copy=False,
        help="Specify the existing Fiscal Folios to replace. Prepend with '04|'",
    )
    l10n_mx_edi_is_cfdi_needed = fields.Boolean(
        compute="_compute_l10n_mx_edi_is_cfdi_needed",
        store=True,
    )
    l10n_mx_edi_cfdi_state = fields.Selection(
        string="CFDI status",
        selection=[
            ("sent", "Signed"),
            ("cancel", "Cancelled"),
        ],
        store=True,
        copy=False,
        tracking=True,
        compute="_compute_l10n_mx_edi_cfdi_state_and_attachment",
    )
    l10n_mx_edi_cfdi_sat_state = fields.Selection(
        string="SAT status",
        selection=[
            ("valid", "Validated"),
            ("not_found", "Not Found"),
            ("not_defined", "Not Defined"),
            ("cancelled", "Cancelled"),
            ("error", "Error"),
        ],
        store=True,
        copy=False,
        tracking=True,
        compute="_compute_l10n_mx_edi_cfdi_state_and_attachment",
    )
    l10n_mx_edi_cfdi_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        store=True,
        copy=False,
        compute="_compute_l10n_mx_edi_cfdi_state_and_attachment",
    )
    l10n_mx_edi_update_sat_needed = fields.Boolean(compute="_compute_l10n_mx_edi_update_sat_needed")
    l10n_mx_edi_idccp = fields.Char(
        string="IdCCP",
        help="Additional UUID for the Delivery Guide.",
        compute="_compute_l10n_mx_edi_idccp",
    )
    l10n_mx_edi_external_trade = fields.Char(compute="_compute_batch_contact")
    l10n_mx_edi_cfdi_uuid = fields.Char(
        string="Fiscal Folio",
        compute="_compute_l10n_mx_edi_cfdi_uuid",
        copy=False,
        store=True,
        help="Folio in electronic invoice, is returned by SAT when send to stamp.",
    )
    is_delivery_guide_possible = fields.Boolean(compute="_compute_is_delivery_guide_possible")
    figure_ids = fields.One2many(related="l10n_mx_edi_vehicle_id.figure_ids")
    figure_id = fields.Many2one("l10n_mx_edi.figure", 
        string="Vehicle Operator",
        domain="""[("id", "in", figure_ids), ("type", "=", "01")]""")
    effective_date = fields.Datetime("Date of Batch", copy=False, readonly=True, help="Date at which the batch has been processed or cancelled.")
    batch_contact = fields.Many2one("res.partner", compute="_compute_batch_contact")

    def action_done(self):
        res = super().action_done()
        self.effective_date = datetime.today()
        return res
    
    @api.depends("company_id", "state", "picking_type_code")
    def _compute_l10n_mx_edi_is_cfdi_needed(self):
        for batch in self:
            batch.l10n_mx_edi_is_cfdi_needed = \
                batch.country_code == "MX" \
                and batch.state == "done" \
                and batch.picking_type_code == "outgoing"
            
    @api.depends("l10n_mx_edi_document_ids.state", "l10n_mx_edi_document_ids.sat_state")
    def _compute_l10n_mx_edi_cfdi_state_and_attachment(self):
        for batch in self:
            batch.l10n_mx_edi_cfdi_sat_state = None
            batch.l10n_mx_edi_cfdi_state = None
            batch.l10n_mx_edi_cfdi_attachment_id = None
            for doc in batch.l10n_mx_edi_document_ids.sorted():
                if doc.state == "batch_sent":
                    batch.l10n_mx_edi_cfdi_sat_state = doc.sat_state
                    batch.l10n_mx_edi_cfdi_state = "sent"
                    batch.l10n_mx_edi_cfdi_attachment_id = doc.attachment_id
                    break
                elif doc.state == "batch_cancel":
                    batch.l10n_mx_edi_cfdi_sat_state = doc.sat_state
                    batch.l10n_mx_edi_cfdi_state = "cancel"
                    batch.l10n_mx_edi_cfdi_attachment_id = doc.attachment_id
                    break
    
    @api.depends("l10n_mx_edi_document_ids.state")
    def _compute_l10n_mx_edi_update_sat_needed(self):
        for batch in self:
            batch.l10n_mx_edi_update_sat_needed = bool(
                batch.l10n_mx_edi_document_ids.filtered_domain(
                    expression.OR(self.env["l10n_mx_edi.document"]._get_update_sat_status_domains())
                )
            )

    @api.depends("l10n_mx_edi_cfdi_attachment_id")
    def _compute_l10n_mx_edi_cfdi_uuid(self):
        for batch in self:
            if batch.l10n_mx_edi_cfdi_attachment_id:
                cfdi_infos = self.env["l10n_mx_edi.document"]._decode_cfdi_attachment(batch.l10n_mx_edi_cfdi_attachment_id.raw)
                batch.l10n_mx_edi_cfdi_uuid = cfdi_infos.get("uuid")
            else:
                batch.l10n_mx_edi_cfdi_uuid = None
    
    @api.depends("l10n_mx_edi_is_cfdi_needed")
    def _compute_l10n_mx_edi_idccp(self):
        for batch in self:
            if batch.l10n_mx_edi_is_cfdi_needed and not batch.l10n_mx_edi_idccp:
                # The IdCCP must be a 36 characters long RFC 4122 identifier starting with "CCC".
                batch.l10n_mx_edi_idccp = f"CCC{str(uuid.uuid4())[3:]}"
            else:
                batch.l10n_mx_edi_idccp = False

    @api.depends("picking_ids.l10n_mx_edi_distance")
    def _compute_l10n_mx_edi_distance(self):
        for batch in self:
            batch.l10n_mx_edi_distance = sum(batch.picking_ids.mapped("l10n_mx_edi_distance"))
    
    @api.depends("picking_ids.partner_id")
    def _compute_batch_contact(self):
        for batch in self:
            if len(batch.picking_ids.partner_id) == 1:
                batch.batch_contact = batch.picking_ids.partner_id
            elif len(batch.picking_ids.partner_id.parent_id) == 1 \
                 and all([p.parent_id for p in batch.picking_ids.partner_id]):
                batch.batch_contact = batch.picking_ids.partner_id.parent_id
            else:
                batch.batch_contact = False
            batch.l10n_mx_edi_external_trade = batch.batch_contact.country_code != "MX"
    
    @api.depends("picking_ids")
    def _compute_is_delivery_guide_possible(self):
        for batch in self:
            batch.is_delivery_guide_possible = batch.state == "done" \
                and self.picking_type_code == "outgoing" \
                and self.batch_contact
    
    @api.model
    def _l10n_mx_edi_add_domicilio_cfdi_values(self, cfdi_values, partner):
        cfdi_values["domicilio"] = {
            "calle": partner.street,
            "codigo_postal": partner.zip,
            "estado": partner.state_id.code,
            "pais": partner.country_id.l10n_mx_edi_code,
            "municipio": partner.city_id.l10n_mx_edi_code or partner.city,
        }
    
    def _l10n_mx_edi_add_batch_cfdi_values(self, cfdi_values):
        self.ensure_one()
        company = cfdi_values["company"]

        if self.picking_type_id.warehouse_id.partner_id:
            cfdi_values["issued_address"] = self.picking_type_id.warehouse_id.partner_id
        issued_address = cfdi_values["issued_address"]

        self.env["l10n_mx_edi.document"]._add_base_cfdi_values(cfdi_values)
        self.env["l10n_mx_edi.document"]._add_currency_cfdi_values(cfdi_values, company.currency_id)
        self.env["l10n_mx_edi.document"]._add_document_name_cfdi_values(cfdi_values, self.name)
        self.env["l10n_mx_edi.document"]._add_document_origin_cfdi_values(cfdi_values, self.l10n_mx_edi_cfdi_origin)
        self.env["l10n_mx_edi.document"]._add_customer_cfdi_values(cfdi_values, self.batch_contact)

        mx_tz = issued_address._l10n_mx_edi_get_cfdi_timezone()
        date_fmt = "%Y-%m-%dT%H:%M:%S"

        cfdi_values.update({
            "record": self,
            "cfdi_date": self.effective_date.astimezone(mx_tz).strftime(date_fmt),
            "scheduled_date": self.scheduled_date.astimezone(mx_tz).strftime(date_fmt),
            "lugar_expedicion": issued_address.zip,
            "moves": self.move_ids.filtered(lambda ml: ml.quantity > 0),
            "weight_uom": self.env["product.template"]._get_weight_uom_id_from_ir_config_parameter(),
        })

        cfdi_values["idccp"] = self.l10n_mx_edi_idccp

        if self.l10n_mx_edi_vehicle_id:
            cfdi_values["peso_bruto_vehicular"] = self.l10n_mx_edi_vehicle_id.gross_vehicle_weight
        else:
            cfdi_values["peso_bruto_vehicular"] = None

        warehouse_partner = self.picking_type_id.warehouse_id.partner_id
        warehouse_location = self.picking_type_id.warehouse_id.lot_stock_id \
                             or self.picking_type_id.default_location_src_id
        receptor = cfdi_values["receptor"]
        emisor = cfdi_values["emisor"]

        cfdi_values["origen"] = {
            "id_ubicacion": f"OR{str(warehouse_location.id).rjust(6, '0')}",
            "fecha_hora_salida_llegada": cfdi_values["cfdi_date"],
            "num_reg_id_trib": None,
            "residencia_fiscal": None,
        }
        cfdi_values["destino"] = [{
            "id_ubicacion": f"DE{str(picking.location_dest_id.id).rjust(6, '0')}",
            "fecha_hora_salida_llegada": picking.scheduled_date.astimezone(mx_tz).strftime(date_fmt),
            "num_reg_id_trib": None,
            "residencia_fiscal": None,
            "distancia_recorrida": picking.l10n_mx_edi_distance,
        } for picking in self.picking_ids]

        if warehouse_partner.country_id.l10n_mx_edi_code != "MEX":
            cfdi_values["origen"]["rfc_remitente_destinatario"] = "XEXX010101000"
            cfdi_values["origen"]["num_reg_id_trib"] = emisor["supplier"].vat
            cfdi_values["origen"]["residencia_fiscal"] = warehouse_partner.country_id.l10n_mx_edi_code
        else:
            cfdi_values["origen"]["rfc_remitente_destinatario"] = emisor["rfc"]
        self._l10n_mx_edi_add_domicilio_cfdi_values(cfdi_values["origen"], warehouse_partner)
        
        for picking in cfdi_values["destino"]:
            picking["rfc_remitente_destinatario"] = receptor["rfc"]
            if self.l10n_mx_edi_external_trade:
                picking["num_reg_id_trib"] = receptor["customer"].vat
                picking["residencia_fiscal"] = receptor["customer"].country_id.l10n_mx_edi_code
            self._l10n_mx_edi_add_domicilio_cfdi_values(picking, receptor["customer"])
    
    def _l10n_mx_edi_cfdi_document_sent_failed(self, error, cfdi_filename=None, cfdi_str=None):
        self.ensure_one()

        document_values = {
            "batch_id": self.id,
            "state": "batch_sent_failed",
            "sat_state": None,
            "message": error,
        }
        if cfdi_filename and cfdi_str:
            document_values["attachment_id"] = {
                "name": cfdi_filename,
                "raw": cfdi_str,
            }
        return self.env["l10n_mx_edi.document"]._create_update_batch_document(self, document_values)
    
    def _l10n_mx_edi_cfdi_document_sent(self, cfdi_filename, cfdi_str):
        self.ensure_one()

        document_values = {
            "batch_id": self.id,
            "state": "batch_sent",
            "sat_state": "not_defined",
            "message": None,
            "attachment_id": {
                "name": cfdi_filename,
                "raw": cfdi_str,
                "res_model": self._name,
                "res_id": self.id,
                "description": "CFDI",
            },
        }
        return self.env["l10n_mx_edi.document"]._create_update_batch_document(self, document_values)
    
    @api.model
    def _l10n_mx_edi_prepare_batch_cfdi_template(self):
        return "jasman_delivery_guide.cfdi_cartaporte_30"
    
    def l10n_mx_edi_action_send_batch_delivery_guide(self):
        self.ensure_one()
        if not self.is_delivery_guide_possible:
            raise UserError(_("Operation type must be 'Delivery' and "
                              "batch must be in stage 'Done' to "
                              "generate the Delivery Guide"))
        
        for picking in self.picking_ids:
            errors = picking._l10n_mx_edi_cfdi_check_external_trade_config() \
                   + picking._l10n_mx_edi_cfdi_check_picking_config()
            if errors:
                errors.insert(0, picking.name)
                self._l10n_mx_edi_cfdi_document_sent_failed("\n".join(errors))
                return
            
        self.env["l10n_mx_edi.document"]._with_locked_records(self)
        
        def on_populate(cfdi_values):
            self._l10n_mx_edi_add_batch_cfdi_values(cfdi_values)

        def on_failure(error, cfdi_filename=None, cfdi_str=None):
            self._l10n_mx_edi_cfdi_document_sent_failed(error, cfdi_filename=cfdi_filename, cfdi_str=cfdi_str)

        def on_success(_cfdi_values, cfdi_filename, cfdi_str, populate_return=None):
            document = self._l10n_mx_edi_cfdi_document_sent(cfdi_filename, cfdi_str)
            self.message_post(
                body=_("The CFDI document was successfully created and signed by the government."),
                attachment_ids=document.attachment_id.ids,
            )

        qweb_template = self._l10n_mx_edi_prepare_batch_cfdi_template()
        cfdi_filename = f"CFDI_DeliveryGuide_{self.name}.xml".replace("/", "")
        self.env["l10n_mx_edi.document"]._send_api(
            self.company_id,
            qweb_template,
            cfdi_filename,
            on_populate,
            on_failure,
            on_success,
        )

    def _l10n_mx_edi_cfdi_document_cancel_failed(self, error, cfdi, cancel_reason):
        self.ensure_one()

        document_values = {
            "batch_id": self.id,
            "state": "batch_cancel_failed",
            "sat_state": None,
            "message": error,
            "attachment_id": cfdi.attachment_id.id,
            "cancellation_reason": cancel_reason,
        }
        return self.env["l10n_mx_edi.document"]._create_update_batch_document(self, document_values)
    
    def _l10n_mx_edi_cfdi_document_cancel(self, cfdi, cancel_reason):
        self.ensure_one()

        document_values = {
            "batch_id": self.id,
            "state": "batch_cancel",
            "sat_state": "not_defined",
            "message": None,
            "attachment_id": cfdi.attachment_id.id,
            "cancellation_reason": cancel_reason,
        }
        return self.env["l10n_mx_edi.document"]._create_update_batch_document(self, document_values)
    
    def _l10n_mx_edi_cfdi_try_cancel(self, document):
        self.ensure_one()
        if self.l10n_mx_edi_cfdi_state != "sent":
            return

        self.env["l10n_mx_edi.document"]._with_locked_records(self)

        substitution_doc = document._get_substitution_document()
        cancel_uuid = substitution_doc.attachment_uuid
        cancel_reason = "01" if cancel_uuid else "02"

        def on_failure(error):
            self._l10n_mx_edi_cfdi_document_cancel_failed(error, document, cancel_reason)

        def on_success():
            self._l10n_mx_edi_cfdi_document_cancel(document, cancel_reason)
            self.l10n_mx_edi_cfdi_origin = f"04|{self.l10n_mx_edi_cfdi_uuid}"
            self.message_post(body=_("The CFDI document has been successfully cancelled."))

        document._cancel_api(self.company_id, cancel_reason, on_failure, on_success)
    
    def l10n_mx_edi_cfdi_try_cancel(self):
        self.ensure_one()
        source_document = self.l10n_mx_edi_document_ids.filtered(lambda x: x.state == "batch_sent")[:1]
        self._l10n_mx_edi_cfdi_try_cancel(source_document)

    def l10n_mx_edi_cfdi_try_sat(self):
        self.ensure_one()
        self.env["l10n_mx_edi.document"]._fetch_and_update_sat_status(extra_domain=[("batch_id", "=", self.id)])
