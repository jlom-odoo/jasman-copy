from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(string="Minor Group")
    mayor_group_id = fields.Many2one(string="Mayor Group", comodel_name="product.category", compute="_compute_mayor_group_id", store=True)
    line_id = fields.Many2one(string="Line", comodel_name="product.category", compute="_compute_line_id", store=True)
    multiple_attribute_values = fields.Boolean("Multiple Attribute Values", groups="sales_team.group_sale_manager")

    @api.depends("categ_id")
    def _compute_mayor_group_id(self):
        for report in self:
            report.mayor_group_id = report.categ_id.parent_id if report.categ_id.parent_id else False

    @api.depends("mayor_group_id")
    def _compute_line_id(self):
        for report in self:
            report.line_id = report.mayor_group_id.parent_id if report.mayor_group_id and report.mayor_group_id.parent_id else False
    
    @api.constrains("attribute_line_ids", "multiple_attribute_values")
    def _check_attribute_line_ids(self):
        for product_template in self:
            if not product_template.multiple_attribute_values and product_template.attribute_line_ids.filtered(lambda l: l.value_count > 1):
                raise ValidationError(_("You can't set more than one value per attribute."))
