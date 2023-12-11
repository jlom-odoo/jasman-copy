from datetime import date

from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestAccountMoveJasman(TransactionCase):
    def test_account_move_new_fields(self):
        partner = self.env['res.partner'].create({
            'name': 'Test Partner 1',
            'pay_day': 'sunday',
            'payment_reference': 'Test Payment Reference',
        })

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'invoice_date_due': '2021-01-01',
            'partner_id': partner.id,
        })

        self.assertEqual(invoice.payment_reference, partner.payment_reference)
        self.assertEqual(invoice.invoice_date_due, date(2021, 1, 3))

        partner = self.env['res.partner'].create({
            'name': 'Test Partner 2',
            'pay_day': 'thursday',
        })

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'invoice_date_due': '2021-01-01',
            'partner_id': partner.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test Product 1',
                    'quantity': 1,
                    'price_unit': 100,
                }),
            ],
        })

        invoice.action_post()

        self.assertEqual(invoice.payment_reference, invoice.name)
        self.assertEqual(invoice.invoice_date_due, date(2021, 1, 7))
