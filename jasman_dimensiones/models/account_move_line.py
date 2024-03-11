from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        AccountMove = self.env['account.move'].with_prefetch([vals['move_id'] for vals in vals_list])
        for vals in vals_list:
            vals['analytic_distribution'] = self._build_analytic_distribution(AccountMove.browse(vals['move_id']))
        return super().create(vals_list)

    @api.model
    def _build_analytic_distribution(self, move):
        ceco_account = self.env.user.ceco_analytic_account_id.id
        channel_account = self.env.user.channel_analytic_account_id.id
        zona_account = self.env.user.zona_analytic_account_id.id
        subzona_account = self.env.user.subzona_analytic_account_id.id
        payment_method_account = move.l10n_mx_edi_payment_method_id.analytic_account_id.id

        return {
            f'{ceco_account},{channel_account},{zona_account},{subzona_account},{payment_method_account}': 100
        }
