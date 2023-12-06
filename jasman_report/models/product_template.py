from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(comodel_name="product.category", string="Minor Group")
    mayor_group_id = fields.Many2one(comodel_name="product.category", string="Mayor Group", compute="_compute_mayor_group_id", store=True)
    line_id = fields.Many2one(comodel_name="product.category", string="Line", compute="_compute_line_id", store=True)
    multiple_attribute_values = fields.Boolean("Multiple Attribute Values", groups="sales_team.group_sale_manager")

    @api.depends("categ_id")
    def _compute_mayor_group_id(self):
        product_tmpl_ids = self.filtered(lambda _product_tmpl: _product_tmpl.categ_id.parent_id)
        self.mayor_group_id = False
        categ_by_product_id = {p.id: p.categ_id.parent_id for p in product_tmpl_ids}
        for product_tmpl_id in product_tmpl_ids:
            product_tmpl_id.mayor_group_id = categ_by_product_id.get(product_tmpl_id.id)

    @api.depends("mayor_group_id")
    def _compute_line_id(self):
        product_tmpl_ids = self.filtered(lambda _product_tmpl: _product_tmpl.mayor_group_id.parent_id)
        self.line_id = False
        categ_by_product_id = {p.id: p.mayor_group_id.parent_id for p in product_tmpl_ids}
        for product_tmpl_id in product_tmpl_ids:
            product_tmpl_id.line_id = categ_by_product_id.get(product_tmpl_id.id)
    
    @api.constrains("attribute_line_ids", "multiple_attribute_values")
    def _check_attribute_line_ids(self):
        product_tmpl_ids = self.filtered(lambda _product_template: not _product_template.multiple_attribute_values and _product_template.attribute_line_ids.filtered(lambda l: l.value_count > 1))
        if product_tmpl_ids:
            raise ValidationError(_("You can't set more than one value per attribute."))
