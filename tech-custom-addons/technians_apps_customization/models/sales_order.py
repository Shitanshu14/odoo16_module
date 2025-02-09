from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.onchange('order_line')
    def _onchange_order_line_set_sn(self):
        sl_no = 1
        for line in self.order_line:
            if line.display_type not in ['line_note', 'line_section']:
                line.sl_no = sl_no
                sl_no += 1
            else:
                line.sl_no = 1

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sl_no = fields.Integer(string='Sl. No.')