from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def write(self, vals):
        if 'state' not in vals and 'date_approve' not in vals and 'currency_id' not in vals:
            return super().write(vals)
        products = self.order_line.product_id
        res = super().write(vals)
        # Lines may have been added in the same write
        (products | self.order_line.product_id)._update_last_purchase_info()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    _LAST_PURCHASE_TRIGGER_FIELDS = {'product_id', 'price_unit', 'discount', 'uom_id'}

    def write(self, vals):
        if not self._LAST_PURCHASE_TRIGGER_FIELDS.intersection(vals):
            return super().write(vals)
        confirmed = self.filtered(lambda l: l.order_id.state == 'purchase')
        products = confirmed.product_id
        res = super().write(vals)
        (products | confirmed.product_id)._update_last_purchase_info()
        return res

    def unlink(self):
        products = self.filtered(lambda l: l.order_id.state == 'purchase').product_id
        res = super().unlink()
        products.exists()._update_last_purchase_info()
        return res
