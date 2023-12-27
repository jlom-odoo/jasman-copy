from odoo.addons.product.tests.common import ProductCommon
from odoo.exceptions import ValidationError


class TestParentCategories(ProductCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_template = cls.env['product.template'].create({
            'name': 'Test Product'
        })
        cls.mayor_group = cls.env['product.category'].create({
            'name': 'Mayor Group',
            'parent_id': cls.product_category.id,
        })
        cls.minor_group = cls.env['product.category'].create({
            'name': 'Minor Group',
            'parent_id': cls.mayor_group.id,
        })


    def test_mayor_group_and_line_assignment(self):
        product = self.product_template
        product.write({'categ_id': self.product_category.id})
        self.assertFalse(product.line_id)
        self.assertFalse(product.mayor_group_id)
        self.assertEqual(product.categ_id, self.product_category)
        product.write({'categ_id': self.mayor_group.id})
        self.assertFalse(product.line_id)
        self.assertEqual(product.mayor_group_id, self.product_category)
        self.assertEqual(product.categ_id, self.mayor_group)
        product.write({'categ_id': self.minor_group.id})
        self.assertEqual(product.line_id, self.product_category)
        self.assertEqual(product.mayor_group_id, self.mayor_group)
        self.assertEqual(product.categ_id, self.minor_group)
