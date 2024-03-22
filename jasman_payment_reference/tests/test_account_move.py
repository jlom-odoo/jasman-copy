from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountMoveJasman(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
    
        analytic_plan = cls.env['account.analytic.plan'].create({
            'name': 'Test Analytic Plan',
        })

        analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
            'code': '1',
            'plan_id': analytic_plan.id,
        })
        
        account_journal = cls.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'sale',
            'code': '1100',
        })
        
        account_account = cls.env['account.account'].create({
            'code': '23234234',
            'name': 'Test',
            'account_type': 'asset_cash',
        })

        cls.jasman_invoice_values = {
            'name': f'{account_journal.code}/2023/00001',
            'move_type': 'out_invoice',
            'invoice_date': '2023-12-27',
            'journal_id': account_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test Product 1',
                    'quantity': 1,
                    'price_unit': 100,
                    'account_id': account_account.id,
                }),
            ],
            'l10n_mx_edi_payment_method_id': 2,
        }

        cls.env.user.zona_analytic_account_id = analytic_account.id

    def test_account_move_payment_reference_case_non_credit(self):

        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })

        move = self.env['account.move'].create({'partner_id': partner.id} | self.jasman_invoice_values)
        move.action_post()

        self.assertEqual(move.payment_reference, '20231227110002135')

    def test_account_move_payment_reference_case_credit(self):

        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'use_partner_credit_limit': True,
        })

        move = self.env['account.move'].create({'partner_id': partner.id} | self.jasman_invoice_values)
        move.action_post()

        self.assertEqual(move.payment_reference, '110020230000170')

    def test_account_move_payment_reference_case_user(self):

        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'payment_reference': '123456789'
        })

        move = self.env['account.move'].create({'partner_id': partner.id} | self.jasman_invoice_values)
        move.action_post()

        self.assertEqual(move.payment_reference, '123456789')



