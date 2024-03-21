# -*- coding: utf-8 -*-

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import tagged, TransactionCase, Form
from odoo.tools import mute_logger

from time import sleep

from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon

@tagged('post_install', '-at_install')
class TestSaleLoyaltyDiscountRelation(TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.largeCabinet = cls.env['product.product'].create({
            'name': 'Large Cabinet',
            'list_price': 320.0,
            'taxes_id': False,
        })
        cls.base_order = cls.empty_order
        cls.base_order.write({'order_line': [
            (0, False, {
                'product_id': cls.largeCabinet.id,
                'name': cls.largeCabinet.name,
                'product_uom_qty': 1.0,
                'discount': 0.0
            }),
        ]})
        cls.base_discount_program_specific_product = cls.env['loyalty.program'].create({
            'name': '10 percent on orders including large cabinet',
            'trigger': 'auto',
            'program_type': 'promotion',
            'applies_on': 'current',
            'rule_ids': [(0, 0, {
                'product_ids': cls.largeCabinet,
                'reward_point_mode': 'order',
                'minimum_qty': 0,
                'reward_point_amount': 1.0
            })],
            'reward_ids': [(0, 0, {
                'reward_type': 'discount',
                'discount_mode': 'percent',
                'discount': 10,
                'discount_applicability': 'specific',
                'required_points': 1,
                'discount_product_ids': cls.largeCabinet
            })],
        })
        
    def test_order_line_loyalty_discount_relation(self):    
        self.base_order._update_programs_and_rewards() 
        claimable_rewards = self.base_order._get_claimable_rewards()
        try:
            status = False
            if len(claimable_rewards) == 1:
                coupon = next(iter(claimable_rewards))
                if len(claimable_rewards[coupon]) == 1:
                    for reward in claimable_rewards[coupon]:
                        if reward.program_id == self.base_discount_program_specific_product:
                            status = self.base_order._apply_program_reward(reward, coupon)
                            if 'error' in status:
                                raise ValidationError(status['error'])
        except Exception as e:
            self.fail(f"An exception occurred while applying loyalty program rewards: {e}") 
            
        for line in self.base_order.order_line:
            if not line.is_reward_line:
                self.assertAlmostEqual(line.discount, self.base_discount_program_specific_product.reward_ids[0].discount)
            
