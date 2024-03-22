from odoo import models, fields


class MissingTire(models.Model):
    _name = "missing.tire"
    _description= "Model to store information about the tires that were not available when making the sale order."

    analytic_account_id = fields.Many2one(string="Channel", comodel_name="account.analytic.account")
    order_id = fields.Many2one(comodel_name="sale.order")
    product_tmpl_id = fields.Many2one(string="Product", comodel_name="product.template")
    quantity = fields.Integer(string="Quantity")
    action_to_take = fields.Selection(
        selection=[
            ("buy_stock", "Suggestion to buy stock"),
            ("no_stock", "No stock in plant"),
            ("alternate_codes","Alternate codes"),
            ("sales","Sales")
        ]
    )
