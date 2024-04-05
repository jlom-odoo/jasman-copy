from odoo import api, models


class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'
    
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if not res.get('template_id'):
            return res
        template_id = self.env['sign.template'].browse(res['template_id'])
        customer_id = self.env.ref('sign.sign_item_role_customer').id
        employee_id = self.env.ref('sign.sign_item_role_employee').id
        for signer_id in res['signer_ids']:
            if signer_id[2]['role_id'] == customer_id:
                signer_id[2]['partner_id'] = template_id.sale_order_id.partner_id.id
            elif signer_id[2]['role_id'] == employee_id:
                signer_id[2]['partner_id'] = template_id.sale_order_id.user_id.partner_id.id
        return res
