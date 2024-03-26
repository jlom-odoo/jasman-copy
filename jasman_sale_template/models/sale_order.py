from odoo import api, fields, models, Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_template_ids = fields.Many2many("sale.order.template", string="Sale Order Templates")

    @api.onchange("sale_order_template_ids")
    def _onchange_sale_order_template_ids(self):
        for order in self:
            old_template_ids = order.order_line.mapped("sale_order_template_id")
            new_template_ids = self.env["sale.order.template"].browse(order.sale_order_template_ids.ids)
            to_link = new_template_ids - old_template_ids
            to_unlink = old_template_ids - new_template_ids
            order.order_line = order._prepare_order_line_values_to_link(to_link) + order._prepare_order_line_values_to_unlink(to_unlink)

    def _get_new_sequence(self):
        return self.order_line and self.order_line[-1].sequence + 1 or 10

    def _get_template_lines_with_sequence(self, template, sequence):
        return [Command.create({**line._prepare_order_line_values(), "sequence": sequence + i, "sale_order_template_id": template.id})
                for i, line in enumerate(template.sale_order_template_line_ids)]

    def _prepare_order_line_values_to_link(self, template_ids):
        self.ensure_one()
        order_lines = []
        sequence = self._get_new_sequence()

        for i, template in enumerate(template_ids):
            order_lines.append(Command.create({
                "name": template.name,
                "display_type": "line_section",
                "sequence": sequence + i,
                "sale_order_template_id": template.id,
            }))
            order_lines.extend(self._get_template_lines_with_sequence(template, sequence + i + 1))
            sequence = order_lines[-1][2]["sequence"]

        return order_lines

    def _prepare_order_line_values_to_unlink(self, template_ids):
        return [Command.unlink(line.id) for line in self.order_line.filtered(lambda line: line.sale_order_template_id in template_ids)]
