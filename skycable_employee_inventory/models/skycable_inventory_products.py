from odoo import api, fields, models, tools, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from collections import Counter 
import pandas as pd

class ProductTemplateInheritance(models.Model):
    _inherit = 'product.template'
    # _rec_name = 'etsi_product_id'

    description_txt = fields.Text(string="Description:")
    # product_type = fields.Selection([('product','Product'),('material','Material')] , default ="product", string ="Product Type:")
    internal_ref_name = fields.Selection([('catv5', 'CATV5'), ('broadband', 'BROADBAND'), ('drops', 'DROPS'), ('others', 'OTHERS')], string = "Internal Reference", default='catv5',required="true")
    
    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True,default='catv5')
    product_count = fields.Integer(compute ='get_product_count')

    #DELETE THIS FIELDS FOR TEST ONLY
    # drops_reference = fields.Char()
    # end of deletion

    drops_reference_id = fields.Many2one('etsi.product.drops.reference')

    @api.onchange('internal_ref_name')
    def product_type_func(self):
        if self.internal_ref_name == 'catv5':
            self.default_code = 'CATV5'
        elif self.internal_ref_name == 'drops':
            self.default_code = 'DROPS'
        elif self.internal_ref_name == 'others':
            self.default_code = 'OTHERS'
        else:
            self.default_code = 'BROADBAND'

    @api.multi
    def serial_location(self):
        if self.internal_ref_name == 'broadband':
            view_id = self.env.ref("skycable_employee_inventory.serials_tree_view_one").id
            view_ids = self.env.ref("skycable_employee_inventory.etsi_inventory_form_02").id
            return {
                'name': 'BROADBAND',
                'type': 'ir.actions.act_window',
                'res_model': 'etsi.inventory',
                'view_mode': 'tree,form',
                'views': [(view_id,'tree'),(view_ids,'form')],
                'domain': [('etsi_product_id', '=', self.name )]
            }
            
        else:
            view_id = self.env.ref("skycable_employee_inventory.serials_tree_view_two").id
            view_ids = self.env.ref("skycable_employee_inventory.etsi_inventory_form_02").id
            return {
                'name': 'CATV5',
                'type': 'ir.actions.act_window',
                'res_model': 'etsi.inventory',
                'view_mode': 'tree,form',
                'views': [(view_id,'tree'),(view_ids,'form')],
                'domain': [('etsi_product_id', '=', self.name )]
            }


    def get_product_count(self):
        for rec in self:
            count = self.env['etsi.inventory'].search_count([('etsi_product_id', '=', rec.name)])
            rec.product_count = count

    def testing121212(self):
        return {

            'name': 'Convert Transient',
            'res_model': 'stock.move.test',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('skycable_employee_inventory.stock_move_test_transient').id,
            'context': {'default_matcode':self.id}
            
            # 'test':self.id
            
        }

    @api.onchange('name')
    def duplicate_name(self):
        for rec in self:
            count = self.env['product.template'].search_count([('name', '=', rec.name)])
            if count >= 1 and rec.internal_ref_name != "drops":
                return {'warning': {'title': _('Warning'),'message': _('Material code already exist in the database.')}}

    @api.constrains('name')
    def duplicate_name_cons(self):
        for rec in self:
            count = self.env['product.template'].search_count([('name', '=', rec.name)])
            if count >= 2 and rec.internal_ref_name != "drops":
                raise ValidationError("Material code already exist in the database.")

    @api.constrains('internal_ref_name')
    def duplicate_name_cons(self):
        for rec in self:
            count = self.env['product.template'].search_count([('name', '=', rec.name)])
            if count >= 2 and rec.internal_ref_name != "drops":
                raise ValidationError("Material code already exist in the database.")

                # return {'warning': {'title': _('Warning'),'message': _('Material code already exist in the database.')}}
        

    


#REFERENCE OF DROPS MANY2ONE
class Product_drops_reference(models.Model):
    _name = 'etsi.product.drops.reference'
    _rec_name = 'drops_references'

    drops_references=fields.Char(string="Drops type")


# serial smart button content
class Product_Serial_SmartButton(models.Model):
    _name = 'etsi.inventory'
    _rec_name = 'etsi_product_id'

    etsi_serial = fields.Char(string="Serial ID")
    etsi_mac = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    etsi_status = fields.Selection([('available', 'Available'),('deployed', 'Deployed'),('used', 'Used'),('returned', 'Returned'),('pending', 'Pending Transfer'),('damaged', 'Damaged'),('onhand', 'On Hand'),('delivery', 'Delivery'),('delivered', 'Delivered')], string="Status", default='available', readonly=True)
    etsi_product_id = fields.Many2one('product.product',string="Product")
    etsi_product_name = fields.Many2one('product.product',string="Product")

    type_checker = fields.Selection(related='etsi_product_id.internal_ref_name')
    type_checker_02 = fields.Selection([('catv5', 'CATV5'), ('broadband', 'BROADBAND'), ('drops', 'DROPS'), ('others', 'OTHERS')])
    etsi_receive_date_in = fields.Date(string="Receive")
    etsi_subscriber_in = fields.Char(string="Subscriber")
    etsi_date_issued_in = fields.Date(string="Date Issued")
    etsi_date_returned_in = fields.Date(string="Date Returned")
    etsi_team_in = fields.Many2one('team.configuration', string="Teams")
    etsi_punched_date_in = fields.Datetime("Punch Time")
    etsi_employee_in = fields.Many2one('res.users',"Employee")
    # ADDING FIELDS FOR DROPS REFERENCE
    etsi_drops_references_in = fields.Char(string="Drop Types")
    
    active = fields.Boolean('Active', default=True)
    
    #ADDING DESCRIPTION FIELD
    etsi_description = fields.Text(related='etsi_product_id.description_txt')

    #history one2many
    etsi_history_lines =  fields.One2many('etsi.inventory.history','etsi_connection')


    #Quantity
    etsi_product_quantity = fields.Integer(string="Quantity")
    
    #product scheduler
    @api.multi
    def product_archive_scheduler(self):
        two_years = datetime.now().date() - timedelta(days=730)
        active_products = self.env['etsi.inventory'].search([('etsi_date_issued_in', '<=', str(two_years))])
        print(active_products)
        for archive_products in active_products:
            archive_products.active = False

# update quantity on hand one2many content

class Product_Serial_SmartButton(models.Model):
    _name = 'etsi.inventory.history'

    etsi_connection = fields.Many2one('etsi.inventory')
    etsi_operation = fields.Char(string="Operation")
    etsi_transaction_description = fields.Char(string="Description")
    etsi_transaction_num = fields.Many2one('stock.picking',string="Transaction Number")
    # etsi_date_issued = fields.Date(string="Date Issued")
    # etsi_date_returned = fields.Date(string="Date Returned")
    etsi_status = fields.Char(string="Status")
    etsi_employee = fields.Many2one('res.users',string="Employee")
    etsi_teams = fields.Many2one('team.configuration',string="Team")
    etsi_action_date = fields.Date(string="Date")
    etsi_history_quantity = fields.Integer(string="Quantity")

class Product_Quanty_On_Hand_Model(models.TransientModel):

    _name = 'etsi.inventory.product'
    _rec_name = 'etsi_product_id_product'


    etsi_serial_product = fields.Char(string="Serial ID", required=True)
    etsi_mac_product = fields.Char(string="MAC ID", required=True)
    etsi_status_product = fields.Selection([('available', 'Available'),('deployed', 'Deployed'),('used', 'Used'),('returned', 'Returned'),('damaged', 'Damaged'),('onhand', 'On Hand'),('delivery', 'Delivery'),('delivered', 'Delivered')], string="Status", default='available', readonly=True)
    etsi_product_id_product = fields.Many2one('stock.change.product.qty')
    etsi_product_name_product = fields.Many2one(related='etsi_product_id_product.product_id',string="Product")
    etsi_quantity = fields.Float(string= "Quantity", readonly=True, default=1)

    etsi_product_type = fields.Selection(related='etsi_product_name_product.internal_ref_name')



    #ADDING NEW FIELDS
    # date_and
    etsi_receive_date = fields.Date(string="Receive", related='etsi_product_id_product.date_time', required=True)
    etsi_subscriber = fields.Char(string="Subscriber")
    etsi_date_issued = fields.Date(string="Date Issued")
    etsi_date_returned = fields.Date(string="Date Returned")
    etsi_team = fields.Char(string="Team")
    etsi_punch_time = fields.Datetime("Punched Time", default=fields.Datetime.now, readonly=True, required=True)

    checkbox_duplicate  = fields.Boolean('Duplicate Products')
  

    @api.onchange('etsi_serial_product')
    def _onchange_etsi_serial_product(self):

        print(list_of_serials)
        print(list_of_macs)
      
        
        for rec in self:
            if rec.etsi_serial_product:
                if rec.etsi_serial_product in list_of_serials:
                    rec.checkbox_duplicate =True
            

    @api.onchange('etsi_mac_product')
    def _onchange_etsi_mac_product(self):
       
        for rec in self:
            if rec.etsi_serial_product:
                if rec.etsi_serial_product in list_of_macs:
                    rec.checkbox_duplicate =True
                    



# Onchange Validation for serial product and mac product
    @api.onchange('etsi_serial_product', 'etsi_mac_product')
    def onchangevalidation(self):


    

        for rec in self:
                
            if self.etsi_serial_product:
                if self.etsi_serial_product in self.env['etsi.inventory'].search([]).mapped('etsi_serial'):
                    
                    check = "Duplicate detected within the database \n Serial Number: {}".format(self.etsi_serial_product)

                    # self.checkbox_duplicate = True

                    raise ValidationError(check)

            if self.etsi_mac_product:
                if self.etsi_mac_product in self.env['etsi.inventory'].search([]).mapped('etsi_mac'):

                    check = "Duplicate detected within the database \n MAC ID: {}".format(self.etsi_mac_product)
                    raise ValidationError(check)

    



class Product_Quanty_On_Hand_Model_2(models.TransientModel):

    _name = 'etsi.inventory.product_2'
    _rec_name = 'etsi_product_id_product_2'


    etsi_serial_product_2 = fields.Char(string="Serial ID", required=True)
    etsi_smart_card_product_2 = fields.Char(string="Smart Card ID", required=True)
    etsi_status_product_2 = fields.Selection([('available', 'Available'),('deployed', 'Deployed'),('used', 'Used'),('returned', 'Returned'),('damaged', 'Damaged'),('onhand', 'On Hand'),('delivery', 'Delivery'),('delivered', 'Delivered')], string="Status", default='available', readonly=True)
    etsi_product_id_product_2 = fields.Many2one('stock.change.product.qty')
    etsi_product_name_product_2 = fields.Many2one(related='etsi_product_id_product_2.product_id',string="Product")
    etsi_quantity_2 = fields.Float(string= "Quantity", readonly=True, default=1)

    etsi_product_type_2 = fields.Selection(related='etsi_product_name_product_2.internal_ref_name')

    #ADDING NEW FIELDS
    etsi_receive_date2 = fields.Date(string="Receive", related='etsi_product_id_product_2.date_time', required="True")
    etsi_subscriber2 = fields.Char(string="Subscriber")
    etsi_date_issued2 = fields.Date(string="Date Issued")
    etsi_date_returned2 = fields.Date(string="Date Returned")
    etsi_team2 = fields.Char(string="Team")
    etsi_punch_time_2 = fields.Datetime("Punched Time", default=fields.Datetime.now, readonly=True, required=True)
    checkbox_duplicate_2  = fields.Boolean('Duplicate Products')


    @api.onchange('etsi_serial_product_2')
    def _onchange_etsi_serial_product_2(self):
        print(list_of_serials_2)
        print(list_of_serials_2)
        print(list_of_serials_2)
        print(list_of_serials_2)
        print(list_of_serials_2)


        for rec in self:
            if rec.etsi_serial_product_2:
                if rec.etsi_serial_product_2 in list_of_serials_2:
                    rec.checkbox_duplicate_2 = True

    @api.onchange('etsi_smart_card_product_2')
    def _onchange_etsi_smart_card_product_2(self):

        print(list_of_smart_card_2)
        print(list_of_smart_card_2)
        print(list_of_smart_card_2)
        print(list_of_smart_card_2)

        for rec in self:
            if rec.etsi_smart_card_product_2:
                if rec.etsi_smart_card_product_2 in list_of_smart_card_2:
                    rec.checkbox_duplicate_2 = True
    

    

 # Onchange Validation for serial product2 and smart card2
    @api.onchange('etsi_serial_product_2', 'etsi_smart_card_product_2')
    def onchangevalidation_2s(self):

        for rec in self:

            if self.etsi_serial_product_2:

                if self.etsi_serial_product_2 in self.env['etsi.inventory'].search([]).mapped('etsi_serial'):

                    check = "Duplicate detected within the database \n Serial Number: {}".format(self.etsi_serial_product_2)
                    raise ValidationError(check)

            if self.etsi_smart_card_product_2:   
                if self.etsi_smart_card_product_2 in self.env['etsi.inventory'].search([]).mapped('etsi_smart_card'):

                    check = "Duplicate detected within the database \n Smart Card ID: {}".format(self.etsi_smart_card_product_2)
                    raise ValidationError(check)




class Inherit_Product_Quantity(models.TransientModel):

    _inherit='stock.change.product.qty'

    etsi_product_items = fields.One2many('etsi.inventory.product', 'etsi_product_id_product')
    etsi_product_items_2 = fields.One2many('etsi.inventory.product_2', 'etsi_product_id_product_2')
    new_quantity2 = fields.Float(string='New Quantity on Hand' , related='new_quantity')

    internal_ref_name_2 = fields.Selection(related='product_id.internal_ref_name', string = "Internal Reference")
    employee_name = fields.Many2one('res.users', string='Employee Name', default=lambda self: self.env.user.id)
    date_time = fields.Date(string="Date Received",required="True", default=fields.Datetime.now)
    
    


#currently testing the ui
    @api.onchange('etsi_product_items_2')
    def _onchange_etsi_product_items_2(self):


        #DO NOT USE THESE GLOBAL VARIABLE TO OTHER CLASSES AND PACKAGES: @mr.robot
        global list_of_serials_2
        global list_of_smart_card_2

        list_of_serials_2 =[]
        list_of_smart_card_2 = []
        for rec in self:
            for line in rec.etsi_product_items_2:
                if not line.etsi_serial_product_2 == False:
                    list_of_serials_2.append(line.etsi_serial_product_2)
                if not line.etsi_smart_card_product_2 == False:
                    list_of_smart_card_2.append(line.etsi_smart_card_product_2)

        # df_serials = pd.DataFrame(list_of_serials)
        # df_smart_card = pd.DataFrame(list_of_smart_card)

        # duplicate_serials = df_serials[df_serials.duplicated()]
        # duplicate_smart_card = df_smart_card[df_smart_card.duplicated()]
        # global list_of_serials


        # if not duplicate_serials.empty:

            #  return {'warning': {'title': _('Warning'),'message': _('Duplicate Serials Detected within the table.')}}
        # if not duplicate_smart_card.empty:
        #      return {'warning': {'title': _('Warning'),'message': _('Duplicate Smart Card Detected within the table.')}}



    # duplicated in BROADBAND ON CHANGE
    @api.onchange('etsi_product_items')
    def _onchange_etsi_product_items(self):
        
        #DO NOT USE THESE GLOBAL VARIABLE TO OTHER CLASSES AND PACKAGES: @mr.robot
        global list_of_serials
        global list_of_macs

        list_of_serials =[]
        list_of_macs = []


        for rec in self:
            for line in rec.etsi_product_items:
                if not line.etsi_serial_product == False:
                    list_of_serials.append(line.etsi_serial_product)
                if not line.etsi_mac_product == False:
                    list_of_macs.append(line.etsi_mac_product)



        # df_serials = pd.DataFrame(list_of_serials)
        # df_macs = pd.DataFrame(list_of_macs)

        # duplicate_serials = df_serials[df_serials.duplicated()]
        # duplicate_macs = df_macs[df_macs.duplicated()]


        # if not duplicate_serials.empty:
        #     return {'warning': {'title': _('Warning'),'message': _('Duplicate Serials Detected within the table.')}}
        # if not duplicate_macs.empty:
        #     return {'warning': {'title': _('Warning'),'message': _('Duplicate Mac Address Detected within the table.')}}

# Validation for serial number for broadband within the table
    @api.constrains('etsi_product_items')
    def _check_exist_serial_in_line(self):

        exist_serial_list = []
        exist_mac_list = []
        for search in self:
            
            for line in search.etsi_product_items:
                if line.etsi_serial_product == False:
                    raise ValidationError(_('Serial ID can not be blank'))
                if line.etsi_serial_product:
                    
                    if line.etsi_serial_product in exist_serial_list:
                        check = "Duplicate detected within the table \n Serial Number: {}".format(line.etsi_serial_product)
                        raise ValidationError(check)
                        # Raise Validation Error
                    exist_serial_list.append(line.etsi_serial_product)
            
                if line.etsi_mac_product:
                    if line.etsi_mac_product == False:
                        pass
                    elif line.etsi_mac_product in exist_mac_list:
                        check = "Duplicate detected within the table \n MAC ID : {}".format(line.etsi_mac_product)
                        raise ValidationError(check)
                    exist_mac_list.append(line.etsi_mac_product)

                if  line.etsi_serial_product == line.etsi_mac_product :
                    raise ValidationError(_('Serial ID is the same to MAC ID'))
                    
        for fetch_serial_list in exist_serial_list:
            if fetch_serial_list in exist_mac_list:
                check = "Duplicate detected within the table serial and mac id is the same \n : {}".format(fetch_serial_list)
                raise ValidationError(check)
                   
  

# Validation for Catv type
  
    @api.constrains('etsi_product_items_2')
    def _check_exist_serial_in_line_catv(self):
        exist_serial_list = []
        exist_smart_card_list = []
        for search in self:

            for line in search.etsi_product_items_2:
                if line.etsi_serial_product_2 == False:
                    raise ValidationError(_('Serial ID can not be blank'))
                if line.etsi_serial_product_2:
                    if line.etsi_serial_product_2 in exist_serial_list:
                        check = "Duplicate detected within the table : {}".format(line.etsi_serial_product_2)
                        raise ValidationError(check)
                    exist_serial_list.append(line.etsi_serial_product_2)
                if line.etsi_smart_card_product_2:
                    if line.etsi_smart_card_product_2 in exist_smart_card_list:
                        check = "Duplicate detected within the table : {}".format(line.etsi_smart_card_product_2)
                        raise ValidationError(check)
                    exist_smart_card_list.append(line.etsi_smart_card_product_2) 
                    
        for fetch_serial_list in exist_serial_list:
            if fetch_serial_list in exist_smart_card_list:
                check = "Duplicate detected within the table serial and smart card id is the same \n : {}".format(fetch_serial_list)
                raise ValidationError(check)

# Database validation for serial number for catv5
    @api.constrains('etsi_product_items')
    def check_existing_serial_broadband(self):
        serials = []
        mac = []
        search_serials = self.env['etsi.inventory'].search([]).mapped('etsi_serial')
        search_mac = self.env['etsi.inventory'].search([]).mapped('etsi_mac')
        for rec_serial in search_serials:
            serials.append(rec_serial)
        for rec_map in search_mac: 
            mac.append(rec_map)
        for line in self.etsi_product_items:
            if line.etsi_serial_product:
                if line.etsi_serial_product in serials:
                    check = "Duplicate detected within the database \n Serial Number: {}".format(fetch_serial_list)

        for line in self.etsi_product_items:
            if line.etsi_mac_product:
                if line.etsi_mac_product in mac:
                    check = "Duplicate detected within the database \n  MAC ID: {}".format(line.etsi_mac_product)
                    raise ValidationError(check)

# Validation for serial number for catv5
    @api.constrains('etsi_product_items_2')
    def check_existing_serial_catv(self):
        serials_2 = []
        smart_card = []
        search_serials_2 = self.env['etsi.inventory'].search([]).mapped('etsi_serial')
        search_etsi_smart_card = self.env['etsi.inventory'].search([]).mapped('etsi_smart_card')
        for rec_serial in search_serials_2:
            serials_2.append(rec_serial)
            for rec_smart_card in search_etsi_smart_card: 
                smart_card.append(rec_smart_card)
        for line_2 in self.etsi_product_items_2:
            if line_2.etsi_serial_product_2:
                if line_2.etsi_serial_product_2 in serials_2:
                    check = "Duplicate detected within the database \n Serial Number: {}".format(fetch_serial_list)
                    raise ValidationError(check)
            if line_2.etsi_smart_card_product_2:
                if line_2.etsi_smart_card_product_2 == False:
                    pass
                elif line_2.etsi_smart_card_product_2 in smart_card:
                    check = "Duplicate detected within the database \n Smart Card: {}".format(line_2.etsi_smart_card_product_2)
                    raise ValidationError(check)

    # @api.onchange('etsi_product_items')
    # def update_product_qty1(self):
    #     count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])
        
    #     product = self.env['product.product'].browse(self.product_id.id)
    #     warehouse1_quantity = product.with_context({'location' : 'WH/Stock'}).qty_available
        
    #     self.new_quantity = warehouse1_quantity
    #     self.new_quantity2 = warehouse1_quantity

    #     for record in self.etsi_product_items:
    #         self.new_quantity += record.etsi_quantity
    #         self.new_quantity2 = self.new_quantity 

    # @api.onchange('etsi_product_items_2')
    # def update_product_qty2(self):
    #     count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])

    #     product = self.env['product.product'].browse(self.product_id.id)
    #     warehouse1_quantity = product.with_context({'location' : 'WH/Stock'}).qty_available

    #     self.new_quantity = warehouse1_quantity
    #     self.new_quantity2 = warehouse1_quantity

    #     for record in self.etsi_product_items_2:
    #         self.new_quantity += record.etsi_quantity_2
    #         self.new_quantity2 = self.new_quantity 

    @api.onchange('etsi_product_items')
    def update_product_qty1(self):
        count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])
        
        product = self.env['product.product'].browse(self.product_id.id)
        warehouse1_quantity = product.with_context({'location' : 'WH/Stock'}).qty_available
        
        self.new_quantity = warehouse1_quantity
        # self.new_quantity2 = warehouse1_quantity
        qty_count = 0

        for record in self.etsi_product_items:
            qty_count += record.etsi_quantity
            self.new_quantity2 = qty_count
        self.new_quantity = self.new_quantity + qty_count

    @api.onchange('etsi_product_items_2')
    def update_product_qty2(self):
        count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])

        product = self.env['product.product'].browse(self.product_id.id)
        warehouse1_quantity = product.with_context({'location' : 'WH/Stock'}).qty_available

        self.new_quantity = warehouse1_quantity
        # self.new_quantity2 = warehouse1_quantity
        qty_count = 0

        for record in self.etsi_product_items_2:
            qty_count += record.etsi_quantity_2
            self.new_quantity2 = qty_count
        self.new_quantity = self.new_quantity + qty_count



    # def update_product_qty3(self):
    #     if self.internal_ref_name_2 =='broadband':
    #         count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])
    #         self.new_quantity = len(count)
    #         self.new_quantity2 = len(count)

    #         for record in self.etsi_product_items:
    #             self.new_quantity += record.etsi_quantity
    #             self.new_quantity2 = self.new_quantity 
    #     else:
    #         count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])
    #         self.new_quantity = len(count)
    #         self.new_quantity2 = len(count)

    #         for record in self.etsi_product_items_2:
    #             self.new_quantity += record.etsi_quantity_2
    #             self.new_quantity2 = self.new_quantity 

    @api.multi
    def change_product_qty(self):
        if self.internal_ref_name_2 == 'DROPS' or self.internal_ref_name_2 == 'OTHERS':
            pass
        else:
            """ Changes the Product Quantity by making a Physical Inventory. """
            Inventory = self.env['stock.inventory']
            for wizard in self:
                product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
                line_data = wizard._prepare_inventory_line()
                # line_data2 = wizard._prepare_product_line()
                
               
                

                lst = []
                for line in self.etsi_product_items:
                    res = {
                        'etsi_serials': line.etsi_serial_product,
                        'etsi_macs': line.etsi_mac_product,
                        'etsi_products': line.etsi_product_name_product.id,
                       
                        'sky_receive_date': line.etsi_receive_date,
                        'sky_time_punch': line.etsi_punch_time,
                        'sky_subscriber': line.etsi_subscriber,
                        'sky_date_issued':line.etsi_date_issued,
                        'sky_date_returned': line.etsi_date_returned,
                        'sky_team': line.etsi_team,

                    }
                    lst.append(res)

                lst2 = []    
                for line in self.etsi_product_items_2:
                    res = {
                        'etsi_serials_2': line.etsi_serial_product_2,
                        'etsi_smart_card_2': line.etsi_smart_card_product_2,
                        'etsi_products_2': line.etsi_product_name_product_2.id,
                        
                        'sky_receive_date_2': line.etsi_receive_date2,
                        'sky_time_punch_2': line.etsi_punch_time_2,
                        'sky_subscriber_2': line.etsi_subscriber2,
                        'sky_date_issued_2':line.etsi_date_issued2,
                        'sky_date_returned_2': line.etsi_date_returned2,
                        'sky_team_2': line.etsi_team2,
                    }
                    lst2.append(res)
                new_lst = []
                for x in lst:
                    new_lst.append((0, 0, x))

                new_lst2 = []
                for x in lst2:
                    new_lst2.append((0, 0, x))




                if wizard.product_id.id and wizard.lot_id.id:
                    inventory_filter = 'none'
                elif wizard.product_id.id:
                    inventory_filter = 'product'
                else:
                    inventory_filter = 'none'
                inventory = Inventory.create({
                    'name': _('INV: %s') % tools.ustr(wizard.product_id.name),
                    'filter': inventory_filter,
                    'product_id': wizard.product_id.id,
                    'location_id': wizard.location_id.id,
                    'lot_id': wizard.lot_id.id,
                    'line_ids': [(0, 0, line_data)],
                    'etsi_product_detail': new_lst,
                    'etsi_product_detail_2': new_lst2,
                    'employee_name_inv': self.employee_name.id,
                    'receive_date_inv': self.date_time,
                })

                inventory.action_done()
                for line in self.etsi_product_items:
                    status_checker = self.env['etsi.inventory'].search([('etsi_serial', '=', line.etsi_serial_product)])
                    status_checker.write({'etsi_history_lines': [(0,0, {'etsi_history_quantity':1,'etsi_operation':'Product Module','etsi_transaction_description':'Serial Added','etsi_action_date':line.etsi_punch_time,'etsi_status':'Available','etsi_employee':self.employee_name.id})]})

                for line in self.etsi_product_items_2:
                    status_checker = self.env['etsi.inventory'].search([('etsi_serial', '=', line.etsi_serial_product_2)])
                    status_checker.write({'etsi_history_lines': [(0,0, {'etsi_history_quantity':1,'etsi_operation':'Product Module','etsi_transaction_description':'Serial Added','etsi_action_date':line.etsi_punch_time_2,'etsi_status':'Available','etsi_employee':self.employee_name.id})]})

                
                

            
                
        return {'type': 'ir.actions.act_window_close'}

 

    @api.multi
    def _prepare_inventory_line(self):
        product = self.product_id.with_context(location=self.location_id.id, lot_id=self.lot_id.id)
        th_qty = product.qty_available

        res = {
               'product_qty': self.new_quantity,
               'location_id': self.location_id.id,
               'product_id': self.product_id.id,
               'product_uom_id': self.product_id.uom_id.id,
               'theoretical_qty': th_qty,
               'prod_lot_id': self.lot_id.id,
        }
        return res

    # @api.multi
    # def _prepare_product_line(self):

    #     lst = []
    #     for line in self.etsi_product_items:
    #         res = {
    #             'etsi_serials': line.etsi_serial_product,
    #             'etsi_macs': line.etsi_mac_product,
    #             'etsi_products': line.etsi_product_name_product.id
    #         }
    #         lst.append(res[line])
    #     return lst

    # @api.multi
    # def change_product_qty(self):

    #     for line in self.etsi_product_items:
    #             self.env['etsi.product.detail.line'].create(
    #                 {'etsi_serials': line.etsi_serial_product,
    #                 'etsi_macs':line.etsi_mac_product,
    #                 'etsi_products':line.etsi_product_name_product.id
    #                 })

    #     res = super(Inherit_Product_Quantity, self).change_product_qty()
    #     return res

