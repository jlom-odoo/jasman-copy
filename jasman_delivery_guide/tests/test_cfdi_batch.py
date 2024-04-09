from freezegun import freeze_time

from odoo.tests import tagged

from .common import TestJasmanDeliveryGuideCommon


@tagged('jasman', 'post_install_l10n', 'post_install', '-at_install')
class TestCFDIJasmanBatchXml(TestJasmanDeliveryGuideCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='mx'):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env.company.partner_id.city_id = cls.env.ref('l10n_mx_edi_extended.res_city_mx_chh_032').id

    @freeze_time('2017-01-01')
    def test_delivery_guide_batch(self):
        warehouse = self._create_warehouse()
        batch = self._create_batch(warehouse)
        batch.action_done()

        with self.with_mocked_pac_sign_success():
            batch.l10n_mx_edi_action_send_batch_delivery_guide()

        self._assert_batch_cfdi(batch, 'test_delivery_guide_batch')
