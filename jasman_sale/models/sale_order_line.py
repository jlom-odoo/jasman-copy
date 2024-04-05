from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_domain_filter = fields.Char(compute='_compute_product_domain_filter', string='Product Domain')
    technician_id = fields.Many2one(comodel_name='hr.employee', string='Technician')

    @api.depends('order_id.is_vehicle_required')
    def _compute_product_domain_filter(self):
        for line in self:
            product_domain_filter = [('sale_ok', '=', True)]
            if not line.order_id.is_vehicle_required:
                product_domain_filter.append(('is_sale_mandatory_vehicle', '=', False))
            line.product_domain_filter = product_domain_filter

