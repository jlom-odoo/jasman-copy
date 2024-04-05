from odoo import api, fields, models


class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    urgency = fields.Selection([('none', 'None'), ('green', 'Green'), ('yellow', 'Yellow'), ('red', 'Red')])
    is_additional = fields.Boolean()
    is_present = fields.Boolean(readonly=False)

    def button_add_to_order(self):
        self.with_context(from_backend=True).add_option_to_order()
    
    def _get_values_to_add_to_order(self):
        values = super()._get_values_to_add_to_order()
        if self.env.context.get('from_backend'):
            values['is_additional'] = self.is_additional
        return values
