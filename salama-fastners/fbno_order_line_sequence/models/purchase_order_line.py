from odoo import api, models


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['purchase.order.line', 'order.line.sl.no.mixin']

    @api.depends('order_id.order_line.sequence', 'order_id.order_line.display_type')
    def _compute_sl_no(self):
        return super()._compute_sl_no()
