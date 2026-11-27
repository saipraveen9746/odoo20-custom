from odoo import fields, models


class OrderLineSlNoMixin(models.AbstractModel):
    _name = 'order.line.sl.no.mixin'
    _description = 'Order Line Serial Number Mixin'

    sl_no = fields.Integer(
        string='Sl. No.',
        compute='_compute_sl_no',
        help="Serial number of the line within its order. Section and note lines are not numbered.",
    )

    def _compute_sl_no(self):
        self.sl_no = 0
        for order in self.order_id:
            # sorted() is stable: lines with equal sequence keep their current order
            product_lines = order.order_line.filtered(lambda l: not l.display_type).sorted('sequence')
            numbers = {line: index for index, line in enumerate(product_lines, start=1)}
            for line in self.filtered(lambda l: l.order_id == order):
                line.sl_no = numbers.get(line, 0)
