from . import models


def post_init_hook(env):
    """Fill last purchase info from already confirmed purchase orders."""
    products = env['purchase.order.line'].search([
        ('order_id.state', '=', 'purchase'),
        ('product_id', '!=', False),
    ]).product_id
    products._update_last_purchase_info()
