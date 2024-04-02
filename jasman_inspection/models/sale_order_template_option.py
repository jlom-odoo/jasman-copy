from odoo import api, fields, models


class SaleOrderTemplateOptiion(models.Model):
    _inherit = "sale.order.template.option"

    def _prepare_option_line_values(self):
        values = super()._prepare_option_line_values()
        urgency = self.env.context.get('urgency')
        if urgency:
            values['urgency'] = urgency
            values['is_additional'] = True
        return values
