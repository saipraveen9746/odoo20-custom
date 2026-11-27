from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apps_menu_theme = fields.Selection(
        related='company_id.apps_menu_theme',
        readonly=False,
    )

