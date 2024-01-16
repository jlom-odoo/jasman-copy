from odoo.addons.sale.tests.common import SaleCommon
from odoo.tests import tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestSaleReportGroups(SaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usd_cmp = cls.env['res.company'].create({
            'name': 'USD Company', 'currency_id': cls.env.ref('base.USD').id,
        })
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
        cls.product_a = cls.env['product.product'].create({
            'name': 'product_a',
            'categ_id': cls.minor_group_a.id,
        })
        cls.product_b = cls.env['product.product'].create({
            'name': 'product_b',
            'categ_id': cls.minor_group_b.id,
        })
        cls.product_c = cls.env['product.product'].create({
            'name': 'product_c',
            'categ_id': cls.minor_group_c.id,
        })
        cls.orders = cls.env['sale.order'].create([
            {
                'partner_id': cls.partner.id,
                'company_id': cls.usd_cmp.id,
                'order_line': [
                    (0, None, {
                        'product_id': cls.product_a.id,
                        'product_uom_qty': 3,
                        'price_unit': 750,
                    }),
                ]
            },
            {
                'partner_id': cls.partner.id,
                'company_id': cls.usd_cmp.id,
                'order_line': [
                    (0, None, {
                        'product_id': cls.product_b.id,
                        'product_uom_qty': 3,
                        'price_unit': 750,
                    }),
                ]
            },
            {
                'partner_id': cls.partner.id,
                'company_id': cls.usd_cmp.id,
                'order_line': [
                    (0, None, {
                        'product_id': cls.product_c.id,
                        'product_uom_qty': 3,
                        'price_unit': 750,
                    }),
                ]
            },
        ])
    
    def test_account_invoice_report_category_groups(self):
        minor_group_report = self.env['sale.report'].read_group([('company_id','=', self.usd_cmp.id)], fields=['price_total'], groupby=['categ_id'])
        self.assertEqual(len(minor_group_report), 3)                                          
        mayor_group_report = self.env['sale.report'].read_group([('company_id','=', self.usd_cmp.id)], fields=['price_total'], groupby=['mayor_group_id'])
        self.assertEqual(len(mayor_group_report), 2)  
        line_report = self.env['sale.report'].read_group([('company_id','=', self.usd_cmp.id)], fields=['price_total'], groupby=['line_id'])
        self.assertEqual(len(line_report), 1)
