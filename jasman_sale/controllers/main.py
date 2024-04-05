from odoo import models
from odoo.addons.sign.controllers.main import Sign


class SignInherit(Sign):

    def get_document_qweb_context(self, sign_request_id, token, **post):
        res = super().get_document_qweb_context(sign_request_id, token, **post)
        if res['current_request_item']:
            for item_type in res['sign_item_types']:
                if item_type['sale_auto_field']:
                    try:
                        auto_field = res['current_request_item'].sign_request_id.template_id.sale_order_id.mapped(item_type['sale_auto_field'])
                        item_type['auto_value'] = auto_field[0] if auto_field and not isinstance(auto_field, models.BaseModel) else ''
                    except Exception:
                        item_type['auto_value'] = ''
        return res
