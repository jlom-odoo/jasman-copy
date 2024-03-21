import ast

from odoo import _, api, fields, models
from odoo.osv import expression

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'
    
    sale_line_domain = fields.Char(default="[]")
    
    def _get_valid_order_lines(self, order_lines, rule_order_lines):
        for rule in self:
            rule_order_lines[rule] = order_lines
            if rule.sale_line_domain != '[]':
                rule_order_lines[rule] = order_lines.filtered_domain(ast.literal_eval(rule.sale_line_domain))
