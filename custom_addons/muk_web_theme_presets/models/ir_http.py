from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        if self.env.user._is_internal():
            allowed = result['user_companies']['allowed_companies']
            for company in self.env.user.company_ids:
                if company.id in allowed:
                    allowed[company.id]['apps_menu_theme'] = company.apps_menu_theme
                elif str(company.id) in allowed:
                    allowed[str(company.id)]['apps_menu_theme'] = company.apps_menu_theme
        return result

