from odoo import fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    truck_number = fields.Char(string='Truck Number')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        self.ensure_one()

        if self.mapped('move_line_ids').filtered(lambda x: x.qty_done == 0):
            raise UserError('done quantity should not be zero')

        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    number_of_lot = fields.Integer(string='Number of Lot')

    def generate_lot_wise_move_lines(self, lot_name_listt):
        self.ensure_one()

        move_line_list_of_dict = []

        move_line_vals = {
            'picking_id': self.picking_id.id,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'qty_done': 0,
        }
        for lot_name in lot_name_listt:
            loc = self.location_dest_id._get_putaway_strategy(
                self.product_id, quantity=1, packaging=self.product_packaging_id, additional_qty=0
            )
            move_line_cmd = dict(move_line_vals, lot_name=lot_name, location_dest_id=loc.id)
            move_line_list_of_dict.append((0, 0, move_line_cmd))

        return move_line_list_of_dict

    def action_assign_lot_show_details(self):

        self.ensure_one()
        if self.number_of_lot <= 0:
            raise UserError(_('Number of lot must be greater than zero'))

        lot_name_listt = []

        for i in range(self.number_of_lot):
            sequ = self.env['ir.sequence'].next_by_code('lot.sequence')
            lot_name = (self.picking_id.origin or '') + sequ
            lot_name_listt.append(lot_name)

        move_lines = self.generate_lot_wise_move_lines(lot_name_listt)

        self.write({'move_line_ids': move_lines})

        return self.action_show_details()

    def action_clear_assign_lot_move_lines(self):
        move_lines = self.move_line_ids
        move_lines.unlink()
        return self.action_show_details()

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        for line in self.move_line_ids:
            if line.qty_done != 0:
                line.write({'lot_name': str(line.lot_name) + '-' + str(line.qty_done)})

        return res
