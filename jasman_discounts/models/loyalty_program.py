from odoo import _, api, fields, models

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'
    
    line_discount = fields.Boolean()
    
    def _get_valid_order_lines(self, order_lines):
        rule_order_lines = dict()
        for rule in self.rule_ids:
           rule._get_valid_order_lines(order_lines, rule_order_lines) 
        return rule_order_lines
