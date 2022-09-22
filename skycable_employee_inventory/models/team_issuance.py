from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError


class Team_issuance(models.Model):
    _inherit = 'stock.move'
    product_id_duplicate = fields.Many2one(related="product_id")

    etsi_serials_field = fields.Char(string="Serial ID")
    etsi_mac_field = fields.Char(string="Mac ID")
    etsi_smart_card_field = fields.Char(string="Smart Card")

    # duplicate
    etsi_serials_field_duplicate = fields.Char(related="etsi_serials_field")
    etsi_mac_field_duplicate = fields.Char(related="etsi_mac_field")
    etsi_smart_card_field_duplicate = fields.Char(related="etsi_smart_card_field")

    checker_box = fields.Boolean(string="To be issued")

    issued_field = fields.Char(string="Issued",default="No")
    subscriber_field = fields.Many2one('res.partner',string="Subcscriber")

    @api.multi
    @api.onchange('checker_box')
    def checker_change(self): 
        for rec in self:
            if rec.etsi_serials_field != False:
                search_data = self.env['stock.move'].search_count([('etsi_serials_field','=',rec.etsi_serials_field),('state','not in',['cancel']),('picking_type_id.return_picking_type_id','!=',False),('issued_field','!=','Return')])
                if search_data > 1:
                    rec.checker_box = False
                    return {'warning': {'title': ('FlexERP Warning'), 'message': ('Data Selected is already existing in subscriber issuance.'),},}

            elif rec.etsi_mac_field != False:
                search_data = self.env['stock.move'].search_count([('etsi_mac_field','=',rec.etsi_mac_field),('state','not in',['cancel']),('picking_type_id.return_picking_type_id','!=',False),('issued_field','!=','Return')])
                if search_data > 1:
                    rec.checker_box = False
                    return {'warning': {'title': ('FlexERP Warning'), 'message': ('Data Selected is already existing in subscriber issuance.'),},}
            
            elif rec.etsi_smart_card_field != False:
                search_data = self.env['stock.move'].search_count([('etsi_smart_card_field','=',rec.etsi_smart_card_field),('state','not in',['cancel']),('picking_type_id.return_picking_type_id','!=',False),('issued_field','!=','Return')])
                if search_data > 1:
                    rec.checker_box = False
                    return {'warning': {'title': ('FlexERP Warning'), 'message': ('Data Selected is already existing in subscriber issuance.'),},}
            

    @api.multi
    @api.onchange('etsi_serials_field','etsi_mac_field','etsi_smart_card_field')
    def auto_fill_details_01(self): 
        self.ensure_one()
        for rec in self:
            database = self.env['etsi.inventory']
            # database2 = self.env['stock.move'].search([], limit=1)

            duplicate_count = self.env['etsi.inventory'].search_count([('etsi_serial', '=', rec.etsi_serials_field)])
            duplicate_count2 = self.env['etsi.inventory'].search_count([('etsi_mac', '=', rec.etsi_mac_field)])
            duplicate_count3 = self.env['etsi.inventory'].search_count([('etsi_smart_card', '=', rec.etsi_smart_card_field)])

            search_first = database.search([('etsi_serial','=',rec.etsi_serials_field)])
            search_first2 = database.search([('etsi_mac','=',rec.etsi_mac_field)])
            search_first3 = database.search([('etsi_smart_card','=',rec.etsi_smart_card_field)])


            if rec.etsi_serials_field != False:
                if duplicate_count < 1:
                    raise ValidationError("Serial not found in the database.")
                else:
                    if search_first.etsi_status == 'used':
                        raise ValidationError("Serial is already used.")
                    else:

                        # search_status = self.env['stock.move'].search_count([('etsi_serials_field','=',rec.etsi_serials_field)])

                        # if search_status == 0:
                        stock_moves = self.env['stock.move'].search([('state','not in',['cancel']),('picking_type_id.code','=','internal'),('picking_type_id.return_picking_type_id','!=',False),('issued_field','!=','Return')])

                        # stock_moves = self.env['stock.move'].search([('state','not in',['cancel']),('picking_type_id.code','=','internal'),('picking_type_id.return_picking_type_id','!=',False)])
                        
                        if stock_moves:
                            for moves in stock_moves:
                                if moves.etsi_serials_field == rec.etsi_serials_field:
                                    raise ValidationError("Serial is already on another process.")
                                else:
                                    test = database.search([('etsi_serial','=',rec.etsi_serials_field)])
                                    rec.product_id = test.etsi_product_id.id
                                    rec.etsi_serials_field = test.etsi_serial
                                    rec.etsi_mac_field = test.etsi_mac  
                                    rec.etsi_smart_card_field = test.etsi_smart_card
                        else:
                            test = database.search([('etsi_serial','=',rec.etsi_serials_field)])
                            rec.product_id = test.etsi_product_id.id
                            rec.etsi_serials_field = test.etsi_serial
                            rec.etsi_mac_field = test.etsi_mac  
                            rec.etsi_smart_card_field = test.etsi_smart_card


                
                        # for moves in stock_moves:
                        #     if moves.etsi_serials_field == rec.etsi_serials_field:
                        #         raise ValidationError("Serial is already on another process.")
                        #     else:
                        #         test = database.search([('etsi_serial','=',rec.etsi_serials_field)])
                        #         rec.product_id = test.etsi_product_id.id
                        #         rec.etsi_serials_field = test.etsi_serial
                        #         rec.etsi_mac_field = test.etsi_mac  
                        #         rec.etsi_smart_card_field = test.etsi_smart_card



                        ###############################
                        # else:
                        #     raise ValidationError("Serial is already on another process.")




            elif rec.etsi_mac_field != False:
                if duplicate_count2 < 1:
                    raise ValidationError("Mac not found in the database.")
                else:
                    if search_first2.etsi_status == 'used':
                        raise ValidationError("Mac is already used.")
                    else:

                        stock_moves = self.env['stock.move'].search([('state','not in',['cancel']),('picking_type_id.code','=','internal'),('picking_type_id.return_picking_type_id','!=',False),('issued_field','!=','Return')])


                        if stock_moves:
                            for moves in stock_moves:
                                if moves.etsi_mac_field == rec.etsi_mac_field:
                                    raise ValidationError("Mac is already on another process.")
                                else:
                                    test = database.search([('etsi_mac','=',rec.etsi_mac_field)])
                                    rec.product_id = test.etsi_product_id.id
                                    rec.etsi_serials_field = test.etsi_serial
                                    rec.etsi_mac_field = test.etsi_mac  
                                    rec.etsi_smart_card_field = test.etsi_smart_card
                        else:
                            test = database.search([('etsi_mac','=',rec.etsi_mac_field)])
                            rec.product_id = test.etsi_product_id.id
                            rec.etsi_serials_field = test.etsi_serial
                            rec.etsi_mac_field = test.etsi_mac  
                            rec.etsi_smart_card_field = test.etsi_smart_card





                        

            elif rec.etsi_smart_card_field != False:
                if duplicate_count3 < 1:
                    raise ValidationError("Smart Card not found in the database.")
                else:
                    if search_first3.etsi_status == 'used':
                        raise ValidationError("Smart Card is already used.")
                    else:

                        stock_moves = self.env['stock.move'].search([('state','not in',['cancel']),('picking_type_id.code','=','internal'),('picking_type_id.return_picking_type_id','!=',False),('issued_field','!=','Return')])

                        if stock_moves:
                            for moves in stock_moves:
                                if moves.etsi_smart_card_field == rec.etsi_smart_card_field:
                                    raise ValidationError("Smart card is already on another process.")
                                else:
                                    test = database.search([('etsi_smart_card','=',rec.etsi_smart_card_field)])
                                    rec.product_id = test.etsi_product_id.id
                                    rec.etsi_serials_field = test.etsi_serial
                                    rec.etsi_mac_field = test.etsi_mac  
                                    rec.etsi_smart_card_field = test.etsi_smart_card
                        else:
                            test = database.search([('etsi_smart_card','=',rec.etsi_smart_card_field)])
                            rec.product_id = test.etsi_product_id.id
                            rec.etsi_serials_field = test.etsi_serial
                            rec.etsi_mac_field = test.etsi_mac  
                            rec.etsi_smart_card_field = test.etsi_smart_card

                    

    @api.constrains('etsi_serials_field')
    def testfunc(self):
        for record in self.picking_id.move_lines:
            if record.state == 'done':
                raise ValidationError("You cannot add new item once the record is validated.")

        check5 = self.picking_id.move_lines - self
        for rec2 in check5:
            if self.etsi_serials_field == False:
                print("running")
                pass
            elif rec2.etsi_serials_field == self.etsi_serials_field:
                check6 = "Duplicate detected within the Table \n Serial Number: {}".format(rec2.etsi_serials_field)
                raise ValidationError(check6)
    
    @api.constrains('etsi_mac_field')
    def testfunc2(self):
        for record in self.picking_id.move_lines:
            if record.state == 'done':
                raise ValidationError("You cannot add new item once the record is validated.")

        check5 = self.picking_id.move_lines - self
        for rec2 in check5:
            if self.etsi_mac_field == False:
                print("running")
                pass
            elif rec2.etsi_mac_field == self.etsi_mac_field:
                check6 = "Duplicate detected within the Table \n Mac Number: {}".format(rec2.etsi_serials_field)
                raise ValidationError(check6)
    
    @api.constrains('etsi_smart_card_field')
    def testfunc3(self):
        for record in self.picking_id.move_lines:
            if record.state == 'done':
                raise ValidationError("You cannot add new item once the record is validated.")
                
        check5 = self.picking_id.move_lines - self
        for rec2 in check5:
            if self.etsi_smart_card_field == False:
                print("running")
                pass
            elif rec2.etsi_smart_card_field == self.etsi_smart_card_field:
                check6 = "Duplicate detected within the Table \n Serial Number: {}".format(rec2.etsi_serials_field)
                raise ValidationError(check6)

class Team_issuance_stock_picking(models.Model):
    _inherit = 'stock.picking'


    move_lines = fields.One2many('stock.move', 'picking_id', string="Stock Moves", copy=True)

    # pick_id = fields.Many2one('stock.picking')

    @api.multi
    def process(self):
        self.ensure_one()
        for pack in self.pack_operation_product_ids:
            if pack.product_qty > 0:
                pack.write({'qty_done': pack.product_qty})
            else:
                pack.unlink()
        return 

    @api.multi
    def do_transfer(self):
        res = super(Team_issuance_stock_picking, self).do_transfer()

        for check in self:
            # picking_checker = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
            picking_checker = self.env['stock.picking.type'].search([('code', '=', 'outgoing'),('subscriber_checkbox', '=', True),('return_picking_type_id', '!=', False)])
            if self.picking_type_id.id == picking_checker.id:
                for rec in self.move_lines:
                    if rec.etsi_serials_field != False:
                        status_checker = self.env['etsi.inventory'].search([('etsi_serial', '=', rec.etsi_serials_field)])
                        status_checker.etsi_status = "used"

                        status_checker2 = self.env['stock.move'].search([('etsi_serials_field', '=', rec.etsi_serials_field)])
                        for records in status_checker2:
                                records.issued_field = "Yes"
                                records.subscriber_field = self.partner_id.id
                                records.checker_box = False
                    elif rec.etsi_mac_field != False:
                        status_checker = self.env['etsi.inventory'].search([('etsi_mac', '=', rec.etsi_mac_field)])
                        status_checker.etsi_status = "used"

                        status_checker2 = self.env['stock.move'].search([('etsi_mac_field', '=', rec.etsi_mac_field)])
                        for records in status_checker2:
                                records.issued_field = "Yes"
                                records.subscriber_field = self.partner_id.id
                                records.checker_box = False
                    elif rec.etsi_smart_card_field != False:
                        status_checker = self.env['etsi.inventory'].search([('etsi_smart_card', '=', rec.etsi_smart_card_field)])
                        status_checker.etsi_status = "used"

                        status_checker2 = self.env['stock.move'].search([('etsi_smart_card_field', '=', rec.etsi_smart_card_field)])
                        for records in status_checker2:
                                records.issued_field = "Yes"
                                records.subscriber_field = self.partner_id.id
                                records.checker_box = False
            else:
                pass
        return res