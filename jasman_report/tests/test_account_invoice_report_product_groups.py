from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestAccountInvoiceReportProductGroups(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line = cls.env['product.category'].create({
            'name': "Line"
        })
        cls.mayor_group_a = cls.env['product.category'].create({
            'name': 'Mayor Group A',
            'parent_id': cls.line.id,
        })
        cls.minor_group_a = cls.env['product.category'].create({
            'name': 'Minor Group A',
            'parent_id': cls.mayor_group_a.id,
        })
        cls.mayor_group_b = cls.env['product.category'].create({
            'name': 'Mayor Group B',
            'parent_id': cls.line.id,
        })
        cls.minor_group_b = cls.env['product.category'].create({
            'name': 'Minor Group B',
            'parent_id': cls.mayor_group_b.id,
        })
        cls.minor_group_c = cls.env['product.category'].create({
            'name': "Minor Group C",
            "parent_id": cls.mayor_group_b.id,
        })
        cls.product_c = cls.env['product.product'].create({
            'name': 'product_c',
            'categ_id': cls.minor_group_c.id,
        })
        cls.product_a.write({'categ_id': cls.minor_group_a.id})
        cls.product_b.write({'categ_id': cls.minor_group_b.id})
        cls.invoices = cls.env['account.move'].create([
            {
                'move_type': 'out_invoice',
                'partner_id': cls.partner_a.id,
                'invoice_date': fields.Date.from_string('2016-01-01'),
                'currency_id': cls.currency_data['currency'].id,
                'invoice_line_ids': [
                    (0, None, {
                        'product_id': cls.product_a.id,
                        'quantity': 3,
                        'price_unit': 750,
                    }),
                ]
            },
            {
                'move_type': 'out_invoice',
                'partner_id': cls.partner_a.id,
                'invoice_date': fields.Date.from_string('2016-01-01'),
                'currency_id': cls.currency_data['currency'].id,
                'invoice_line_ids': [
                    (0, None, {
                        'product_id': cls.product_b.id,
                        'quantity': 6,
                        'price_unit': 860,
                    }),
                ]
            },
            {
                'move_type': 'out_invoice',
                'partner_id': cls.partner_a.id,
                'invoice_date': fields.Date.from_string('2016-01-01'),
                'currency_id': cls.currency_data['currency'].id,
                'invoice_line_ids': [
                    (0, None, {
                        'product_id': cls.product_c.id,
                        'quantity': 6,
                        'price_unit': 860,
                    }),
                ]
            }
        ])
    
    def test_account_invoice_report_category_groups(self):
        minor_group_report = self.env['account.invoice.report'].read_group([('company_id', '=', self.company_data['company'].id)], fields=['price_total'], groupby=['product_categ_id'])
        self.assertEqual(len(minor_group_report), 3)                                          
        mayor_group_report = self.env['account.invoice.report'].read_group([('company_id', '=', self.company_data['company'].id)], fields=['price_total'], groupby=['mayor_group_id'])
        self.assertEqual(len(mayor_group_report), 2)  
        line_report = self.env['account.invoice.report'].read_group([('company_id', '=', self.company_data['company'].id)], fields=['price_total'], groupby=['line_id'])
        self.assertEqual(len(line_report), 1)
