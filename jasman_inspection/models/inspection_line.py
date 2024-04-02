from odoo import api, fields, models, _
from odoo.exceptions import UserError

class InspectionLine(models.Model):
    _name = "inspection.line"
    _description = "Inspection"

    name = fields.Char()
    quotation_template_id = fields.Many2one(comodel_name="sale.order.template")
    is_task_template = fields.Boolean(related="task_id.is_template")
    sale_order_id = fields.Many2one(comodel_name="sale.order", related="task_id.sale_line_id.order_id", readonly=True)
    task_id = fields.Many2one(comodel_name="project.task")
    urgency = fields.Selection([
            ('none', 'None'),
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('red', 'Red')
        ], default='green')

    @api.constrains('urgency')
    def check_urgency_has_start(self):
        for inspection in self:
            if inspection.urgency == 'none':
                raise UserError(_('Inspections must have at least one star'))
