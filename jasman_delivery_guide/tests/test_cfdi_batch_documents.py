from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged

from .common import TestJasmanDeliveryGuideCommon


@tagged('jasman', 'post_install_l10n', 'post_install', '-at_install')
class TestCFDIJasmanBatchWorkflow(TestJasmanDeliveryGuideCommon):

    def test_batch_workflow(self):
        warehouse = self._create_warehouse()
        batch = self._create_batch(warehouse)
        batch.action_done()

        # No pac found.
        self.env.company.l10n_mx_edi_pac = None
        with freeze_time('2017-01-05'):
            batch.l10n_mx_edi_action_send_batch_delivery_guide()
        self.assertRecordValues(batch.l10n_mx_edi_document_ids, [
            {
                'datetime': fields.Datetime.from_string('2017-01-05 00:00:00'),
                'message': "No PAC specified.",
                'state': 'batch_sent_failed',
                'sat_state': False,
                'cancellation_reason': False,
                'cancel_button_needed': False,
                'retry_button_needed': True,
            },
        ])
        self.assertRecordValues(batch, [{'l10n_mx_edi_cfdi_state': None}])

        # Set back the PAC but make it raising an error.
        self.env.company.l10n_mx_edi_pac = 'solfact'
        with freeze_time('2017-01-06'), self.with_mocked_pac_sign_error():
            batch.l10n_mx_edi_action_send_batch_delivery_guide()
        self.assertRecordValues(batch.l10n_mx_edi_document_ids, [
            {
                'datetime': fields.Datetime.from_string('2017-01-06 00:00:00'),
                'message': "turlututu",
                'state': 'batch_sent_failed',
                'sat_state': False,
                'cancellation_reason': False,
                'cancel_button_needed': False,
                'retry_button_needed': True,
            },
        ])
        self.assertRecordValues(batch, [{'l10n_mx_edi_cfdi_state': None}])

        # The failing attachment remains accessible for the user.
        self.assertTrue(batch.l10n_mx_edi_document_ids.attachment_id)

        # Sign.
        with freeze_time('2017-01-07'), self.with_mocked_pac_sign_success():
            batch.l10n_mx_edi_document_ids.action_retry()
        sent_doc_values = {
            'datetime': fields.Datetime.from_string('2017-01-07 00:00:00'),
            'message': False,
            'state': 'batch_sent',
            'sat_state': 'not_defined',
            'cancellation_reason': False,
            'cancel_button_needed': True,
            'retry_button_needed': False,
        }
        self.assertRecordValues(batch.l10n_mx_edi_document_ids, [sent_doc_values])
        self.assertTrue(batch.l10n_mx_edi_cfdi_attachment_id)
        self.assertTrue(batch.l10n_mx_edi_document_ids.attachment_id)
        self.assertRecordValues(batch, [{'l10n_mx_edi_cfdi_state': 'sent'}])

        # Cancel failed.
        self.env.company.l10n_mx_edi_pac = None
        with freeze_time('2017-02-01'):
            batch._l10n_mx_edi_cfdi_try_cancel(batch.l10n_mx_edi_document_ids)
        self.assertRecordValues(batch.l10n_mx_edi_document_ids.sorted(), [
            {
                'datetime': fields.Datetime.from_string('2017-02-01 00:00:00'),
                'message': "No PAC specified.",
                'state': 'batch_cancel_failed',
                'sat_state': False,
                'cancellation_reason': '02',
                'cancel_button_needed': False,
                'retry_button_needed': True,
            },
            sent_doc_values,
        ])

        # Set back the PAC but make it raising an error.
        self.env.company.l10n_mx_edi_pac = 'solfact'
        with freeze_time('2017-02-06'), self.with_mocked_pac_cancel_error():
            batch.l10n_mx_edi_document_ids.sorted()[0].action_retry()
        self.assertRecordValues(batch.l10n_mx_edi_document_ids.sorted(), [
            {
                'datetime': fields.Datetime.from_string('2017-02-06 00:00:00'),
                'message': "turlututu",
                'state': 'batch_cancel_failed',
                'sat_state': False,
                'cancellation_reason': '02',
                'cancel_button_needed': False,
                'retry_button_needed': True,
            },
            sent_doc_values,
        ])

        # Cancel
        with freeze_time('2017-02-07'), self.with_mocked_pac_cancel_success():
            batch.l10n_mx_edi_document_ids.sorted()[0].action_retry()

        batch.l10n_mx_edi_document_ids.invalidate_recordset(fnames=['cancel_button_needed'])
        sent_doc_values['cancel_button_needed'] = False
        sent_doc_values['sat_state'] = 'skip'

        cancel_doc_values = {
            'datetime': fields.Datetime.from_string('2017-02-07 00:00:00'),
            'message': False,
            'state': 'batch_cancel',
            'sat_state': 'not_defined',
            'cancellation_reason': '02',
            'cancel_button_needed': False,
            'retry_button_needed': False,
        }
        self.assertRecordValues(batch.l10n_mx_edi_document_ids.sorted(), [
            cancel_doc_values,
            sent_doc_values,
        ])
        self.assertRecordValues(batch, [{'l10n_mx_edi_cfdi_state': 'cancel'}])

        # Sign again.
        with freeze_time('2017-03-10'), self.with_mocked_pac_sign_success():
            batch.l10n_mx_edi_action_send_batch_delivery_guide()
        sent_doc_values2 = {
            'datetime': fields.Datetime.from_string('2017-03-10 00:00:00'),
            'message': False,
            'state': 'batch_sent',
            'sat_state': 'not_defined',
            'cancellation_reason': False,
            'cancel_button_needed': True,
            'retry_button_needed': False,
        }
        self.assertRecordValues(batch.l10n_mx_edi_document_ids.sorted(), [
            sent_doc_values2,
            cancel_doc_values,
            sent_doc_values,
        ])
        self.assertRecordValues(batch, [{'l10n_mx_edi_cfdi_state': 'sent'}])

        # Sat.
        with freeze_time('2017-04-01'), self.with_mocked_sat_call(lambda x: 'valid' if x['state'] == 'batch_sent' else 'cancelled'):
            batch.l10n_mx_edi_cfdi_try_sat()
        sent_doc_values2['sat_state'] = 'valid'
        cancel_doc_values['sat_state'] = 'cancelled'
        self.assertRecordValues(batch.l10n_mx_edi_document_ids.sorted(), [
            sent_doc_values2,
            cancel_doc_values,
            sent_doc_values,
        ])
        self.assertRecordValues(batch, [{'l10n_mx_edi_cfdi_state': 'sent'}])
