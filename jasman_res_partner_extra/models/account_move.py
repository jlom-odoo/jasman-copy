from datetime import timedelta

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    date_due_pay_day = fields.Date(string='Due Pay Day', compute='_compute_date_due_pay_day')

    def _compute_date_due_pay_day(self):
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        today = fields.Date.context_today(self)
        for account_move in self:
            if account_move.state == 'draft':
                account_move.date_due_pay_day = account_move.needed_terms and max(
                    (k['date_maturity'] for k in account_move.needed_terms.keys() if k),
                    default=False,
                ) or account_move.invoice_date_due or today

                if account_move.partner_id.pay_day:
                    diff = days.index(account_move.partner_id.pay_day) - account_move.date_due_pay_day.weekday()
                    diff = diff + 7 if diff < 0 else diff
                    account_move.date_due_pay_day = account_move.date_due_pay_day + timedelta(days=diff)
            else:
                account_move.date_due_pay_day = account_move.date_due_pay_day
