from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.product.tests.common import ProductAttributesCommon

class TestMultipleValuesAssignment(ProductAttributesCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_template = cls.env['product.template'].create({
            'name': 'Test Product Template'
        })

    def test_multiple_values_assignment(self):
        product = self.product_template
        with self.assertRaises(ValidationError):
            product.write({'attribute_line_ids': [
                Command.create({'attribute_id': self.size_attribute.id,
                                'value_ids': [Command.set([self.size_attribute_l.id, self.size_attribute_m.id])]}),
                Command.create({'attribute_id': self.color_attribute.id,
                                'value_ids': [Command.set([self.color_attribute_red.id, self.color_attribute_blue.id])]}),
            ]})
        product.write({'multiple_attribute_values': True,
            'attribute_line_ids': [
                Command.create({'attribute_id': self.size_attribute.id,
                                'value_ids': [Command.set([self.size_attribute_l.id, self.size_attribute_m.id])]}),
                Command.create({'attribute_id': self.color_attribute.id,
                                'value_ids': [Command.set([self.color_attribute_red.id, self.color_attribute_blue.id])]}),
            ]})
        for line in product.attribute_line_ids:
            self.assertTrue(line.value_count > 1)
