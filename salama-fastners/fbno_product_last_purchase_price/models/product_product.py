from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_purchase_price = fields.Monetary(
        string='Last Purchase Price',
        currency_field='cost_currency_id',
        readonly=True,
        copy=False,
        help="Unit price (after discount, in the product's unit of measure and company "
             "currency) from the most recently confirmed purchase order.",
    )
    last_purchase_vendor_id = fields.Many2one(
        'res.partner', string='Last Vendor', readonly=True, copy=False, index='btree_not_null',
    )
    last_purchase_date = fields.Datetime(string='Last Purchase Date', readonly=True, copy=False)
    last_purchase_order_id = fields.Many2one(
        'purchase.order', string='Last Purchase Order', readonly=True, copy=False,
    )

    def _get_last_purchase_line(self):
        """Return the product's line on its most recently confirmed purchase order."""
        self.ensure_one()
        order = self.env['purchase.order'].sudo().search([
            ('state', '=', 'purchase'),
            ('order_line.product_id', '=', self.id),
        ], order='date_approve desc, id desc', limit=1)
        return order.order_line.filtered(
            lambda l: l.product_id == self and not l.display_type
        ).sorted('id')[-1:]

    def _update_last_purchase_info(self):
        for product in self.sudo():
            line = product._get_last_purchase_line()
            if not line:
                product.write({
                    'last_purchase_price': 0.0,
                    'last_purchase_vendor_id': False,
                    'last_purchase_date': False,
                    'last_purchase_order_id': False,
                })
                continue
            order = line.order_id
            price = line.uom_id._compute_price(line.price_unit_discounted, product.uom_id)
            date = order.date_approve or order.date_order or fields.Datetime.now()
            price = order.currency_id._convert(
                price, order.company_id.currency_id, order.company_id, date.date(), round=False,
            )
            product.write({
                'last_purchase_price': price,
                'last_purchase_vendor_id': order.partner_id.id,
                'last_purchase_date': date,
                'last_purchase_order_id': order.id,
            })
