from odoo import api, models


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line', 'order.line.sl.no.mixin']

    @api.depends('order_id.order_line.sequence', 'order_id.order_line.display_type')
    def _compute_sl_no(self):
        return super()._compute_sl_no()
