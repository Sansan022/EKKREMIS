from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class Validate_Subscriber_Issuance(models.Model):
    _inherit = 'stock.picking'
    
    # Subscriber Issuance Form Field
    job_number = fields.Char("Job Order")
    subs_type = fields.Char("Type")
    comp_date = fields.Date("Completion Date", default=datetime.today())
    form_num = fields.Text("Form Number")
    form_type = fields.Selection({
        ('a','Newly Installed'),
        ('b','Immediate')
    })
    # One2many for items that will be issued 
    subs_issue = fields.One2many('subscriber_issuance_child','subs_issuance_connector')

    @api.multi
    def sub_btn(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))

        subs_list = []
        for rec in self:
            search_name = self.env['stock.picking'].search([('name','=',rec.name)])
            picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Subscriber Issuance')])

            for x in rec.subs_issue:

                subs_list.append((
                    0, 0, {
                        'name':x.product_id.product_tmpl_id.name,
                        'product_id': x.product_id_related.id, 
                        'product_uom_qty' : x.product_uom_qty, 
                        'product_uom' : x.product_uom_related.id, # Unit of measure 
                        'move_id': x.id, 
                        'issued_field': "Used",
                        'etsi_serials_field': x.etsi_serial_product, 
                        'etsi_mac_field': x.etsi_mac_product, 
                        'etsi_smart_card_field': x.etsi_smart_card,
                        'state' : 'draft',
                        'location_id' : rec.location_id,
                        'location_dest_id' : rec.location_dest_id,
                        'picking_type_id': rec.picking_type_id
                    }
                    ))
                
        picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
        stock_picking_db = self.env['stock.picking']

        self.update({
            'move_lines':subs_list,
            'status_field' : 'done',
        })
        
        product_lists = []
        product_serials = []

        product_serials_issued= []
        product_lists_issued = []

        final= []
        final_ids = []

        for rec in self:
            # if rec.picking_type_id.name == "Subscriber Return" or rec.picking_type_id.name == "Team Return":
            for plines_issued in rec.subs_issue:
                product_serials_issued.append(plines_issued.etsi_serial_product)
                product_lists_issued.append(plines_issued.product_id)

        for item in  product_serials_issued:
            final.append(item)

        for items_ids in product_lists_issued:
            final_ids.append(items_ids.id)

        issued_stats = self.env['stock.move'].search([])
        inventory_stats = self.env['etsi.inventory'].search([])

        if final and final_ids:
            for issued_ids in issued_stats:
                if issued_ids.etsi_serials_field in final:
                    issued_ids.update({'issued_field': 'Used'})

                    for searched_ids in inventory_stats:
                        if searched_ids.etsi_product_id.id in final_ids:
                            if searched_ids.etsi_serial in final:
                                searched_ids.update({'etsi_status': 'used'})

    # Validation for serial number within the table 
    @api.constrains('subs_issue')
    @api.onchange('subs_issue')
    def _check_exist_serial_in_line_subs(self):

        exist_serial_list = []
        exist_mac_list = []
        exist_smart_card_list = []

        count = 0
        for search in self:
            
            for line in search.subs_issue:
                if line.etsi_serial_product == False:
                    raise ValidationError(_('Serial ID can not be blank'))
                if line.etsi_serial_product:
                    
                    if line.etsi_serial_product in exist_serial_list:
                        check = "Duplicate detected within the table \n Serial Number: {}".format(line.etsi_serial_product)
                        raise ValidationError(check)
                        # Raise Validation Error
                    exist_serial_list.append(line.etsi_serial_product)


    @api.multi
    def do_new_transfer(self):

        if self.teller == 'subscriber':
            subs_list = []
            for rec in self:
                search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=','Subscriber Issuance')])

                for x in rec.subs_issue:
                    print(x.etsi_serial_product, "APPENDDDD")
                    subs_list.append((
                        0, 0, {
                            'name':x.product_id.product_tmpl_id.name,
                            'product_id': x.product_id_related.id, 
                            'product_uom_qty' : x.product_uom_qty, 
                            'product_uom' : x.product_uom_related.id, # Unit of measure 
                            'move_id': x.id, 
                            'issued_field': "Used",
                            'etsi_serials_field': x.etsi_serial_product, 
                            'etsi_mac_field': x.etsi_mac_product, 
                            'etsi_smart_card_field': x.etsi_smart_card,
                            'state' : 'draft',
                            'location_id' : rec.location_id,
                            'location_dest_id' : rec.location_dest_id,
                            'picking_type_id': rec.picking_type_id
                        }))
                        
            self.update({
                'move_lines': subs_list,
                'status_field' : 'done',
            })

        # Code for updating the status of products as issued 
        res = super(Validate_Subscriber_Issuance, self).do_new_transfer()

        for rec in self:
            if rec.teller == 'subscriber':
                picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))

                search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Subscriber Issuance')])
                picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
                stock_picking_db = self.search([])

                self.update({
                    'state' : 'done'
                })
                
                # list To Update the status 
                count = 0
                counter = []
                product_lists = []
                product_serials = []
                product_serials_issued= []
                product_lists_issued = []
                serial_trans = []
                serial_store = []
                final= []
                final_info = []
                final_ids = []

                # if rec.picking_type_id.name == "Subscriber Return" or rec.picking_type_id.name == "Team Return":
                for plines_issued in rec.subs_issue:
                    product_serials_issued.append(plines_issued.etsi_serial_product)
                    product_lists_issued.append(plines_issued.product_id)

                for item in product_serials_issued:
                    final.append(item)

                for items_ids in product_lists_issued:
                    final_ids.append(items_ids.id)

                issued_stats = self.env['stock.move'].search([('issued_field','=','Deployed')])
                inventory_stats = self.env['etsi.inventory'].search([])
                trans_float_data = self.env['stock.transfer.team.return'].search([])
                
                if final and final_ids:
                    for plines_issued in rec.subs_issue:
                        trans_float_data2 = self.env['stock.transfer.team.return'].search([('etsi_serial_product','=', plines_issued.etsi_serial_product)]) # fetch temp data
                        serial_store.append(plines_issued.etsi_serial_product) # store serials for validation
                        
                        for trans in trans_float_data2:
                            if trans and plines_issued.trans_checker: # get true data only and transfered items only
                                invento = self.env['etsi.inventory'].search([('etsi_serial','=', plines_issued.etsi_serial_product)], limit=1)
                                
                                serial_trans.append(trans.etsi_serial_product) # store serial in 
                                
                                if invento.etsi_team_in.id == plines_issued.teams_to.id: # check if 'teams_from' and 'teams_to' are the same 
                                    raise UserError("'Teams from' and 'Teams to' cannot be the same!")
                                
                                # check if already installed
                                elif trans.installed and trans.return_checker and trans.issued == 'Waiting' and trans.transfer_checker == False: 
                                    raise UserError("This serial is already used, Please wait the other team for transfer slip (confirmation)!")
                                
                                elif trans.team_num_to.id != plines_issued.teams_to.id: # if teams_to and team_num_to not the same
                                    raise UserError("The 'Teams to' are not the same as the team that returned the item.")
                                
                                # check if installed item is available in transfer
                                elif trans.etsi_serial_product in final and trans.issued == 'Waiting' and trans.transfer_checker == True and trans.return_checker == False:
                                    trans.update({ # Update existing floatong data
                                        'issued': "Done",
                                        'return_checker': True,
                                        'installed': True,
                                    })
                                                                           
                        # if temp database has no value and serial does not exist
                        if not trans_float_data or plines_issued.etsi_serial_product not in serial_trans:
                            if plines_issued.trans_checker: # if product recipient is early to arrived in warehouse
                                invento = self.env['etsi.inventory'].search([('etsi_serial','=', plines_issued.etsi_serial_product)], limit=1)
                                
                                if invento.etsi_team_in.id == plines_issued.teams_to.id: # check if 'teams_from' and 'teams_to' are the same 
                                    raise UserError("'Teams from' and 'Teams to' cannot be the same!")
                                
                                return_transfer = self.env['stock.transfer.team.return'].create({ # Create data for transfer items
                                    'product_id': plines_issued.product_id.id,
                                    'quantity': 1.0,
                                    'issued': "Waiting",
                                    'etsi_serial_product': plines_issued.etsi_serial_product,
                                    'etsi_mac_product':  plines_issued.etsi_mac_product,
                                    'etsi_smart_card':  plines_issued.etsi_smart_card,
                                    'team_num_from': invento.etsi_team_in.id,
                                    'team_num_to': plines_issued.teams_to.id,
                                    'transfer_checker': False,
                                    'return_checker': True,
                                    'installed': True,
                                })
                                
                            else: # check if serial is available on transfer lists
                                trans = self.env['stock.transfer.team.return'].search([('etsi_serial_product','=', plines_issued.etsi_serial_product)], limit=1)
                                
                                # Validation for unchecked transfered
                                if trans.issued == "Waiting" and trans.transfer_checker == True and trans.return_checker == False: # check if serial is available on transfer lists
                                    raise UserError("This process cannot be proceeded, because this serial is available on the transfer list. Please confirm first by checking 'transfered' checkbox")
                                elif trans.installed and trans.return_checker and trans.issued == 'Waiting' and trans.transfer_checker == False: # check if already installed
                                    raise UserError("This serial is already used, Please wait the other team for transfer slip (confirmation)!")
                            
                            # # update stock move    
                            # for issued_ids in issued_stats:
                            #     if issued_ids.etsi_serials_field in final:
                            #         count += 1
                            #         counter.append(issued_ids.id) # store ids for validation
                            #         if count == 1:
                            #             print("USEEEEED PRODUCT 1")
                            #             print(max(counter), "COUNTEEEER")
                            #             issued_ids.update({'issued_field': 'Used'})

                            # update etsi inventory
                            for searched_ids in inventory_stats:
                                if searched_ids.etsi_product_id.id in final_ids:
                                    if searched_ids.etsi_serial in final:
                                        searched_ids.update({'etsi_status': 'used'})
                                        
                        # If transfer transaction is finished / confirmed update product location
                        for list_trans in trans_float_data:
                            # Check if the floating data is ready - to update the product list on team issuance (Product reciever)
                            if list_trans.etsi_serial_product in serial_store and list_trans.issued == "Done" and list_trans.return_checker == True and list_trans.transfer_checker == True and list_trans.installed == True:
                                final_info.append({
                                    'serial': list_trans.etsi_serial_product,
                                    'source': list_trans.source.id,
                                    'team_to': list_trans.team_num_to.id
                                })
                        
                        # Update record of product recipient's team issuance
                        for fin in final_info:
                            trans_move = self.env['stock.move'].search([('etsi_serials_field', '=', fin['serial']), ('issued_field','=','Deployed')])
                            
                            for move in trans_move: # update stock.move
                                if move.etsi_serials_field: # get true data
                                    count += 1
                                    counter.append(move.id) # store ids for validation
                                    
                                    if count == 1: # ensure 1 data only
                                        move.update({'picking_id': fin['source']}) # Replace team_issuance ref number
                                        move.update({'issued_field': 'Used'}) # Update product status - to available
                                            
                            for inventory in inventory_stats: # update etsi.inventory - team number
                                if inventory.etsi_serial == fin['serial']:
                                    inventory.update({'etsi_team_in': fin['team_to']}) # update team_number
                                    inventory.update({'etsi_status': 'used'}) # update product status 
                        
                        # Delete done transactions
                        for list_trans in trans_float_data:
                            # Check if the floating data is ready - to update the product list on team issuance (Product reciever)
                            if list_trans.etsi_serial_product in serial_store and list_trans.issued == "Done" and list_trans.return_checker == True and list_trans.transfer_checker == True and list_trans.installed == True:
                                list_trans.unlink() # Delete floating data
        return res

    # Code for checking what form the user is currently in
    @api.model
    def default_get(self, fields):
        res = super(Validate_Subscriber_Issuance, self).default_get(fields)

        data_obj = self.env['stock.picking']
        for data in self:       
            list_data = data_obj.search([()])
            data.etsi_subscriber_issuance = len(list_data)  

        if 'picking_type_id' in res:
            picking_type_id = res['picking_type_id']
            
            self.env['hr.employee.category'].search([ ('default_emp_category', '=', True)]).ids

            search = self.search([('picking_type_id','=', picking_type_id)], limit=1)
            names = self.env['hr.employee.category'].search([ ('default_emp_category', '=', True)]).name

            pm_search_sr = self.env['stock.picking.type'].search([('id','=', picking_type_id)])
            
            data_obj    = self.env['stock.picking']
            for data in self:       
                list_data   = data_obj.search([])
                data.example_count = len(list_data)

            if pm_search_sr.name == 'Subscriber Issuance':
                res['teller'] = 'subscriber'
            if pm_search_sr.name == 'Team Issuance':
                res['teller'] = 'others'
            if pm_search_sr.name == 'Team Return':
                res['teller'] = 'return'
            if pm_search_sr.name == 'Damage Location':
                res['teller'] = 'damage'
            if pm_search_sr.name == 'Pullout Receive':
                res['teller'] = 'pull-out'
            if pm_search_sr.name == 'Pullout Return To Sky':
                res['teller'] = 'pull-out-return'
        return res

   

class Validate_Subscriber_Issuance_Child(models.TransientModel):
    _name = 'subscriber_issuance_child'

    subs_issuance_connector = fields.Many2one('stock.picking')
     # Subscriber Form
    job_number = fields.Char("Job Order")
    subs_type = fields.Char("Type")
    comp_date = fields.Date("Completion Date", default=datetime.today())
    form_num = fields.Char("Form Number")
    form_type = fields.Selection({
        ('a','Newly Installed'),
        ('b','Immediate')
    })
    product_id =  fields.Many2one('product.product', required="True") 
    product_id_related =  fields.Many2one('product.product', related="product_id") 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Status",default="Used")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_mac_product_related = fields.Char(related="etsi_mac_product")
    etsi_smart_card = fields.Char(string="Smart Card")
    etsi_smart_card_related =  fields.Char(related='etsi_smart_card')
    active_ako = fields.Char("Active Ako ")
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure')
    product_uom_related = fields.Many2one(
        'product.uom', related="product_uom")
    product_uom_qty = fields.Float('Quantity',default=1.0)
    active_name = fields.Char('Active Name')
    trans_checker = fields.Boolean("Transfered")
    teams_to = fields.Many2one('team.configuration', string="Team to")

    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def onchange_transfer(self):
        # Validate Datas

        recommend = []
        for rec in self:
            # search available products - stock.move model
            pm_search_sr = self.env['stock.move'].search([('etsi_serials_field','=', rec.etsi_serial_product)])
            pm_search_mc = self.env['stock.move'].search([('etsi_mac_field','=', rec.etsi_mac_product)])
            pm_search_sc = self.env['stock.move'].search([('etsi_smart_card_field','=', rec.etsi_smart_card)])
            # Lists
            # search available products - stock.picking.return.list.holder model        
            # Valued data only passes
            if rec.etsi_serial_product != False or rec.etsi_mac_product != False or rec.etsi_smart_card != False:
                # Check if data inputted is available
                # MAC ID
                if rec.etsi_mac_product:
                    # Validation for issued status
                    for mac in pm_search_mc:
                        # Auto fill statements
                        rec.product_id = mac.product_id.id
                        rec.etsi_serial_product = mac.etsi_serials_field
                        rec.etsi_smart_card = mac.etsi_smart_card_field
                        rec.issued = "Used"
                        rec.quantity = 1.00
                        rec.product_uom = 1
                        break
                
                # Smart Card
                if rec.etsi_smart_card:
                    # Validation for issued status
                    for scard in pm_search_sc:
                        # Auto fill statements
                        rec.product_id = scard.product_id.id
                        rec.etsi_mac_product = scard.etsi_mac_field
                        rec.etsi_serial_product = scard.etsi_serials_field
                        rec.issued = "Used"
                        rec.quantity = 1.00
                        rec.product_uom = 1
                        break
                        
                # Serial Number
                if rec.etsi_serial_product:
                    # Validation for issued status
                    for ser in pm_search_sr:

                        if ser.issued_field == "Available":
                            raise ValidationError("This Product is not yet issued!")

                        if ser.issued_field != "Deployed":
                            raise ValidationError("This Product is already issued!")
                        
                        # Auto fill statements
                        rec.product_id = ser.product_id.id
                        rec.etsi_mac_product = ser.etsi_mac_field
                        rec.etsi_smart_card = ser.etsi_smart_card_field
                        rec.issued = "Used"
                        rec.quantity = 1.00
                        rec.product_uom = 1
                        break
    
    # Suggestion box 
    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def store_recommendation(self):
        recommend = []
        count =  0 
        for rec in self:
            if rec.etsi_serial_product:

                recommend.append(rec.etsi_serial_product)
                count += 1
        
        for item in recommend:
            database = self.env['issuance.recommendation'].search([])
            database.create({'etsi_serial_product' : item})
        

class Container(models.TransientModel):
    _name = 'issuance.recommendation'

    etsi_serial_product = fields.Char()

class Subscriber_issuance(models.Model):
    _inherit = 'stock.move'

    # Add aditional fields for move_lines
    subs_issuance_connector = fields.Many2one('stock.picking')
     # Subscriber Form
    job_number = fields.Char("Job Order")
    subs_type = fields.Char("Type")
    comp_date = fields.Date("Completion Date", default=datetime.today())
    form_num = fields.Char("Form Number")
    form_type = fields.Selection({
        ('a','Newly Installed'),
        ('b','Immediate')
    })

class ValidationProcess(models.TransientModel):
    _inherit ='stock.immediate.transfer'
        # bypass mark as to do since it was remove
    @api.multi
    def process(self):
        self.ensure_one()
        # If still in draft => confirm and assign
        if self.pick_id.state == 'draft':
            self.pick_id.action_confirm()
            if self.pick_id.state != 'assigned':
                self.pick_id.action_assign()
                if self.pick_id.state != 'assigned':
                    raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
        for pack in self.pick_id.pack_operation_ids:
            if pack.product_qty > 0:
                pack.write({'qty_done': pack.product_qty})
            else:
                pack.unlink()
        return self.pick_id.do_transfer()