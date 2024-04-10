from odoo.addons.l10n_mx_edi_stock_extended_30.tests.common import TestMXEdiStockCommon


class TestJasmanDeliveryGuideCommon(TestMXEdiStockCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref="mx"):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data["company"].write({
            "l10n_mx_edi_pac": "solfact",
        })

        cls.product_c.write({
            "name": "Lámpara de oficina",
            "unspsc_code_id": cls.env.ref("product_unspsc.unspsc_code_56101900").id,
        })

        cls.vehicle_pedro.write({
            "gross_vehicle_weight": 2.0,
        })
        
        cls.customer_location_2 = cls.env["stock.location"].create({
            "name": "Test Customers",
            "location_id": cls.env.ref("stock.stock_location_locations_partner").id,
            "usage": "customer",
        })
        cls.internal_location_2 = cls.env["stock.location"].create({
            "name": "Stock 2",
            "location_id": cls.env.ref("stock.stock_location_locations").id,
        })

        cls.partner_mx_chih = cls.env["res.partner"].create({
            "name": "TEST_CHIH",
            "street": "Street Calle",
            "city": "Hidalgo del Parral",
            "country_id": cls.env.ref("base.mx").id,
            "state_id": cls.env.ref("base.state_mx_chih").id,
            "zip": "33826",
            "vat": "ICV060329BY0",
            "parent_id": cls.partner_mx.id,
        })
        cls.partner_mx_oax = cls.env["res.partner"].create({
            "name": "TEST_OAX",
            "street": "Street Calle",
            "city": "Oaxaca de Juárez",
            "country_id": cls.env.ref("base.mx").id,
            "state_id": cls.env.ref("base.state_mx_oax").id,
            "zip": "68025",
            "vat": "ICV060329BY0",
            "parent_id": cls.partner_mx.id,
        })

    def _create_picking(self, warehouse, picking_vals, move_vals):
        picking = self.env["stock.picking"].create(picking_vals)

        self.env["stock.move"].create({
            "picking_id": picking.id,
            **move_vals,
        })

        self.env["stock.quant"]._update_available_quantity(
            self.product_c, 
            self.env["stock.location"].browse(move_vals["location_id"]), 
            10.0)
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids[0].move_line_ids[0].quantity = 10
        picking.move_ids[0].picked = True
        return picking
    
    def _create_batch(self, warehouse, picking_vals_list=None, move_vals_list=None):
        # By default, use values that lead to
        # a successful result (happy path)
        if not picking_vals_list:
            picking_vals_list = [
                {
                    "location_id": warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_location.id,
                    "picking_type_id": warehouse.out_type_id.id,
                    "partner_id": self.partner_mx_chih.id,
                    "l10n_mx_edi_transport_type": "01",
                    "l10n_mx_edi_vehicle_id": self.vehicle_pedro.id,
                    "l10n_mx_edi_distance": 60,
                    "state": "draft",
                },
                {
                    "location_id": self.internal_location_2.id,
                    "location_dest_id": self.customer_location_2.id,
                    "picking_type_id": warehouse.out_type_id.id,
                    "partner_id": self.partner_mx_oax.id,
                    "l10n_mx_edi_transport_type": "01",
                    "l10n_mx_edi_vehicle_id": self.vehicle_pedro.id,
                    "l10n_mx_edi_distance": 40,
                    "state": "draft",
                },
            ]
        if not move_vals_list:
            move_vals_list = [
                {
                    "name": self.product_c.name,
                    "product_id": self.product_c.id,
                    "product_uom_qty": 3,
                    "product_uom": self.product_c.uom_id.id,
                    "location_id": warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_location.id,
                    "state": "confirmed",
                    "description_picking": self.product_c.name,
                    "company_id": warehouse.company_id.id,
                },
                {
                    "name": self.product_c.name,
                    "product_id": self.product_c.id,
                    "product_uom_qty": 2,
                    "product_uom": self.product_c.uom_id.id,
                    "location_id": self.internal_location_2.id,
                    "location_dest_id": self.customer_location_2.id,
                    "state": "confirmed",
                    "description_picking": self.product_c.name,
                    "company_id": warehouse.company_id.id,
                },
            ]
        pickings = [self._create_picking(warehouse, picking_vals=p[0], move_vals=p[1])
                    for p in zip(picking_vals_list, move_vals_list)]
        return self.env['stock.picking.batch'].create({
            'name': 'BATCH/00001',
            'company_id': self.env.company.id,
            'picking_ids': [p.id for p in pickings],
            'l10n_mx_edi_transport_type': '01',
            'l10n_mx_edi_vehicle_id': self.vehicle_pedro.id,
            'figure_id': self.vehicle_pedro.figure_ids[0].id,
        })
    
    def _assert_batch_cfdi(self, batch, filename):
        document = batch.l10n_mx_edi_document_ids \
            .filtered(lambda x: x.state == 'batch_sent')[:1]
        self._assert_document_cfdi(document, filename)
