import base64
import zipfile
from io import BytesIO
from PyPDF2 import PdfFileMerger,PdfFileWriter,PdfFileReader
from PIL import Image

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    contract_count = fields.Integer(compute='_compute_contract_count', string='Amount of Contracts')
    contract_ids = fields.One2many(
        comodel_name='sign.template',
        inverse_name='sale_order_id',
        string='Contracts')
    combined_documentation = fields.Binary(compute='_compute_combined_documentation', store=True)
    file_authorization = fields.Binary(string='Authorization')
    file_authorization_filename = fields.Char()
    file_survey = fields.Binary(string='Survey')
    file_survey_filename = fields.Char()
    file_identification = fields.Binary(string='Identification')
    file_identification_filename = fields.Char()
    file_circulation_card = fields.Binary(string='Circulation Card')
    file_circulation_card_filename = fields.Char()
    file_picture_evidence = fields.Binary(string='Photo Evidence')
    file_picture_evidence_filename = fields.Char()
    file_signed_invoice = fields.Binary(string='Signed Invoice')
    file_signed_invoice_filename = fields.Char()
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        compute="_compute_fiscal_position_id",
        store=True,
        readonly=False)
    has_doc_authorization = fields.Boolean(compute='_compute_partner_documentation', string='Include Authorization')
    has_doc_survey = fields.Boolean(compute='_compute_partner_documentation', string='Include Survey')
    has_doc_identification = fields.Boolean(compute='_compute_partner_documentation', string="Include Identification")
    has_doc_circulation_card = fields.Boolean(compute='_compute_partner_documentation', string='Include Circulation Card')
    has_doc_picture_evidence = fields.Boolean(compute='_compute_partner_documentation', string='Include Photo Evidence')
    has_doc_signed_invoice = fields.Boolean(compute='_compute_partner_documentation', string='Include Signed Invoice')
    is_vehicle_required = fields.Boolean(
        compute='_compute_is_vehicle_required',
        string='Vehicle Required',
        store=True,
        readonly=False)
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        compute='_compute_journal_id',
        string='Invoicing Journal',
        store=True,
        readonly=False
    )
    salesperson_department_id = fields.Many2one(
        related='user_id.department_id',
        comodel_name='hr.department',
        string='Salesperson Department'
    )
    sign_template_id = fields.Many2one(
        comodel_name='sign.template',
        compute='_compute_sign_template_id',
        string='Sign Template to Copy When Creating Contract'
    )
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Fleet Vehicle')
    vehicle_odometer = fields.Float(string='Vehicle Odometer')
    vehicle_color = fields.Char(compute='_compute_vehicle_fields', readonly=False, store=True, string='Vehicle Color')
    vehicle_model_year = fields.Char(compute='_compute_vehicle_fields', readonly=False, store=True, string='Vehicle Model Year')
    vehicle_vin_sn = fields.Char(compute='_compute_vehicle_fields', readonly=False, store=True, string='Vehicle VIN')
    vehicle_engine_number = fields.Char(compute='_compute_vehicle_fields', readonly=False, store=True, string='Vehicle Engine Number')
    vehicle_front = fields.Binary(string='Vehicle Front Photo')
    vehicle_back = fields.Binary(string='Vehicle Back Photo')
    vehicle_right = fields.Binary(string='Vehicle Right Photo')
    vehicle_left = fields.Binary(string='Vehicle Left Photo')
    vehicle_trunk = fields.Binary(string='Vehicle Trunk Photo')
    vehicle_dashboard = fields.Binary(string='Vehicle Dashboard Photo')
    
    @api.constrains('vehicle_vin_sn')
    def _check_vin_length(self):
        for order in self:
            if order.vehicle_vin_sn and len(order.vehicle_vin_sn) != 17:
                raise UserError(_('The vehicle VIN must be exactly 17 characters long'))
    
    @api.depends('team_id')
    def _compute_is_vehicle_required(self):
        for order in self:
            if order.team_id:
                order.is_vehicle_required = order.team_id.is_vehicle_required
            else:
                order.is_vehicle_required = False
                
    @api.depends('team_id','partner_id')
    def _compute_fiscal_position_id(self):
        for order in self:
            if order.partner_id.property_account_position_id:
                order.fiscal_position_id = order.partner_id.property_account_position_id
            elif order.team_id.property_account_position_id:
                order.fiscal_position_id = order.team_id.property_account_position_id
            else:
                order.fiscal_position_id = order.fiscal_position_id
                
    @api.depends('team_id')
    def _compute_journal_id(self):
        for order in self:
            if order.team_id.journal_id:
                order.journal_id = order.team_id.journal_id
            else:
                order.journal_id = order.journal_id
                
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for order in self:
            order.contract_count = len(order.contract_ids)
            
    @api.depends()
    def _compute_sign_template_id(self):
        for order in self:
            template_id = self.env['ir.config_parameter'].sudo().get_param('sale.sign_template_id')
            order.sign_template_id = self.env['sign.template'].search([('id','=',template_id)])
            
    @api.depends('file_authorization','has_doc_authorization','file_survey','has_doc_survey','file_identification','has_doc_identification','file_circulation_card','has_doc_circulation_card','file_picture_evidence','has_doc_picture_evidence','file_signed_invoice','has_doc_signed_invoice')
    def _compute_combined_documentation(self):
        for order in self:
            merger = PdfFileMerger()
            document_files = order.prepare_document_files()
            if not document_files or not order.check_if_documents_set(document_files):
                order.combined_documentation = False
                continue
            sale_order_report = self.env.ref('sale.action_report_saleorder')
            pdf_content = self.env['ir.actions.report'].sudo()._render_qweb_pdf(sale_order_report, self.id)
            data_record = base64.b64encode(pdf_content[0])
            pdfs = document_files['pdf_files']
            pdfs.append({'file':data_record,'active':True,'order':2})
            images = document_files['image_files']
            
            for image_data in images:
                output = base64.b64decode(image_data['file'])
                image = Image.open(BytesIO(output))
                pdf_width = 595
                pdf_height = 842
                image.thumbnail((pdf_width,pdf_height))
                new_image = Image.new('RGB',
                 (pdf_width, pdf_height),
                 (255, 255, 255))
                new_image.paste(image, ((pdf_width - image.width)//2,(pdf_height - image.height)//2))
                new_image.save('converted_image.pdf')
                with open('converted_image.pdf', 'rb') as file:
                    pdfs.append({'file':base64.encodebytes(file.read()),'order':image_data['order']})
                    
            for pdf in sorted(pdfs, key=lambda x: x['order']):
                b64_data = BytesIO(base64.decodebytes(pdf['file']))
                merger.append(b64_data,import_bookmarks=False)
                
            output_name = order.name + _('_documentation.pdf')
            merger.write(output_name)
            merger.close()
            with open(output_name, 'rb') as file:
                pdf_datas = base64.encodebytes(file.read())
            if len(pdf_datas)/1e+6 > 2:
                pdf_datas = self.compress_pdf(output_name)
            order.combined_documentation = pdf_datas if pdf_datas else False
            
    @api.depends('partner_id')
    def _compute_partner_documentation(self):
        self.has_doc_authorization = False
        self.has_doc_survey = False
        self.has_doc_identification = False
        self.has_doc_circulation_card = False
        self.has_doc_picture_evidence = False
        self.has_doc_signed_invoice = False
        for order in self:
            if order.partner_id.has_doc_authorization or order.partner_id.parent_id.has_doc_authorization:
                order.has_doc_authorization = True
            if order.partner_id.has_doc_survey or order.partner_id.parent_id.has_doc_survey:
                order.has_doc_survey = True
            if order.partner_id.has_doc_identification or order.partner_id.parent_id.has_doc_identification:
                order.has_doc_identification = True
            if order.partner_id.has_doc_circulation_card or order.partner_id.parent_id.has_doc_circulation_card:
                order.has_doc_circulation_card = True
            if order.partner_id.has_doc_picture_evidence or order.partner_id.parent_id.has_doc_picture_evidence:
                order.has_doc_picture_evidence = True
            if order.partner_id.has_doc_signed_invoice or order.partner_id.parent_id.has_doc_signed_invoice:
                order.has_doc_signed_invoice = True
                
    @api.depends('vehicle_id')
    def _compute_vehicle_fields(self):
        for order in self:
            if not order.vehicle_color:
                order.vehicle_color = order.vehicle_id.color
            if not order.vehicle_model_year:
                order.vehicle_model_year = order.vehicle_id.model_year
            if not order.vehicle_vin_sn:
                order.vehicle_vin_sn = order.vehicle_id.vin_sn
            if not order.vehicle_engine_number:
                order.vehicle_engine_number = order.vehicle_id.engine_number
            
    @api.onchange('is_vehicle_required')
    def onchange_is_vehicle_required(self):
        for order in self:
            msg = _('The vehicle required field was changed')
            order_id = order._origin
            if order_id:
                if not order.is_vehicle_required:
                    vehicle_required_lines = order.order_line.filtered(lambda l: l.product_template_id.is_sale_mandatory_vehicle)
                    if vehicle_required_lines:
                        raise UserError(_('The vehicle required field cannot be changed because the following products are only for sales with vehicle required: %s',\
                            ', '.join(vehicle_required_lines.mapped('product_template_id.name'))))
                order_id.message_post(body=msg)
            
    def write(self, vals):
        file_tracked_fields = [
            ('file_authorization',_('Authorization File')),
            ('file_survey',_('Survey File')),
            ('file_identification',_('Identification File')),
            ('file_circulation_card',_('Circulation Card File')),
            ('file_picture_evidence',_('Picture Evidence File')),
            ('file_signed_invoice',_('Signed Invoice File'))]
        for field,name in file_tracked_fields:
            if field in vals:
                msg = (_('The %s was changed',name))
                self.message_post(body=msg)

        return super().write(vals)
    
    def _create_invoices(self, grouped=False, final=False, date=None):
        for order in self:
            documentation = [
                {'active':order.has_doc_authorization,'file':order.file_authorization,'name':(_('Authorization'))},
                {'active':order.has_doc_circulation_card,'file':order.file_circulation_card,'name':(_('Circulation Card'))},
                {'active':order.has_doc_identification,'file':order.file_identification,'name':(_('Identification'))},
                {'active':order.has_doc_picture_evidence,'file':order.file_picture_evidence,'name':(_('Picture Evidence'))},
                {'active':order.has_doc_survey,'file':order.file_survey,'name':(_('Survey'))}]
            error_message = ''
            for document in documentation:
                if document['active'] and not document['file']:
                    error_message += document['name'] + ', '
            if error_message:
                raise UserError(_('The following documents are missing: %s',error_message[:-2]))
            res = super()._create_invoices(grouped,final,date)
            for move in res:
                if order.is_vehicle_required:
                    move.write({
                        'is_vehicle_required':move.line_ids.sale_line_ids.order_id.is_vehicle_required,
                        'vehicle_id':move.line_ids.sale_line_ids.order_id.vehicle_id,
                        'vehicle_odometer':move.line_ids.sale_line_ids.order_id.vehicle_odometer
                    })
            return res
                
    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            order.vehicle_id.write({'odometer': order.vehicle_odometer})
        return res
                
    def _can_be_confirmed(self):
        self.ensure_one()
        if self.is_vehicle_required and (not self.vehicle_id or (self.vehicle_odometer == 0.0) or not self.vehicle_color or not self.vehicle_model_year or not self.vehicle_vin_sn or not self.vehicle_engine_number):
            raise UserError(_('This sale requires vehicle information to be filled in before confirming'))
        elif self.is_vehicle_required and (not self.vehicle_front or not self.vehicle_back or not self.vehicle_left or not self.vehicle_right or not self.vehicle_trunk or not self.vehicle_dashboard):
            raise UserError(_('This sale requires vehicle photos to be attached before confirming'))
        for line in self.order_line:
            if line.product_type == 'service' and not line.technician_id:
                raise UserError(_('This sale includes a service product which requires a technician to be assigned'))
        return super()._can_be_confirmed()
    
    def action_create_contract(self):
        if not self.sign_template_id:
            raise UserError(_('A contract template must be set in the app settings before creating any contracts'))
        self.sign_template_id.copy({'sale_order_id':self.id})
        
    
    def action_view_contract(self):
        self.ensure_one()

        return {
            'res_model': 'sign.template',
            'type': 'ir.actions.act_window',
            'name': _("Contracts for %s", self.name),
            'domain': [('sale_order_id', '=', self.id)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': {},
        }
        
    def action_download_client_documents(self):            
        variables = []
        filenames = []
        for order in self:
            if order.combined_documentation:
                if len(base64.b64decode(order.combined_documentation))/1e+6 >= 2.1:
                    raise UserError(_('The client documentation for sale order: %s, is greater than 2 mb',order.name))
                buffer = BytesIO()
                variables.append(base64.b64decode(order.combined_documentation))
                filenames.append(order.name + _('_documentation.pdf'))
        if len(variables) > 1:
            with zipfile.ZipFile(buffer, mode='w') as zipf:
                for variable, filename in zip(variables, filenames):
                    zipf.writestr(filename, variable)
            compressed_data = buffer.getvalue()
            download_name = _('compressed_documentation.zip')
            download_datas = base64.b64encode(compressed_data)
        elif len(variables) == 1:
            download_name = filenames[0]
            download_datas = base64.b64encode(variables[0])
        else:
            raise UserError(_('Some of the required documents are missing'))
        
        attachment_id = self.env['ir.attachment'].create(
            {'name': download_name, 'datas': download_datas})
        
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        
        
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new"
        }
            
    def prepare_document_files(self):
        file_list = [
            {
                'file':self.file_signed_invoice,
                'active':self.has_doc_signed_invoice,
                'filename':self.file_signed_invoice_filename,
                'order': 1
            },
            {
                'file':self.file_authorization,
                'active':self.has_doc_authorization,
                'filename':self.file_authorization_filename,
                'order': 3
            },
            {
                'file':self.file_survey,
                'active':self.has_doc_survey,
                'filename':self.file_survey_filename,
                'order': 4
            },
            {
                'file':self.file_identification,
                'active':self.has_doc_identification,
                'filename':self.file_identification_filename,
                'order': 5
            },
            {
                'file':self.file_circulation_card,
                'active':self.has_doc_circulation_card,
                'filename':self.file_circulation_card_filename,
                'order': 6
            },
            {
                'file':self.file_picture_evidence,
                'active':self.has_doc_picture_evidence,
                'filename':self.file_picture_evidence_filename,
                'order': 7
            }
        ]
        
        pdf_files = []
        image_files = []
        
        for file in file_list:
            if file['active']:
                if file.get('filename') and file['filename'].split('.')[-1] == 'pdf':
                    pdf_files.append({'file':file['file'],'order':file['order'],'active':file['active']})
                else:
                    image_files.append({'file':file['file'],'order':file['order'],'active':file['active']})
                
        if len(pdf_files) == 0 and len(image_files) == 0:
            return False
        return {'pdf_files':pdf_files,'image_files':image_files}
    
    def compress_pdf(self,output_name):
        reader = PdfFileReader(output_name)
        writer = PdfFileWriter()
        for page in reader.pages:
            page.compressContentStreams()
            writer.addPage(page)
        writer.addMetadata(reader.documentInfo)
        with open(output_name, 'wb') as file:
            writer.write(file)
        with open(output_name,'rb') as file:
            return base64.encodebytes(file.read())

    def check_if_documents_set(self,document_files):
        pdf_files = document_files['pdf_files']
        image_files = document_files['image_files']
        if len(pdf_files) == 1 and len(image_files) == 0:
            return False
        for file_type in document_files.keys():
            for file in document_files[file_type]:
                if(file['active'] == True and not file['file']):
                    return False
        return True
