from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    template_task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task Template",
        domain=[("is_template", "=", True)]
        )
    is_inspection_task = fields.Boolean()
