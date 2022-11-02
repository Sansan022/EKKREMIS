from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class Validate_Subscriber_Issuance(models.Model):
    _inherit = 'stock.picking'
    # Subscriber Issuance Form Field
     # Subscriber Form
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

        listahan = []
        for rec in self:
            search_name = self.env['stock.picking'].search([('name','=',rec.name)])
            picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Subscriber Issuance')])

            for x in rec.subs_issue:

                listahan.append((
                    0, 0, {
                        'name':x.product_id.product_tmpl_id.name,
                        'product_id': x.product_id_related.id, 
                        'product_uom_qty' : x.product_uom_qty, 
                        # Unit of measure 
                        'product_uom' : x.product_uom_related.id,
                        'move_id': x.id, 
                        'issued_field': "Used",
                        'etsi_serials_field': x.etsi_serial_product, 
                        'etsi_mac_field': x.etsi_mac_product, 
                        'etsi_smart_card_field': x.etsi_smart_card,
                        # 'subscriber' : x.subscriber_field.id,
                        'state' : 'draft',
                        'location_id' : rec.location_id,
                        'location_dest_id' : rec.location_dest_id,
                        'picking_type_id': rec.picking_type_id
                    }
                    ))
                
                for item in listahan:
                    print(item)
                    
        picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
        stock_picking_db = self.env['stock.picking']

        self.update({
            # 'etsi_team_issuance_id': picking.id,
            # 'picking_type_id': picking_checker2.id,
            # 'partner_id': self.skycable_subscriber_id.id,
            'move_lines':listahan,
            # 'location_id': picking_checker2.default_location_src_id.id,
            # 'location_dest_id': picking_checker2.default_location_dest_id.id,
            # 'etsi_teams_id':  picking.etsi_teams_id.id,
            # 'state' : 'draft'
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
                                # searched_ids.update({'etsi_team_in': self.etsi_teams_id.team_number})
        
    @api.multi
    def do_new_transfer(self):
        res = super(Validate_Subscriber_Issuance, self).do_new_transfer()

        print("Subscriber ISSUANCE")
        print("Subscriber ISSUANCE")
        print("Subscriber ISSUANCE")


        for rec in self:
            print(rec.teller)
            print(rec.teller)
            teller = rec.teller

        if teller == 'subscriber':
    
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))


            listahan = []
            for rec in self:
                search_name = self.env['stock.picking'].search([('name','=',rec.name)])
                picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Subscriber Issuance')])

            picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
            stock_picking_db = self.env['stock.picking']

            self.update({
                'state' : 'done'
                })
            
            # To Update the status 
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
                                    # searched_ids.update({'etsi_team_in': self.etsi_teams_id.team_number})
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
            print(res['picking_type_id'],"res picking id" )
            picking_type_id = res['picking_type_id']
            print(picking_type_id,"Picking id")
            
            self.env['hr.employee.category'].search([ ('default_emp_category', '=', True)]).ids

            search = self.search([('picking_type_id','=', picking_type_id)], limit=1)
            names = self.env['hr.employee.category'].search([ ('default_emp_category', '=', True)]).name

            pm_search_sr = self.env['stock.picking.type'].search([('id','=', picking_type_id)])
            
            print(search.name, "ANDITO KA")
          
            data_obj    = self.env['stock.picking']
            for data in self:       
                list_data   = data_obj.search([])
                data.example_count = len(list_data)

                print(len(list_data))
                print(len(list_data))
                print(len(list_data))
                print(len(list_data))
                print(len(list_data))
                print(len(list_data))

                print(data.example_count)
                print(data.example_count)
                print(data.example_count)
                print(data.example_count)

            
            # for data in self:       
            #     list_data = data_obj.search_count([()])
            #     data.etsi_subscriber_issuance = len(list_data)  
            #     print(data.etsi_subscriber_issuance,"COUNT")
            #     print(data.etsi_subscriber_issuance,"COUNT")
            #     print(data.etsi_subscriber_issuance,"COUNT")
            #     print(data.etsi_subscriber_issuance,"COUNT")



           
            if pm_search_sr.name == 'Subscriber Issuance':

                res['teller'] = 'subscriber'
            if pm_search_sr.name == 'Team Issuance':

                res['teller'] = 'others'
            if pm_search_sr.name == 'Team Return':

                res['teller'] = 'return'

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


    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def onchange_transfer(self):
        # Validate Datas
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
                    # if p_lists_mc[0] == False:
                    #     raise ValidationError("This product is CATV, there is no MAC ID!")
                    # if rec.etsi_mac_product not in p_lists_mc:
                    #     raise ValidationError("MAC ID not available in returns!")
                    # # Validation for issued status
                    for mac in pm_search_mc:

                    #     if mac.issued_field == "Yes":
                    #         raise ValidationError("This Product is already issued!")
                    #     if mac.issued_field == "Return":
                    #         raise ValidationError("Product is already returned!")
                            
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
                    # if p_lists_sc[0] == False:
                    #     raise ValidationError("This product is MODEM, there is no Smart Card!")
                    # if rec.etsi_smart_card not in p_lists_sc:
                    #     raise ValidationError("Smart Card not available in returns!")
                    # else:
                    #     # Validation for issued status
                    for scard in pm_search_sc:
                    #         if scard.issued_field == "Yes":
                    #             raise ValidationError("This Product is already issued!")
                    #         if scard.issued_field == "Return":
                    #             raise ValidationError("Product is already returned!")
                            
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
                    # if rec.etsi_serial_product not in p_lists_sr:
                    #     raise ValidationError("Serial not available in returns!")
                    # else:
                    #     # Validation for issued status
                    for ser in pm_search_sr:

                        if ser.issued_field == "Available":
                            raise ValidationError("This Product is not yet issued!")

                        if ser.issued_field != "Deployed":
                            raise ValidationError("This Product is already issued!")
                        
                        # if ser.issued_field == "Return":
                        #     raise ValidationError("Product is already returned!")
                        
                            # Auto fill statements
                        rec.product_id = ser.product_id.id
                        rec.etsi_mac_product = ser.etsi_mac_field
                        rec.etsi_smart_card = ser.etsi_smart_card_field
                        rec.issued = "Used"
                        rec.quantity = 1.00
                        rec.product_uom = 1

                        print(ser.issued_field)
                        print(ser.issued_field)
                        print(ser.issued_field)
                        break


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






