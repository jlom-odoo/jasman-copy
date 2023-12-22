from datetime import timedelta

from odoo import models


DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        for account_move in self:
            if account_move.partner_id.pay_day:
                diff = DAYS.index(account_move.partner_id.pay_day) - account_move.invoice_date_due.weekday()
                diff = diff + 7 if diff < 0 else diff
                account_move.invoice_date_due = account_move.invoice_date_due + timedelta(days=diff)
        return res
