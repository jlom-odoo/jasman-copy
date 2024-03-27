from odoo import api, models, fields, _
from markupsafe import Markup


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pricelist_item_id = fields.Many2one(
        search='_search_pricelist_item_id',
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id')
    min_margin = fields.Float(related="pricelist_item_id.min_margin")
    min_price = fields.Monetary(currency_field='currency_id', compute="_compute_min_price")
    is_price_blocked = fields.Boolean(related="product_id.is_price_blocked")
    is_liberated = fields.Boolean()
    can_confirm = fields.Boolean(compute="_compute_can_confirm") 

    @api.depends('product_id.categ_id')
    @api.depends_context('uid')
    def _compute_can_confirm(self):
        for line in self:     
            line.can_confirm = line.product_id.categ_id.id in self.env.user.allowed_product_child_categ_ids.ids
            
    @api.depends('min_price','purchase_price')
    def _compute_min_price(self):
        for line in self:
            line.min_price = line.purchase_price * (1 + line.min_margin)
            
    def write(self, values):
        if 'is_liberated' in values:
            self._update_is_liberated(values, self.order_id)
        return super().write(values)

    def _update_is_liberated(self, values, orders):
        for order in orders:
            order_lines = self.filtered(lambda x: x.order_id == order)            
            msg = Markup("<b>%s</b><ul>") % _("The product has been liberated/blocked.")
            for line in order_lines:
                if 'product_id' in values and values['product_id'] != line.product_id.id:
                    # tracking is meaningless if the product is changed as well.
                    continue
                msg += Markup("<li> %s: <br/>") % line.product_id.display_name
                msg += _(
                    "Is liberated: %(old)s -> %(new)s",
                    old=line.is_liberated,
                    new=values["is_liberated"]
                ) + Markup("<br/>")
            msg += Markup("</ul>")
            order.message_post(body=msg)

    def _search_pricelist_item_id(self, operator, value):
        return [('pricelist_item_id.id', operator, value)]
