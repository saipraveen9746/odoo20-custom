from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    last_purchase_price = fields.Monetary(
        string='Last Purchase Price',
        currency_field='cost_currency_id',
        compute='_compute_last_purchase_info',
        store=True,
        help="Last purchase price of the most recently purchased variant.",
    )
    last_purchase_vendor_id = fields.Many2one(
        'res.partner', string='Last Vendor', compute='_compute_last_purchase_info', store=True,
    )
    last_purchase_date = fields.Datetime(
        string='Last Purchase Date', compute='_compute_last_purchase_info', store=True,
    )

    @api.depends(
        'product_variant_ids.last_purchase_price',
        'product_variant_ids.last_purchase_vendor_id',
        'product_variant_ids.last_purchase_date',
    )
    def _compute_last_purchase_info(self):
        for template in self:
            variants = template.with_context(active_test=False).product_variant_ids.filtered(
                'last_purchase_date'
            )
            latest = max(variants, key=lambda v: (v.last_purchase_date, v.id), default=False)
            template.last_purchase_price = latest.last_purchase_price if latest else 0.0
            template.last_purchase_vendor_id = latest.last_purchase_vendor_id if latest else False
            template.last_purchase_date = latest.last_purchase_date if latest else False
