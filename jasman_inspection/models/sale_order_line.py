from odoo import api, fields, models
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_additional = fields.Boolean()

    def _timesheet_create_task_prepare_values(self, project):
        values = super()._timesheet_create_task_prepare_values(project)
        if self.product_template_id.template_task_id:
            inspection_ids = [inspection.copy().id 
                              for inspection in self.product_template_id.template_task_id.inspection_line_ids]
            values['inspection_line_ids'] = [Command.set(inspection_ids)]
        return values
