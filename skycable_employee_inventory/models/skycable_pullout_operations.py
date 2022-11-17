from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class Validate_Pullout_Received(models.Model):
    _inherit = 'stock.picking'

    pullout_holder = fields.One2many('pullout_picking_child','pullout_picking_child_connector')
    pullout_holder_return = fields.One2many('pullout_picking_child_return','pullout_picking_child_connector_2')

    # Returned items
    pullout_return_list = fields.One2many('pullout_picking_child_return_list','pullout_return_list_connector')

    # Fields after the delivery 
    employee_for_delivery = fields.Many2one('team.configuration')
    date_delivered = fields.Date(string="Date Returned")
    received_by = fields.Char(string="Received By: ")

    # Count all etsi.inventory.pullouts
    etsi_pullout_count = fields.Integer(compute = '_count_pullouts', string="Pull-Out Counts")

    # Detects what type of serial
    serial_type = fields.Selection([('catv', 'CATV'),('modem', 'Modem')], default='catv')

    # Detects what type of serial
    status_field = fields.Selection([('draft', 'Draft'),('waiting', 'Waiting For Delivery Team'),('done', 'Done')], default='draft')

    # Register the serial to the etsi.inventory 

    # Date can not be set from the past 
    @api.constrains('date_delivered')
    def check_date(self):

        if self.date_delivered == False:
            pass

        if self.date_delivered < fields.Date.today():
            raise ValidationError("The date cannot be set in the past")
    
    def _count_pullouts(self):
        for rec in self:
            rec.etsi_pullout_count = self.env['etsi.pull_out.inventory'].search_count([('etsi_status','in', ('received','delivery'))])

    # all records passed the test, don't return anything

    # Load default values for skycable return 
    @api.model
    def default_get(self, fields):
        res = super(Validate_Pullout_Received, self).default_get(fields)

        return_lines = []
        return_res =self.env['etsi.pull_out.inventory'].search([('etsi_status', 'in', ('received', 'damaged')),('status_field', 'not in', ('waiting', 'done'))])

        res['etsi_pullout_count'] = self.env['etsi.pull_out.inventory'].search_count([('etsi_status','in', ('received','delivery')),('status_field', 'not in', ('waiting', 'done'))])
        

        for item in return_res:

            if item.etsi_status == 'received':

                return_lines.append(( 0,0, {
                    'for_delivery': True,  
                    'job_number' : item.job_number,     
                    'job_number_related' : item.job_number,

                    'product_id' : item.etsi_product_name,
                    'product_id_related' : item.etsi_product_name,

                    'etsi_mac_product': item.etsi_mac,
                    'etsi_serial_product' : item.etsi_serial,
                    'etsi_mac_product' : item.etsi_mac,
                    'etsi_smart_card' : item.etsi_smart_card,
                    'etsi_teams_id' : item.etsi_teams_id,
                    'issued' : item.etsi_status
                    
                }))
        if 'pullout_holder_return' in fields :
            res.update({'pullout_holder_return' : return_lines })
            # res['pullout_return_list'] =  return_lines


                # for laman in return_lines :

                    # print(laman)


        
        return res


    @api.multi
    def do_new_transfer(self):
        
        res = super(Validate_Pullout_Received, self).do_new_transfer()
        for rec in self:
            print(rec.teller)
            print(rec.teller)
            teller = rec.teller
        
        if teller == 'pull-out':

            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            # Code sa pag create
            stock_picking_db = self.env['etsi.pull_out.inventory']

            listahan = []
            for rec in self:
                search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Subscriber Issuance')])
                print(rec.etsi_teams_id)
                
                for x in rec.pullout_holder:
                    listahan.append({

                            'job_number': x.job_number,
                            'etsi_product_name' : x.product_id,
                            'etsi_serial' : x.etsi_serial_product,
                            'etsi_mac': x.etsi_mac_product,
                            'etsi_smart_card': x.etsi_smart_card ,
                            'etsi_employee_in' : 'Administrator',
                            'etsi_teams_id' : rec.etsi_teams_id,
                            'etsi_receive_date_in' : x.comp_date,
                            # 'etsi_punched_date_in' : x.comp_date,
                            # 'etsi_date_returned_in' : x.comp_date,
                            })
                            
            for rec in self:
                employee_id = rec.etsi_teams_id.team_number

            for laman in listahan:
               
                stock_picking_db = self.env['etsi.pull_out.inventory']
                stock_picking_db.create(
                {
                # 'etsi_team_issuance_id': picking.id,
                'job_number' : laman['job_number'], 
                'etsi_product_name' : laman['etsi_product_name'],
                'etsi_serial': laman['etsi_serial'],
                'etsi_mac': laman['etsi_mac'],
                'etsi_smart_card': laman['etsi_smart_card'],
                'etsi_employee_in': laman['etsi_employee_in'],
                'etsi_teams_id' : employee_id,
                'etsi_status': 'received',
                'etsi_receive_date_in': laman['etsi_receive_date_in'],
                # 'etsi_punched_date_in': laman['etsi_punched_date_in'],
                # 'etsi_date_returned_in': laman['etsi_date_returned_in'],     
                    
                }
                )        
                print(laman['etsi_serial'])

            picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Pullout Receive')])
            stock_picking_db = self.env['stock.picking']
            
            self.update({
                    # 'etsi_team_issuance_id': picking.id,
                    'picking_type_id': picking_checker2.id,
                    # 'partner_id': self.skycable_subscriber_id.id,
                    # 'move_lines':listahan_delivery,
                    'location_id': picking_checker2.default_location_src_id.id,
                    'location_dest_id': picking_checker2.default_location_dest_id.id,
                    'etsi_teams_id':  picking.etsi_teams_id.id,
                    'state' : 'done'
                    })

        if teller == 'pull-out-return':

            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            # Code sa pag create
            stock_picking_db = self.env['etsi.pull_out.inventory']

            if rec.pullout_holder_return == False:
                raise ValidationError("Please fill up items to return to sky")

            listahan = []
            for rec in self:
                search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Pullout Return To Sky')])
                print(rec.etsi_teams_id)
                
                for x in rec.pullout_holder_return:
                    listahan.append({

                            'job_number': x.job_number,
                            'etsi_product_name' : x.product_id,
                            'etsi_serial' : x.etsi_serial_product,
                            'etsi_mac': x.etsi_mac_product,
                            'etsi_smart_card': x.etsi_smart_card ,
                            'etsi_employee_in' : 'Administrator',
                            'etsi_teams_id' : rec.etsi_teams_id,
                            'etsi_punched_date_in' : x.comp_date,
                            'etsi_date_returned_in' : x.comp_date,
                
                            })

            picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Pullout Return To Sky')])
            stock_picking_db = self.env['stock.picking']
            self.update({'state' : 'waiting'})
     

        return res

    @api.multi
    def receive_pullout_btn(self):

        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        listahan_delivery = []
        for rec in self:
            if rec.pullout_holder:


                search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Pullout Receive')])
            
                for x in rec.pullout_holder:

                    if x.etsi_mac_product  == False and x.etsi_smart_card == False:

                        raise ValidationError("Please make sure to fill MAC or Smart Card for each lines")
                    else:
                        listahan_delivery.append((
                            0, 0, {
                                'name': x.product_id,
                                'product_id': 1, 
                                'product_uom_qty' : x.product_uom_qty, 
                                # Unit of measure 
                                'product_uom' : x.product_uom.id,
                                'move_id': x.id, 
                                'issued_field': "On Hand",
                                'etsi_serials_field': x.etsi_serial_product, 
                                'etsi_mac_field': x.etsi_mac_product, 
                                'etsi_smart_card_field': x.etsi_smart_card,

                                 # Additional for returned items
                                # 'subscriber' : x.subscriber_field.id,
                                'state' : 'draft',
                                'location_id' : rec.location_id,
                                'location_dest_id' : rec.location_dest_id,
                                'picking_type_id': rec.picking_type_id,
                                'etsi_teams_id' : x.etsi_teams_id
                            }
                            ))
                        
                        
                        for item in listahan_delivery:
                            print(item)
                
               

                # CREATE RECORD
                picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
                # Code sa pag create
                stock_picking_db = self.env['etsi.pull_out.inventory']

                listahan = []
                for rec in self:
                    search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                    picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Pullout Receive')])
                    print(rec.etsi_teams_id)
                    
                    for x in rec.pullout_holder:
                        listahan.append({

                                'job_number': x.job_number,
                                'etsi_product_name' : x.product_id,
                                'etsi_serial' : x.etsi_serial_product,
                                'etsi_mac': x.etsi_mac_product,
                                'etsi_smart_card': x.etsi_smart_card ,
                                'etsi_employee_in' : 'Administrator',
                                'etsi_teams_id' : rec.etsi_teams_id,
                                'etsi_receive_date_in' : x.comp_date,
                                # 'etsi_punched_date_in' : x.comp_date,
                                # 'etsi_date_returned_in' : x.comp_date,
                                'name' : rec.name
                                })
                                
                for rec in self:
                    employee_id = rec.etsi_teams_id.team_number

                for laman in listahan:
                
                    stock_picking_db = self.env['etsi.pull_out.inventory']
                    stock_picking_db.create(
                    {
                    # 'etsi_team_issuance_id': picking.id,
                    'job_number' : laman['job_number'], 
                    'etsi_product_name' : laman['etsi_product_name'],
                    'etsi_serial': laman['etsi_serial'],
                    'etsi_mac': laman['etsi_mac'],
                    'etsi_smart_card': laman['etsi_smart_card'],
                    'etsi_employee_in': laman['etsi_employee_in'],
                    'etsi_teams_id' : employee_id,
                    'etsi_status': 'received',
                    'etsi_receive_date_in': laman['etsi_receive_date_in'],
                    # 'etsi_punched_date_in': laman['etsi_punched_date_in'],
                    # 'etsi_date_returned_in': laman['etsi_date_returned_in'],     
                    'transaction_number' : laman['name']          
                    }
                    )        
                    print(laman['etsi_serial'])
            else:
                raise ValidationError("Please fill up  Items to receive for pull-outs ")
            
        self.update({
                    'state' : 'done',
                    'status_field' : 'done',
                    })
            

    # Smart Button for Pull Outs
    @api.multi
    def get_all_pullouts(self):
        context = dict(self.env.context or {})
        context.update(create=False)
        return {
            'name': 'Subscriber Issuance',
            'res_model': 'etsi.pull_out.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {'create':0},
            # 'domain': [('etsi_team_issuance_id','=',self.id)]
        }
   
    # Button For return to Sky  
    @api.multi
    def receive_delivery_btn(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        listahan = []

        count = 0
        for rec in self:

            for lines in rec.pullout_holder_return:

                if lines.for_delivery == True:
                    count += 1

            if count == 0:
                raise ValidationError("Please select at least one item to return to sky")
            else:
                pass

            search_name = self.env['stock.picking'].search([('name','=',rec.name)])
            picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Pullout Return To Sky')])

           
                    
            picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Pullout Return To Sky')])
            stock_picking_db = self.env['stock.picking']

            product_lists = []
            product_serials = []
            # Update the date of delivery to sky cable of pull outs
            for plines_issued in rec.pullout_holder_return:

                if plines_issued.for_delivery == True:

                    product_lists.append(plines_issued.etsi_serial_product)
                    product_serials.append(plines_issued.etsi_serial_product)

                    issued_stats = self.env['pullout_picking_child_return'].search([])
                    inventory_stats = self.env['etsi.pull_out.inventory'].search([])

                    # To update the status of serials as returned from sky 
                    if product_serials:

                        Date = datetime.today()
                            
                        for searched_ids in inventory_stats:
                            if searched_ids.etsi_serial in product_serials:
                                searched_ids.update({'etsi_status': 'delivery',
                                'etsi_date_issued_in' : Date,
                                'transaction_number' : rec.name,
                                'status_field' : 'waiting',
                                })


            self.update({
                # 'etsi_team_issuance_id': picking.id,
                # 'picking_type_id': picking_checker2.id,
                # # 'partner_id': self.skycable_subscriber_id.id,
                # 'move_lines':listahan,
    
                # 'location_id': picking_checker2.default_location_src_id.id,
                # 'location_dest_id': picking_checker2.default_location_dest_id.id,
                # 'etsi_teams_id':  picking.etsi_teams_id.id,
                'state' : 'draft',
                'status_field' : 'waiting'
                })
    
    # Validation for serial number for broadband within the table
    @api.constrains('pullout_holder')
    @api.onchange('pullout_holder')
    def _check_exist_serial_in_lineasd(self):

        exist_serial_list = []
        exist_mac_list = []
        exist_smart_card_list = []

        for search in self:
            
            for line in search.pullout_holder:
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
                
                if line.etsi_smart_card:
                    if line.etsi_smart_card in exist_smart_card_list:
                        check = "Duplicate detected within the table \n SMART CARD ID : {}".format(line.etsi_smart_card)
                        raise ValidationError(check)
                    exist_smart_card_list.append(line.etsi_smart_card) 

                if  line.etsi_serial_product == line.etsi_mac_product :
                    raise ValidationError(_('Serial ID is the same to MAC ID'))
               
        for fetch_serial_list in exist_serial_list:
            if fetch_serial_list in exist_mac_list:
                check = "Duplicate detected within the table serial and mac id is the same \n : {}".format(fetch_serial_list)
                raise ValidationError(check)
        
        for rec in self:

            for lines in rec.pullout_holder:

                if lines.serial_type == False and lines.etsi_serial_product:
                    
                    if etsi_mac_product or etsi_smart_card == False:
                        raise ValidationError("PLEASE TYPE MAC OR SMART CARD ID")

     # Button For return to Sky  
    @api.multi
    def confirm_delivery_btn(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        listahan = []
        returned_pullouts = []
        for rec in self:

            search_name = self.env['stock.picking'].search([('name','=',rec.name)])
            picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Pullout Receive')])

            product_lists = []
            product_serials = []

           
            # if rec.picking_type_id.name == "Subscriber Return" or rec.picking_type_id.name == "Team Return":
            if rec.employee_for_delivery == False:
                raise ValidationError("Please input the team number for delivery")
            if rec.date_delivered == False:
                raise ValidationError("Please input the date delivered")
            if rec.received_by == False:
                raise ValidationError("Please input who received")
            else:

                for plines_issued in rec.pullout_holder_return:
                    if plines_issued.for_delivery == True:
                        product_lists.append(plines_issued.etsi_serial_product)
                        product_serials.append(plines_issued.etsi_serial_product)

                issued_stats = self.env['pullout_picking_child_return'].search([])
                inventory_stats = self.env['etsi.pull_out.inventory'].search([])

                # To update the status of serials as returned from sky 
                if product_serials:
                    for searched_issueds in issued_stats:
                        if searched_issueds.etsi_serial_product in product_lists:
                            searched_issueds.update({'issued': 'returned'})

                        for searched_ids in inventory_stats:
                            if searched_ids.etsi_serial in product_serials:
                                searched_ids.update({'etsi_status': 'returned',
                                'etsi_date_returned_in' : rec.date_delivered,
                                })

            for x in rec.pullout_holder_return:

                if x.for_delivery == True:

                    returned_pullouts.append((
                        0, 0, {
                            'product_id': x.product_id,
                            'etsi_serial_product': x.etsi_serial_product, 
                            'etsi_mac_product': x.etsi_mac_product, 
                            'etsi_smart_card': x.etsi_smart_card,
                            'comp_date' : x.comp_date,
                            'quantity' : x.product_uom_qty,
                            # Unit of measure 
                            'product_uom' : x.product_uom.id,
                            'product_uom_qty' : x.product_uom_qty, 
                            'issued': "returned",

                            'job_number' : x.job_number,
                            # 'name':x.product_id.product_tmpl_id.name,

                            'move_id': x.id, 
                            'issued_field': "Returned"
                        }
                        ))

        # Finish the form
        self.update({
        'pullout_return_list' : returned_pullouts,
        'state' : 'done',
        'pullout_holder_return' : False,
        'status_field' : 'done'
         })

class Validate_Pullout_Received_Child(models.TransientModel):
    _name = 'pullout_picking_child'
    
    pullout_picking_child_connector = fields.Many2one('stock.picking')
     # Subscriber Form
    job_number = fields.Char("Job Order", required="True")
    subs_type = fields.Char("Type")
    comp_date = fields.Date("Pull Out Date", default=datetime.today(), required="True")
    form_num = fields.Char("Form Number")
    form_type = fields.Selection({
        ('a','Newly Installed'),
        ('b','Immediate')
    })
    serial_type = fields.Selection([('catv', 'CATV'),('modem', 'Modem')], default='catv')
    
    etsi_teams_id = fields.Many2one('team.configuration', string="Team Number")
    product_id =  fields.Char('CPE Mat. Code', required="True") 
    quantity = fields.Float('Quantity')

    issued = fields.Selection([('received', 'On-hand'),('delivery', 'For Delivery'),('returned', 'Delivered')], string="Status", default='received', readonly=True)
    etsi_serial_product = fields.Char(string="Serial ID", required="True")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure', default=1)
    product_uom_qty = fields.Float('Quantity',default=1.0)
    active_name = fields.Char('Active Name')


    # Validation for not both MAC and Serial
    @api.constrains('etsi_serial_product')
    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card', 'serial_type')
    def onchange_transfer_pull_out_receive(self):
        # Validate Datas
        for rec in self:
            default_id = rec.etsi_teams_id

            # Search Count
            pm_search_sr_count = self.env['etsi.pull_out.inventory'].search_count([('etsi_serial','=', rec.etsi_serial_product)])
            # search available products - stock.move model
            pm_search_sr = self.env['etsi.pull_out.inventory'].search([('etsi_serial','=', rec.etsi_serial_product)])
            pm_search_mc = self.env['etsi.pull_out.inventory'].search([('etsi_mac','=', rec.etsi_mac_product)])
            pm_search_sc = self.env['etsi.pull_out.inventory'].search([('etsi_smart_card','=', rec.etsi_smart_card)])
            # Lists
            # search available products - stock.picking.return.list.holder model        
            # Valued data only passes

            if rec.etsi_serial_product != False :
                if  pm_search_sr_count >= 1:
                        raise ValidationError("Serial already exists!")

                if rec.etsi_smart_card and rec.etsi_mac_product :
                    if rec.serial_type == 'catv':
                        self.update({'etsi_mac_product' : False})
                    else:
                        self.update({'etsi_smart_card' : False})

    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def onchange_transfer_pull_out_returnasd(self):
        listahan = []
        # Validate Datas
        for rec in self:
            listahan.append(rec.etsi_serial_product)
        
    # Code for serial type

    @api.multi
    @api.onchange('serial_type')   
    def checker_onchange(self):
        # If transfer checker is checked
        for rec in self:
            search_name = self.env['stock.picking'].search([('name','=', rec.active_ako.name)])

            if search_name:
                print("MERON")
            else:
                print("WALAA")
            
            if rec.serial_type == 'catv':
                self.update({'etsi_mac_product' : False})

            else:
                self.update({'etsi_smart_card' : False})

    
class Validate_Pullout_Received_Child(models.TransientModel):
    _name = 'pullout_picking_child_return'
    
    pullout_picking_child_connector_2 = fields.Many2one('stock.picking')
     # Pull Out Return Form
    for_delivery = fields.Boolean('Delivery')
    job_number = fields.Char("Job Order")
    job_number_related = fields.Char(related="job_number")
    subs_type = fields.Char("Type")
    comp_date = fields.Date("Pull Out Date", default=datetime.today())
    form_num = fields.Char("Form Number")
    form_type = fields.Selection({
        ('a','Newly Installed'),
        ('b','Immediate')
    })

    etsi_teams_id = fields.Char( string="Team Number")
    product_id =  fields.Char('CPE Mat. Code') 
    product_id_related = fields.Char(related='product_id')
    quantity = fields.Float('Quantity')

    issued = fields.Selection([('received', 'On-hand'),('delivery', 'For Delivery'),('returned', 'Delivered')], string="Status", default='delivery', readonly=True)
    etsi_serial_product = fields.Char(string="Serial ID", required="True")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Char("Active Ako ")
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', default= 1)
    product_uom_qty = fields.Float('Quantity',default=1.0)
    active_name = fields.Char('Active Name')

    
    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def onchange_transfer_pull_out_return(self):
        # Validate Datas
        for rec in self:
            default_id = rec.etsi_teams_id
            # search available products - stock.move model
            pm_search_sr = self.env['etsi.pull_out.inventory'].search([('etsi_serial','=', rec.etsi_serial_product)])
            pm_search_mc = self.env['etsi.pull_out.inventory'].search([('etsi_mac','=', rec.etsi_mac_product)])
            pm_search_sc = self.env['etsi.pull_out.inventory'].search([('etsi_smart_card','=', rec.etsi_smart_card)])
            # Lists
            # search available products - stock.picking.return.list.holder model        
            # Valued data only passes
            # if rec.etsi_mac_product == False and rec.etsi_smart_card == False:
            #     raise ValidationError("Please put MAC ID or Smart Card ID")
            if rec.etsi_serial_product != False or rec.etsi_mac_product != False or rec.etsi_smart_card != False:
                
             
                # Check if data inputted is available
                # MAC ID
                # if pm_search_sc:
                #     if rec.etsi_mac_product:
                #         # if p_lists_mc[0] == False:
                #         #     raise ValidationError("This product is CATV, there is no MAC ID!")
                #         # if rec.etsi_mac_product not in p_lists_mc:
                #         #     raise ValidationError("MAC ID not available in returns!")
                #         # # Validation for issued status
                #         for mac in pm_search_mc:

                #         #     if mac.issued_field == "Yes":
                #         #         raise ValidationError("This Product is already issued!")
                #         #     if mac.issued_field == "Return":
                #         #         raise ValidationError("Product is already returned!")
                                
                #             # Auto fill statements
                #             rec.product_id = mac.product_id.id
                #             rec.etsi_serial_product = mac.etsi_serials_field
                #             rec.etsi_smart_card = mac.etsi_smart_card_field
                #             rec.issued = "delivery"
                #             rec.quantity = 1.00
                #             rec.product_uom = 1
                #             rec.etsi_teams_id = default_id 

                #             break
                
                # # Smart Card
                # if pm_search_mc:
                    
                #     if rec.etsi_smart_card:
                #         # if p_lists_sc[0] == False:
                #         #     raise ValidationError("This product is MODEM, there is no Smart Card!")
                #         # if rec.etsi_smart_card not in p_lists_sc:
                #         #     raise ValidationError("Smart Card not available in returns!")
                #         # else:
                #         #     # Validation for issued status
                #         for scard in pm_search_sc:
                #         #         if scard.issued_field == "Yes":
                #         #             raise ValidationError("This Product is already issued!")
                #         #         if scard.issued_field == "Return":
                #         #             raise ValidationError("Product is already returned!")
                                
                #                 # Auto fill statements
                #             rec.product_id = scard.product_id.id
                #             rec.etsi_mac_product = scard.etsi_mac_field
                #             rec.etsi_serial_product = scard.etsi_serials_field
                #             rec.issued = "delivery"
                #             rec.quantity = 1.00
                #             rec.product_uom = 1
                #             rec.etsi_teams_id = default_id 
                #             break
                        
                # Checks if search is true
                if pm_search_sr:

                    if rec.etsi_serial_product:
                        # if rec.etsi_serial_product not in p_lists_sr:
                        #     raise ValidationError("Serial not available in returns!")
                        # else:
                        #     # Validation for issued status
                        for ser in pm_search_sr:
                        
                                if ser.etsi_status == "delivery":
                                    raise ValidationError("This Product is already on delivery!")
                                    rec.product_id = False
                                    rec.etsi_serial_product =  False
                                    rec.etsi_mac_product = False
                                    rec.etsi_smart_card = False
                                    rec.issued = False
                                    rec.quantity = False
                                    rec.product_uom = False

                                if ser.etsi_status == "returned":
                                    raise ValidationError("Product is already returned to Sky!")
                                
                                    # Auto fill statements
                                rec.job_number = ser.job_number
                                rec.product_id = ser.etsi_product_name
                                rec.etsi_mac_product = ser.etsi_mac
                                rec.etsi_smart_card = ser.etsi_smart_card
                  
                                rec.quantity = 1.00

                                # rec.product_uom = 21
                                rec.etsi_teams_id = ser.etsi_teams_id
                                break
                else:
                    raise ValidationError("Serial not found in the database")


class Validate_Pullout_Return_List(models.TransientModel):
    _name = 'pullout_picking_child_return_list'


    pullout_return_list_connector = fields.Many2one('stock.picking')
     # Pull Out Return Form
    for_delivery = fields.Boolean('Delivery')
    job_number = fields.Char("Job Order")
    job_number_related = fields.Char(related="job_number")
    subs_type = fields.Char("Type")
    comp_date = fields.Date("Pull Out Date", default=datetime.today())
    form_num = fields.Char("Form Number")
    form_type = fields.Selection({
        ('a','Newly Installed'),
        ('b','Immediate')
    })

    etsi_teams_id = fields.Char( string="Team Number")
    product_id =  fields.Char('CPE Mat. Code') 
    product_id_related = fields.Char(related='product_id')
    quantity = fields.Float('Quantity')

    issued = fields.Selection([('received', 'On-hand'),('delivery', 'For Delivery'),('returned', 'Delivered'),('damaged', 'Damaged')], string="Status", default='delivery', readonly=True)
    etsi_serial_product = fields.Char(string="Serial ID", required="True")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Char("Active Ako ")
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', default= 1)
    product_uom_qty = fields.Float('Quantity',default=1.0)
    active_name = fields.Char('Active Name')


class Etsi_Pullout_Inventory(models.Model):

    _name = 'etsi.pull_out.inventory'

    @api.multi 
    def _get_count_list(self):
        data_obj = self.env['etsi.pull_out.inventory']
        for data in self:       
            list_data  = data_obj.search([()])
            data.example_count = len(list_data)

            # print(data.example_count)
            # print(data.example_count)
            # print(data.example_count)

    etsi_serial = fields.Char(string="Serial ID")
    etsi_mac = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    etsi_status = fields.Selection([('received', 'Received'),('delivery', 'Delivery'),('returned', 'Returned')], string="Status", default='delivery', readonly=True)

    etsi_product_id = fields.Many2one('product.product',string="Product")
    etsi_product_name = fields.Char(string="Product")

    etsi_teams_id = fields.Char('Team')
    type_checker = fields.Selection(related='etsi_product_id.internal_ref_name')

    etsi_receive_date_in = fields.Date(string="Date Received",default = datetime.today())
    etsi_date_issued_in = fields.Date(string="Date of Delivery" )
    
    etsi_date_returned_in = fields.Date(string="Date Returned")
    etsi_date_received_in = fields.Date(string="Date Issued", default = datetime.today())
  
  
    etsi_team_in = fields.Char(string="Team")
    etsi_punched_date_in = fields.Date("Punch Time", default = datetime.today())
    etsi_employee_in = fields.Char("Employee")

    job_number =  fields.Char('Job Order')

    transaction_number = fields.Char('Transaction Number')

    status_field = fields.Selection([('draft', 'Draft'),('waiting', 'Waiting For Delivery Team'),('done', 'Done')], default='draft')

    # count = fields.Char('Count: ' default=data.example_count)
