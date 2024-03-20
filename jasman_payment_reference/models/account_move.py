import re

from odoo import fields, models


ALPHANUM_EQUIVALENT = {
    'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5', 'F': '6', 'G': '7', 'H': '8', 'I': '9', 
    'J': '1', 'K': '2', 'L': '3', 'M': '4', 'N': '5', 'O': '6', 'P': '7', 'Q': '8', 'R': '9', 
    'S': '2', 'T': '3', 'U': '4', 'V': '5', 'W': '6', 'X': '7', 'Y': '8', 'Z': '9'
}

class AccountMove(models.Model):
    _inherit = 'account.move'

    odometer = fields.Float()
    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
    ], default='kilometers', required=True)
    
    def _get_bank_verification_code(self, payment_reference_list):
        constants = [13, 17, 19, 23, 11]
        verification_code = sum(int(char) * constants[i % len(constants)] for i, char in enumerate(payment_reference_list[::-1][1:]))
        return str((verification_code + 330) % 97 + 1)

    def _get_payment_reference(self, original_payment_reference):
        """ This method returns a payment reference with a Banorte's (Mexican Bank) verification code.
        Parameters:
        - original_payment_reference (string): Payment reference w/o verification code.
        
        Returns:
        - string: Final payment reference containing the original reference and the bank verification code.
        """
        transformed_payment_reference = re.sub('[^A-Z0-9]+', '', original_payment_reference.upper())
        converted_chars = [ALPHANUM_EQUIVALENT.get(char, char) for char in transformed_payment_reference]
        reference_prefix = ''.join(converted_chars)
        return reference_prefix + self._get_bank_verification_code(converted_chars)

    def _compute_payment_reference(self):
        for move in self.filtered(lambda m: (
            m.state == 'posted' 
            and m.move_type == 'out_invoice' 
            and not m.payment_reference
        )):
            if move.partner_id.payment_reference:
                move.payment_reference = move.partner_id.payment_reference
            elif (
                not move.partner_id.use_partner_credit_limit 
                and move.l10n_mx_edi_payment_method_id.code
                and move.create_uid.zona_analytic_account_id.code
            ):
                date = move.invoice_date
                original_payment_reference = (
                    f'{date.year}{date.month}{date.day}{move.journal_id.code}'
                    f'{move.l10n_mx_edi_payment_method_id.code}{move.create_uid.zona_analytic_account_id.code}'
                )
                move.payment_reference = self._get_payment_reference(original_payment_reference)
            else:
                original_payment_reference = move.name.replace(move.journal_id.code, '')
                move.payment_reference = self._get_payment_reference(original_payment_reference)
            