# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.sale.tests.common import SaleCommon


@tagged('post_install', '-at_install')
class TestSaleOrderAmountDiscount(SaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'detailed_type': 'consu',
            'list_price': 200.0,
        })
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                #Base case
                Command.create({
                    'product_id': cls.product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 200.0,
                    'discount': 0.0
                }),
            ]
        })
    
    def calculate_discount(self, amount_discount, initial_price):    
        expected_discount = (amount_discount / initial_price) * 100
        return expected_discount
        
    def test_amount_discount_change(self):
        for line in self.sale_order.order_line:
            line.amount_discount = 100.0
            expected_discount = self.calculate_discount(line.amount_discount,line.price_unit)
            self.assertAlmostEqual(line.discount, expected_discount)
