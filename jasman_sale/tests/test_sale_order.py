import base64
from PIL import Image
from reportlab.pdfgen import canvas

from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()
        cls.department_1 = cls.env['hr.department'].create({
            'name': 'Test Department'
        })
        cls.fiscal_position_1 = cls.env['account.fiscal.position'].create({
            'name': 'Test Fiscal Position'
        })
        cls.fiscal_position_2 = cls.env['account.fiscal.position'].create({
            'name': 'Different Test Fiscal Position'
        })
        cls.journal_1 = cls.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TESTCODE',
            'type': 'sale'
        })
        cls.customer_1 = cls.env['res.partner'].create({
            'name': 'Test Customer'
        })
        cls.customer_2 = cls.env['res.partner'].create({
            'name': 'Test Customer with Fiscal Position',
            'property_account_position_id': cls.fiscal_position_2.id
        })
        cls.salesperson_partner_1 = cls.env['res.partner'].create({
            'name': 'Test Salesperson'
        })
        cls.salesperson_user_1 = cls.env['res.users'].create({
            'name': 'Test Salesperson',
            'login': 'test_salesperson@example.com',
            'partner_id': cls.salesperson_partner_1.id
        })
        cls.technician_1 = cls.env['hr.employee'].create({
            'name': 'Test Salesperson',
            'department_id': cls.department_1.id
        })
        cls.sales_team_1 = cls.env['crm.team'].create({
            'name': 'Test Sales Team',
            'is_vehicle_required': True,
            'property_account_position_id': cls.fiscal_position_1.id,
            'journal_id': cls.journal_1.id
        })
        cls.sales_team_member_1 = cls.env['crm.team.member'].create({
            'crm_team_id': cls.sales_team_1.id,
            'user_id': cls.salesperson_user_1.id
        })
        cls.service_product_1 = cls.env['product.product'].create({
            'name': 'Test Service Product',
            'detailed_type': 'service',
        })
        cls.vehicle_not_required_product_1 = cls.env['product.product'].create({
            'name': 'Test No Vehicle Required Product',
            'detailed_type': 'consu',
            'is_sale_mandatory_vehicle': False
        })
        cls.fleet_vehicle_model_brand_1 = cls.env['fleet.vehicle.model.brand'].create({
            'name': 'Test Vehicle Brand'
        })
        cls.fleet_vehicle_model_1 = cls.env['fleet.vehicle.model'].create({
            'name': 'Test Fleet Vehicle',
            'brand_id': cls.fleet_vehicle_model_brand_1.id
        })
        cls.fleet_vehicle_1 = cls.env['fleet.vehicle'].create({
            'model_id': cls.fleet_vehicle_model_1.id,
            'odometer': 150,
            'color': 'Red',
            'model_year': '2024',
            'vin_sn': '12345678901234567',
            'engine_number': '001'
        })
        cls.blank_image = Image.new('RGB', (100, 100), color='white')
        cls.blank_image.save('blank_image.png')
        with open('blank_image.png', 'rb') as file:
            cls.encoded_blank_image = base64.encodebytes(file.read())
        c = canvas.Canvas("hello-world.pdf")
        c.save()
        with open('hello-world.pdf','rb') as file:
            cls.encoded_blank_pdf = base64.encodebytes(file.read())
        cls.attachment_1 = cls.env['ir.attachment'].create({
            'name': 'test_attachment.png',
            'datas': cls.encoded_blank_pdf
        })
        cls.sale_1 = cls.env['sale.order'].create({
            'team_id': cls.sales_team_1.id,
            'user_id': cls.salesperson_user_1.id,
            'is_vehicle_required': True,
            'partner_id': cls.customer_1.id,
            'vehicle_id': cls.fleet_vehicle_1.id
        })
        cls.sale_order_line_1 = cls.env['sale.order.line'].create({
            'order_id': cls.sale_1.id,
            'product_id': cls.service_product_1.id,
            'product_uom_qty': 1,
            'technician_id': cls.technician_1.id
        })
        cls.sale_2 = cls.env['sale.order'].create({
            'team_id': cls.sales_team_1.id,
            'user_id': cls.salesperson_user_1.id,
            'partner_id': cls.customer_2.id
        })
        cls.sign_template_1 = cls.env['sign.template'].create({
            'attachment_id': cls.attachment_1.id
        })

    def test_sale_order_purchase_cost(self):
        #Default Information from Sales Team
        #The fiscal position will prioritize the one set from the customer before the one set from the sales team 
        self.assertEqual(self.sale_1.fiscal_position_id.id,self.sales_team_1.property_account_position_id.id,'A sale created by a sales team with a fiscal position assigned should the same one')
        self.assertEqual(self.sale_2.fiscal_position_id.id,self.sale_2.partner_id.property_account_position_id.id,'A sale created by a sales team with a fiscal position assigned and one assigned for the customer should use the customer position') 
        self.assertEqual(self.sale_1.journal_id.id,self.sales_team_1.journal_id.id,'A sale created by a sales team with a journal assigned should the same one')
        
        
        #Vehicle Information and Images
        #Sale Orders can only be confirmed if the odometer is different from 0.0 and all of the vehicle images are attached
        self.sale_1.vehicle_odometer = 250
        self.sale_1.vehicle_front = self.encoded_blank_image
        self.sale_1.vehicle_back = self.encoded_blank_image
        self.sale_1.vehicle_left = self.encoded_blank_image
        self.sale_1.vehicle_right = self.encoded_blank_image
        self.sale_1.vehicle_trunk = self.encoded_blank_image
        self.sale_1.vehicle_dashboard = self.encoded_blank_image
        self.sale_1.action_confirm()
        self.assertEqual(self.sale_1.vehicle_odometer,self.fleet_vehicle_1.odometer,'After a sale is confirmed, the fleet vehicle odometer should be set to the sale vehicle_odometer')

        #Invoices created from a Sale
        #When an invoice is created from a sale, they should have the same vehicle_id and odometer as the sale
        self.sale_1._create_invoices()
        self.assertEqual(self.sale_1.invoice_ids[0].vehicle_id.id,self.sale_1.vehicle_id.id,'An invoice created from a sale with a vehicle should have the same vehicle_id')
        self.assertEqual(self.sale_1.invoice_ids[0].vehicle_odometer,self.sale_1.vehicle_odometer,'An invoice created from a sale with a vehicle should have the same vehicle_odometer')

        #Sales can have the vehicle required field changed
        #These types of sales can only include products that have the is_sale_mandatory_vehicle field set to False
        #They also don't need any vehicle information or pictures to confirm
        self.sale_2.is_vehicle_required = False
        self.env['sale.order.line'].create({
            'order_id': self.sale_2.id,
            'product_id': self.vehicle_not_required_product_1.id,
            'product_uom_qty': 2
        })
        self.sale_2.action_confirm()
        
        #Contracts created from a Sale
        #The default sign.template must first be assigned in the global sale settings
        #The button should create a new sign.template copied from the one from the settings and assign it to the contract_ids
        self.env['ir.config_parameter'].sudo().set_param('sale.sign_template_id', self.sign_template_1.id)
        self.sale_1.action_create_contract()
        if self.sale_1.contract_ids:
            has_contracts = True
        else:
            has_contracts = False
        self.assertEqual(has_contracts,True,'The action_create_contract function from sale should create and assign a new sign.template to the contract_ids')
