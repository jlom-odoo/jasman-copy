from odoo import api, fields, models, _
from odoo.fields import Command
from odoo.exceptions import ValidationError


class Task(models.Model):
    _inherit = "project.task"

    inspection_line_ids = fields.One2many(comodel_name="inspection.line", inverse_name="task_id", copy=True)
    is_template = fields.Boolean(copy=False)
    product_has_template = fields.Boolean(related="sale_line_id.product_template_id.is_inspection_task")

    def add_to_order(self):
        self.ensure_one()
        if self.inspection_line_ids.filtered(lambda inspection: inspection.urgency == 'none'):
            raise ValidationError(_("You need to evaluate all inspections before adding products."))
        products_in_order = self.mapped('sale_line_id.order_id.sale_order_option_ids.product_id')
        priority_inspections = self.inspection_line_ids.\
                filtered(lambda inspection: inspection.urgency in ['yellow', 'red'])
        products_in_templates = priority_inspections.mapped(
            'quotation_template_id.sale_order_template_option_ids.product_id'
            )
        optional_products_to_add = products_in_templates - products_in_order
        if not optional_products_to_add:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "info",
                    "title": _("No new products were added"),
                    "message": _("Order already contains the products from the inspetions."),
                    "next": {"type": "ir.actions.act_window_close"},
                }
            }
        lines_to_add = []
        for inspection in priority_inspections:
            lines_in_inspection = inspection.quotation_template_id.sale_order_template_option_ids\
                        .filtered(lambda line: line.product_id.id in optional_products_to_add.ids)
            lines_to_add += [(line, inspection.urgency) for line in lines_in_inspection]    
        order_option_data = []
        order_option_data = [
            Command.create(line[0].with_context(urgency=line[1])._prepare_option_line_values())
            for line in lines_to_add
        ]
        self.sale_line_id.order_id.write({
            'sale_order_option_ids': order_option_data
        })
        return {
            'name': _("New Quotation"),
            'type': "ir.actions.act_window",
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_line_id.order_id.id,
        }
