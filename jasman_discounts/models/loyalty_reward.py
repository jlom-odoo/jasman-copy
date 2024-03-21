import ast

from odoo import _, api, fields, models
from odoo.osv import expression

class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'
    
    discount_sale_line_domain = fields.Char(default="[]")
    
    def _get_discount_sale_line_domain(self, order_line):
        if self.discount_sale_line_domain and self.discount_sale_line_domain != '[]':
            return order_line.filtered_domain(ast.literal_eval(self.discount_sale_line_domain))
        return order_line
