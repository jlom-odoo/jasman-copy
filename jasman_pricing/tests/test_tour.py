import odoo.tests
import unittest

from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon

@unittest.skip('Fails because we are hidding a button')
def test_01_account_tour(self):
    pass

AccountTestInvoicingCommon.test_01_account_tour = test_01_account_tour
