from odoo import api, fields, models, tools, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from collections import Counter 

class OperationReturn(models.TransientModel):
    _inherit = "stock.return.picking"
    
    serial_holder_id = fields.One2many('stock.return.picking.line.return.serial','serial_holder_ids', string="Return List")
    picking_id = fields.Many2one("stock.picking")
    
    # Validation to check if the serial ID is the same from move_lines to serial_holder_id 
    @api.onchange('serial_holder_id')
    def check_other_serial(self):
        if 'serial_holder_id':
            for issued in self.product_return_moves:
                for issued2 in self.serial_holder_id:
                    if issued2.etsi_product_name_duplicate:
                        if issued.product_id != issued2.etsi_product_name_duplicate:
                            check = "Serial Number not found in available returns \n Serial Number: {}".format(issued2.etsi_serial_product_duplicate)
                            raise ValidationError(check)
    
    
    
    # @api.constrains('serial_holder_id')                
    # @api.onchange('serial_holder_id')
    # def check_other_serial(self):

    #         list =[]
    #         list2 =[]
    #         lines =[]

    #         for rec in self:
    #             for issued in rec.product_return_moves:
    #                 print("mga serials", issued.etsi_serial_product)
    #                 list.append(issued.etsi_serial_product)
                    
    #             for issued2 in rec.serial_holder_id:
    #                 if len(rec.serial_holder_id) == 0:
    #                     raise ValidationError(('Product details table can not be empty.'))
    #                 if issued2.etsi_serial_product:
    #                     if issued2.etsi_serial_product not in list:
    #                         print("mga serials1", issued2.etsi_serial_product)
    #                         check = "Serial Number not found in available returns \n Serial Number: {}".format(issued2.etsi_serial_product)
    #                         raise ValidationError(check)
                        
    #                     print(list2)
    #                     if issued2.etsi_serial_product in list2:
    #                         print("Naulit na")
    #                         check_duplicate = "Duplicate serial within the \n Serial Number: {}".format(issued2.etsi_serial_product)
    #                         raise ValidationError(check_duplicate)
                        
    #                         # Mag auto fill ka na

    #                     list2.append(issued2.etsi_serial_product)

    # Return Items Validation
    @api.multi
    def create_returns(self):
        counter = 0
        inputted = []
        for rec in self:
            for return_moves in rec.product_return_moves:
                for lines in rec.serial_holder_id:
                    counter += 1
                    
                    if lines.etsi_serial_product != return_moves.etsi_serial_product:
                        raise ValidationError('Serial Number are not available in returns!')
            
        if counter <= 0:
            raise ValidationError('Return Items cannot be empty!')
        # return super(OperationReturn, self).create_returns()

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError("You may only return one picking at a time!")

        Quant = self.env['stock.quant']
        move_dest_exists = False
        product_return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking:
            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings"))
            for move in picking.move_lines:
                # Filtering of returned products, stupid
                if move.issued_field == "Return":
                    raise ValidationError("Can not be returned!")
                if move.scrapped:
                    continue
                if move.move_dest_id:
                    move_dest_exists = True
                # Sum the quants in that location that can be returned (they should have been moved by the moves that were included in the returned picking)
                quantity = sum(quant.qty for quant in Quant.search([
                    ('history_ids', 'in', move.id),
                    ('qty', '>', 0.0), ('location_id', 'child_of', move.location_dest_id.id)
                ]).filtered(
                    lambda quant: not quant.reservation_id or quant.reservation_id.origin_returned_move_id != move)
                )
                quantity = move.product_id.uom_id._compute_quantity(quantity, move.product_uom)
                    
                # If CATV is selected
                if move.etsi_smart_card_field:
                    product_return_moves.append((
                        0, 0, {
                            'product_id': move.product_id.id, 
                            'quantity': quantity, 
                            'move_id': move.id, 
                            'issued': move.issued_field,
                            'etsi_serial_product': move.etsi_serials_field, 
                            'etsi_smart_card': move.etsi_smart_card_field,
                            'subscriber' : move.subscriber_field.id,
                        }
                    ))
                # If MODEM is selected
                if move.etsi_mac_field:
                    product_return_moves.append((
                        0, 0, {
                            'product_id': move.product_id.id, 
                            'quantity': quantity, 
                            'move_id': move.id, 
                            'issued': move.issued_field,
                            'etsi_serial_product': move.etsi_serials_field, 
                            'etsi_mac_product': move.etsi_mac_field, 
                            'subscriber' : move.subscriber_field.id,
                        }
                    ))
                # If MODEM or Smart card does not exist
                if not move.etsi_smart_card_field or move.etsi_mac_field:
                    product_return_moves.append((
                        0, 0, {
                            'product_id': move.product_id.id, 
                            'quantity': quantity, 
                            'move_id': move.id, 
                            'issued': move.issued_field,
                            'etsi_serial_product': move.etsi_serials_field, 
                            'subscriber' : move.subscriber_field.id,
                        }
                    ))
            
            res = super(OperationReturn, self).default_get(fields)

            if not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': product_return_moves})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest_exists})
            if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
                res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
            if 'original_location_id' in fields:
                res.update({'original_location_id': picking.location_id.id})
            if 'location_id' in fields:
                location_id = picking.location_id.id
                if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                    location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                res['location_id'] = location_id
            return res
        

    @api.multi
    def _create_returns(self):
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])

        return_moves = self.product_return_moves.mapped('move_id')
        unreserve_moves = self.env['stock.move']
        for move in return_moves:
            to_check_moves = self.env['stock.move'] | move.move_dest_id
            while to_check_moves:
                current_move = to_check_moves[-1]
                to_check_moves = to_check_moves[:-1]
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    unreserve_moves |= current_move
                split_move_ids = self.env['stock.move'].search([('split_from', '=', current_move.id)])
                to_check_moves |= split_move_ids

        if unreserve_moves:
            unreserve_moves.do_unreserve()
            # break the link between moves in order to be able to fix them later if needed
            unreserve_moves.write({'move_orig_ids': False})

        # create new picking for returned products
        # Code to return to either team return or subscriber return 
        # Number of Picking Type ID for Team Return
        if 'serial_holder_id':
            for issued in self.product_return_moves:
                
                if issued.subscriber == False:
                    database2 = self.env['stock.picking.type']            
                    search_value2 = database2.search([('name', 'like', 'Team Return') or ('name', 'like', 'Team Returns') ], limit=1).id
                    picking_type_id = search_value2

                else:
                    # Number of Picking Type ID for Subscriber Return 
                    database3 = self.env['stock.picking.type']            
                    search_value3 = database3.search([('name', 'like', 'Subscriber Return')], limit=1).id
                    picking_type_id = search_value3

        new_picking = picking.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': picking.name,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': picking},
            subtype_id=self.env.ref('mail.mt_note').id)

        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            new_qty = return_line.quantity
            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if return_line.move_id.origin_returned_move_id.move_dest_id.id and return_line.move_id.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = return_line.move_id.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1
                return_line.move_id.copy({
                    'product_id': return_line.product_id.id,
                    'product_uom_qty': new_qty,
                    'picking_id': new_picking.id,
                    'state': 'draft',
                    'location_id': return_line.move_id.location_dest_id.id,
                    'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
                    'picking_type_id': picking_type_id,
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': return_line.move_id.id,
                    'procure_method': 'make_to_stock',
                    'move_dest_id': move_dest_id,
                })

        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking.id, picking_type_id
        
class OperationReturnLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'
    
    issued = fields.Char(string="Issued")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    subscriber = fields.Char("Subscriber")
    
        
class OperationReturnLineTwo(models.TransientModel):
    _name = 'stock.return.picking.line.return.serial'
    
    serial_holder_ids = fields.Many2one('stock.return.picking')
    product_name = fields.Many2one('product.product')
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    issued_return = fields.Char(string="Issued", default="Returned")
    subscriber = fields.Char("Subscriber")
    picking_id = fields.Many2one("stock.picking")

    etsi_product_name_duplicate = fields.Many2one(related="product_name") 
    etsi_serial_product_duplicate = fields.Char(related="etsi_serial_product")
    etsi_mac_product_duplicate = fields.Char(related="etsi_mac_product")
    etsi_smart_card_duplicate = fields.Char(related="etsi_smart_card")

    @api.multi
    @api.onchange('etsi_serial_product')
    def onchange_auto_fill(self):
        # Validation 
        # x = self.env['stock.move'].search([('etsi_serial','=',rec.etsi_serial_product)])
        # for sarili in self:
        #     for data in x:
        #         if data.product_id.id == sarili.product_name:
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_id'))
       
        # product_checker = False
        # for picking in pickings:
        #     for stock_move in picking.move_lines:
        #         if stock_move.etsi_serials_field == self.etsi_serial_product:
        #             product_checker = True
        # if product_checker:
        #     raise ValidationError("ok na tayo! char")
    
        # for rec in self:
        #     database = self.env['etsi.inventory']
        #     duplicate_count = self.env['etsi.inventory'].search_count([('etsi_serial', '=', rec.etsi_serial_product)])
        #     search_first = database.search([('etsi_serial','=',rec.etsi_serial_product)])
        #     if rec.etsi_serial_product == False:
        #         pass
        #     elif duplicate_count < 1:
        #         raise ValidationError("Serial not found in the database.")
        #     else:
        #         test = database.search([('etsi_serial','=', rec.etsi_serial_product)])
        #         rec.product_name = test.etsi_product_id.id
        #         rec.etsi_serial_product = test.etsi_serial
        #         rec.etsi_mac_product = test.etsi_mac
        #         rec.etsi_smart_card = test.etsi_smart_card
                
                
class TransferData(models.Model):
    _inherit = "stock.picking"   
    
    # When validate button clicked
    @api.multi
    def do_new_transfer(self):
        product_lists = []
        product_serials = []
        for rec in self:
            if rec.picking_type_id.name == "Subscriber Return" or rec.picking_type_id.name == "Team Return":
                for plines in rec.move_lines:
                    product_lists.append(plines.product_id)
                    product_serials.append(plines.etsi_serials_field)
        
        inventory_stats = self.env['etsi.inventory'].search([])
        for searched_ids in inventory_stats:
            if searched_ids.etsi_product_id in product_lists:
                if searched_ids.etsi_serial in product_serials:
                    searched_ids.update({'etsi_status': 'available'})
        return super(TransferData, self).do_new_transfer()