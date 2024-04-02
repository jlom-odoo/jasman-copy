from odoo import Command
from odoo.addons.sale_project.tests.test_sale_project import TestSaleProject
from odoo.tests.common import tagged

@tagged('post_install', '-at_install')
class TestInspections(TestSaleProject):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.quotation_template1 = cls.env['sale.order.template'].create({
            'name': 'A quotation template 1',
            'sale_order_template_option_ids': [
                Command.create({
                    'product_id': cls.product_order_service1.id,
                }),
            ],
        })
        cls.quotation_template2 = cls.env['sale.order.template'].create({
            'name': 'A quotation template 2',
            'sale_order_template_option_ids': [
                Command.create({
                    'product_id': cls.product_order_service3.id,
                }),
            ],
        })
        cls.quotation_template3 = cls.env['sale.order.template'].create({
            'name': 'A quotation template 3',
            'sale_order_template_option_ids': [
                Command.create({
                    'product_id': cls.product_order_service4.id,
                }),
            ],
        })
        cls.inspection1 = cls.env['inspection.line'].create({
            'name': 'Inspection 1',
            'quotation_template_id': cls.quotation_template1.id,
            'urgency': 'red',
        })
        cls.inspection2 = cls.env['inspection.line'].create({
            'name': 'Inspection 2',
            'quotation_template_id': cls.quotation_template2.id,
            'urgency': 'yellow',
        })
        cls.inspection3 = cls.env['inspection.line'].create({
            'name': 'Inspection 3',
            'quotation_template_id': cls.quotation_template3.id,
            'urgency': 'green',
        })
        cls.template_task = cls.env['project.task'].create({
            'name': 'Test Template Task',
            'project_id': cls.project_template.id,
            'inspection_line_ids': [
                Command.set([
                    cls.inspection1.id,
                    cls.inspection2.id,
                    cls.inspection3.id,
                ])
            ]
        })
        cls.product_order_service2.write({
            'is_inspection_task': True,
            'template_task_id': cls.template_task.id,
            'service_tracking': 'task_global_project',
        })
        cls.sales_team_1 = cls.env['crm.team'].create({
            'name': 'Test Sales Team',
            'sequence': 5,
            'company_id': False,
        })
        cls.crm_stage = cls.env['crm.stage'].create({
            'name': 'Stage',
            'team_id': cls.sales_team_1.id,
            'is_inspection_stage': True,
        })

    def test_inspection_flow(self):
        SaleOrder = self.env['sale.order'].with_context(tracking_disable=True)
        SaleOrderLine = self.env['sale.order.line'].with_context(tracking_disable=True)

        sale_order = SaleOrder.create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'team_id': self.sales_team_1.id,
        })

        sale_order.write({
            'order_line': [Command.create({
                'product_id': self.product_order_service2.id,
            })]
        })
        sale_order.action_confirm()
        task = sale_order.tasks_ids[0]

        self.assertEqual(task.mapped('inspection_line_ids.name'), self.template_task.mapped('inspection_line_ids.name'))
        self.assertEqual(task.mapped('inspection_line_ids.urgency'), self.template_task.mapped('inspection_line_ids.urgency'))
        task.add_to_order()

        priority_inspections = self.inspection1 + self.inspection2
        self.assertEqual(sale_order.mapped('sale_order_option_ids.product_id'),
                          priority_inspections.mapped('quotation_template_id.sale_order_template_option_ids.product_id'))
        sale_order.add_extra_quote()
        new_crm_lead = self.env['crm.lead'].search([('name', '=', sale_order.name + ' inspection opportunity')])
        
        self.assertEqual(new_crm_lead.order_ids[0].mapped('order_line.product_id'),
                         sale_order.mapped('sale_order_option_ids.product_id'))
