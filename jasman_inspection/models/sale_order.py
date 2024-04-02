from odoo import api, fields, models, _
from odoo.fields import Command
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    additional_optional_line_ids = fields.One2many(comodel_name="sale.order.option", compute="_compute_additional_optional_line_ids")

    @api.depends('sale_order_option_ids.is_additional', 'sale_order_option_ids.is_present')
    def _compute_additional_optional_line_ids(self):
        for order in self:
            optional_lines = order.sale_order_option_ids.filtered(
                lambda line: line.is_additional and not line.is_present
                )
            order.additional_optional_line_ids = optional_lines.ids if optional_lines else False

    def _can_be_edited_on_portal(self):
        return super()._can_be_edited_on_portal() or self.env.context.get("from_backend")
    
    def add_extra_quote(self):
        self.ensure_one()
        inspection_stage = self.env['crm.stage'].search([
            ('team_id','=', self.team_id.id),
            ('is_inspection_stage', '=', 'True')
            ])
        if not inspection_stage:
            raise UserError(_("Please first set an Inspection CRM Stage."))
        lead_values = {
            'name': _('%s inspection opportunity', self.name),
            'type': 'opportunity',
            'team_id': self.team_id.id,
            'stage_id': inspection_stage[0].id,
        }
        new_lead = self.env['crm.lead'].create(lead_values)
        new_order = self.copy()
        new_order_lines = [
            Command.delete(line.id)
            for line in new_order.order_line
            ] + [
            Command.create(option_line.with_context(from_backend=True)._get_values_to_add_to_order())
            for option_line in self.additional_optional_line_ids
        ]
        new_option_lines = [
            Command.delete(line.id)
            for line in new_order.sale_order_option_ids
        ]
        new_order.write({
            'order_line': new_order_lines,
            'sale_order_option_ids': new_option_lines,
            'opportunity_id': new_lead.id,
        })
        return {
            'name': _("New Opportunity"),
            'type': "ir.actions.act_window",
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': new_lead.id,
        }
