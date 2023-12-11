from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    active = fields.Boolean(string='Active',
                            default=True,
                            tracking=True)
    jasman_id = fields.Char(string='Customer Account')
    property_account_payable_group_id = fields.Many2one(string='Account Payable Group',
                                                    comodel_name='account.account',
                                                    compute='_compute_property_account_payable_group_id',
                                                    store=True)
    channel_analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',
                                                  string='Channel Account')
    confirm_delivery = fields.Boolean(string='Delivery Appointment')
    invoice_user_id = fields.Many2one(comodel_name='res.users',
                                      string='Billing User')
    guarantee_expiry = fields.Date(string='Guarantee Limit')
    contract_expiry = fields.Date(string='Contract Expiry')
    supplier_credit_limit = fields.Monetary(string='Supplier Credit Limit')
    supplier_payment_way = fields.Many2one(comodel_name='account.journal',
                                           string='Supplier Payment Way')
    supplier_invoice_user_id = fields.Many2one(comodel_name='res.users',
                                               string='Payment Executive')
    pay_day = fields.Selection([('monday', 'Monday'),
                                ('tuesday', 'Tuesday'),
                                ('wednesday', 'Wednesday'),
                                ('thursday', 'Thursday'),
                                ('friday', 'Friday'),
                                ('saturday', 'Saturday'),
                                ('sunday', 'Sunday')], string='Payment Day')
    payment_reference = fields.Char(string='Payment Reference')

    @api.depends('property_account_payable_id')
    def _compute_property_account_payable_group_id(self):
        for account in self:
            account.property_account_payable_group_id = account.property_account_payable_id
