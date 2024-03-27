from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    allowed_product_categories_ids = fields.Many2many(comodel_name="product.category")
    allowed_product_child_categ_ids = fields.Many2many(comodel_name="product.category", compute="_compute_allowed_product_child_categ_ids")

    def check_for_child_categories(self, categories):
        childs = self.env['product.category'].search([('parent_id','in', categories.ids)]) - categories
        categories |= childs
        if self.env['product.category'].search([('parent_id','in', childs.ids)]):
            categories |= self.check_for_child_categories(childs)
        return categories

    @api.depends('allowed_product_categories_ids')
    def _compute_allowed_product_child_categ_ids(self):
        self.allowed_product_child_categ_ids = self.check_for_child_categories(self.allowed_product_categories_ids)

