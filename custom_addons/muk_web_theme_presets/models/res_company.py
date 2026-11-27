from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    apps_menu_theme = fields.Selection(
        selection=[
            ('custom', 'Custom Image'),
            # Dark / Night Themes
            ('midnight', 'Midnight Grid'),
            ('aurora', 'Aurora Borealis'),
            ('cosmic', 'Cosmic Nebula'),
            ('slate', 'Executive Slate'),
            ('sunset', 'Sunset Horizon'),
            # Color Themes
            ('lagoon', 'Lagoon'),
            ('emerald', 'Royal Emerald'),
            ('oceanic', 'Deep Sapphire'),
            # Whitish / Light Themes
            ('ceramic', 'Ceramic Light'),
            ('frost', 'Alpine Frost (Ice White)'),
            ('linen', 'Warm Linen (Warm Ivory)'),
            ('pearl', 'Silken Pearl (Opalescent)'),
            ('canvas', 'Studio Canvas (Grid Light)'),
            ('blush', 'Rose Quartz (Pastel White)'),
            ('sandstone', 'Desert Sandstone (Sunlit)'),
            ('glass', 'Glass Grid (Mint Light)'),
            ('orchard', 'Orchard (Sage Light)'),
        ],
        string='Apps Menu Theme',
        default='custom',
        required=True,
    )
