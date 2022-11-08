from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError

class Validate_Team_Return(models.Model):
    _inherit = 'stock.picking'

    # picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
    teller = fields.Selection([('return', 'Return'),('damage', 'Damage'),('others', 'Others'),('subscriber', 'Subscriber'),('pull-out', 'Pullout Receive'),('pull-out-return', 'Pullout Return')], default='others')
    source = fields.Many2one('stock.picking', domain="[('picking_type_id.name','=', 'Team Issuance')]", string="Source Document")
    transfered_item = fields.Many2one("etsi.inventory")
    product_stats = fields.Selection([
        ('damage','Damaged'),
        ('return','Returned')
    ], string="Product status")
    remarks = fields.Text("Remarks")
    # One2many to list all items
    return_list = fields.One2many('stock.picking.return.list','return_list_connector')
    # Returned Items list 
    return_items = fields.One2many('stock.picking.damaged.item.list','damaged_item_connector')
    # Damaged Items List 
    damaged_items =  fields.One2many('stock.picking.damaged.item.list','damaged_item_connector')

    @api.model
    def default_get(self, fields):
        res = super(Validate_Team_Return, self).default_get(fields)

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
    
    # Auto fill of return_list_code
    @api.onchange('source')
    def change_return_list(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        listahan = []
        for rec in self:
            search_name = self.env['stock.picking'].search([('name','=',rec.name)])
            picking_checker = self.env['stock.picking'].search([('picking_type_id.name','=', 'Team Return')])
            
            search_first = self.env['stock.picking'].search([('name','=',rec.source.name)])

            for item in search_first:
                teams_id = item.etsi_teams_id.id
                search_first2 = self.env['stock.move'].search([])
                for x in search_first2:
                    if x.picking_id.name == rec.source.name:
                        if  x.issued_field == 'Deployed' :
                                # listahan.append({'serial':x.etsi_serials_field, 'mac_id': x.etsi_mac_field })
                            listahan.append((
                            0, 0, {
                                'product_id': x.product_id.id, 
                                'quantity' : x.product_uom_qty, 
                                # Unit of measure 
                                'product_uom' : x.product_uom.id,
                                'move_id': x.id, 
                                'issued': x.issued_field,
                                'etsi_serial_product': x.etsi_serials_field, 
                                'etsi_mac_product': x.etsi_mac_field, 
                                'etsi_smart_card': x.etsi_smart_card_field,
                                'issued_field': x.issued_field,
                                'subscriber' : x.subscriber_field.id,
                                'state' : 'draft',
                                'active_ako' : x.picking_id.id,
                                'active_name' : rec.name,
                                'teams': rec.etsi_teams_id.id
                            }
                            ))
                            self.update({'etsi_teams_id' : teams_id })
                        # else:
                        #     raise ValidationError("No available item to return in this ")
                        

        # Update the one2many table
            self.update({'return_list': listahan})

# Transient Model to hold all that will be returned(same as product_return_moves)
class Return_list_holder(models.TransientModel):
    _name = 'stock.picking.return.list.holder'
    
    # One2many to list all items
    return_list_move_holder =  fields.One2many('stock.picking.return.list_2','return_list_moves_connector_2')
    damage_list_ids = fields.One2many("stock.picking.damage.list", "damage_list_id")
    transfer_list_ids = fields.One2many("stock.picking.transfer.list", "transfer_list_id")
    # installed_list_move_holder =  fields.One2many('stock.picking.return.list_3','return_list_moves_connector_3')
    
    # Action na pag save 
    @api.multi
    def return_btn(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        issued_stats = self.env['stock.move'].search([])
        inventory_stats = self.env['etsi.inventory'].search([])

        # Pick up the return picking_type_id for return
        picking_type_id = picking.picking_type_id.id 
        
        # List for team return
        team_return = []
        product_lists = []
        product_serials = []
        
        # list for damaged item
        team_return_damaged = []
        
        # list for transfered items
        team_return_transfer = []

        # Return
        if self.return_list_move_holder:
            for line_ret in self.return_list_move_holder:
                team_return.append({
                    'name':line_ret.product_id.product_tmpl_id.name,
                    'product_id': line_ret.product_id.id,
                    'etsi_serials_field': line_ret.etsi_serial_product,
                    'etsi_mac_field': line_ret.etsi_mac_product,
                    'etsi_smart_card_field': line_ret.etsi_smart_card,

                    # Additional for returned items
                    'etsi_serial_product' : line_ret.etsi_serial_product,
                    'etsi_mac_product' : line_ret.etsi_mac_product,
                    'etsi_smart_card' : line_ret.etsi_smart_card,
                    'issued' : "Return",

                    # Continuation
                    'issued_field': "Return",
                    'product_uom': line_ret.product_id.product_tmpl_id.uom_id.id,
                    'quantity': line_ret.quantity, 
                    'location_id' : 1,
                    'location_dest_id' : 2,
                    # Hard coded pa tong picking_type Id 
                    'picking_type_id': 6
                })
            
        # Damaged
        if self.damage_list_ids:
            for line_dmg in self.damage_list_ids:
                team_return_damaged.append({
                    'name':line_dmg.product_id.product_tmpl_id.name,
                    'product_id': line_dmg.product_id.id,
                    'etsi_serials_field': line_dmg.etsi_serial_product,
                    'etsi_mac_field': line_dmg.etsi_mac_product,
                    'etsi_smart_card_field': line_dmg.etsi_smart_card,
                    
                    # Additional for returned items
                    'etsi_serial_product' : line_dmg.etsi_serial_product,
                    'etsi_mac_product' : line_dmg.etsi_mac_product,
                    'etsi_smart_card' : line_dmg.etsi_smart_card,

                    'dmg_type': line_dmg.dmg_type,

                    'issued' : "Return",
                    'issued_field': "Damaged",
                    'issued' : "Damaged", 
                    'product_uom': line_dmg.product_id.product_tmpl_id.uom_id.id,
                    'quantity': line_dmg.quantity, 
                    'location_id' : 18,
                    'location_dest_id' : 19,
                    # Hard coded pa tong picking_type Id 
                    'picking_type_id': 9,
        
                })
        
        # Transfer declaration / process
        if self.transfer_list_ids:
            for line_trans in self.transfer_list_ids:
                team_return_transfer.append({
                    'name':line_trans.product_id.product_tmpl_id.name,
                    'product_id': line_trans.product_id.id,
                    'etsi_serials_field': line_trans.etsi_serial_product,
                    'etsi_mac_field': line_trans.etsi_mac_product,
                    'etsi_smart_card_field': line_trans.etsi_smart_card,
                    'issued_field': "Return",
                    'product_uom': line_trans.product_id.product_tmpl_id.uom_id.id,
                    'quantity': line_trans.quantity,
                    'teams_from': line_trans.teams_from.id,
                    'teams_to': line_trans.teams_to.id,
                    'location_id' : 1,
                    'location_dest_id' : 2,
                    # Hard coded pa tong picking_type Id 
                    'picking_type_id': 6
                })       
        
        for rec in self:
            # # Normal Return
            if team_return:
                picking.update({
                    'state' : 'done',
                    'picking_type_id': picking_type_id,
                    'move_lines': team_return,
                    'return_items' : team_return,
                    'status_field' :  'done',
                    # create ka pa dito ng laman ng return_list(all items) 
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
                })
                
                for plines in rec.return_list_move_holder:
                    product_lists.append(plines.product_id)
                    product_serials.append(plines.etsi_serial_product)
                
                # For Normal Return
                if product_lists and product_serials:
                    for issued_ids in issued_stats:
                        if issued_ids.etsi_serials_field in product_serials:
                            issued_ids.update({'issued_field': 'Available'})
            
                            for searched_ids in inventory_stats:
                                if searched_ids.etsi_product_id in product_lists:
                                    if searched_ids.etsi_serial in product_serials:
                                        searched_ids.update({'etsi_status': 'available'})
                                        
            # Transfer Items
            if team_return_transfer or team_return:
                transfer_picking = self.env['etsi.inventory'].search([])
                trans_move = self.env['stock.move'].search([])
                trans_ako = self.env['stock.transfer.team.return'].search([])
                
                listahan_ng_trans = []
                store_me_daddy = []
                
                counter = 0
                
                # If reciever is early - get the items from return lists and store it in temporary database
                if team_return:
                    for t_hold in rec.return_list_move_holder:
                        if picking.etsi_teams_id.team_number == t_hold.teams.team_number:
                            store_me_daddy.append(t_hold.active_ako.id)
                            
                        elif picking.etsi_teams_id.team_number != t_hold.teams.team_number:
                            for source in store_me_daddy: # Fetch all source data
                                counter += 1
                                if counter == 1: # filter / get 1 data only
                                    if trans_ako: # if database is not empty
                                        for trans_to2 in trans_ako:
                                            if t_hold.etsi_serial_product == trans_to2.etsi_serial_product and trans_to2.issued == 'Waiting' and trans_to2.transfer_checker == True:
                                                trans_ako.update({
                                                    'issued': "Done",
                                                    'source': source,
                                                    'return_checker': True,
                                                })
                                                
                                                # Update record of product recipient's team issuance
                                                for move in trans_move:
                                                    for inventory in transfer_picking:
                                                        # Check if the floating data is ready - to update the product list on team issuance (Product reciever)
                                                        if trans_to2.issued == 'Done' and trans_to2.transfer_checker == True and trans_to2.return_checker == True:
                                                            # update stock.move
                                                            if move.etsi_serials_field == trans_to2.etsi_serial_product:
                                                                move.update({'picking_id': trans_to2.source.id})
                                                                
                                                                # update etsi.inventory - team number
                                                                if inventory.etsi_serial == t_hold.etsi_serial_product:
                                                                    inventory.update({'etsi_team_in': picking.etsi_teams_id.id})
                                                                    
                                                                    # Delete floating data
                                                                    self.ensure_one()
                                                                    trans_to2.unlink()
                                                                    return
                                            elif t_hold.etsi_serial_product == trans_to2.etsi_serial_product and trans_to2.return_checker:
                                                raise ValidationError("This serial is already returned, Please wait the other team for transfer slip (confirmation)!")
                                            
                                            else:
                                                # Create data function for transfer items
                                                return_transfer_function = self.env['stock.transfer.team.return'].create({
                                                    'product_id': t_hold.product_id.id,
                                                    'quantity': 1.0,
                                                    'issued': "Waiting",
                                                    'etsi_serial_product': t_hold.etsi_serial_product,
                                                    'etsi_mac_product':  t_hold.etsi_mac_product,
                                                    'etsi_smart_card':  t_hold.etsi_smart_card,
                                                    'source': source,
                                                    'team_num_from': t_hold.teams.id,
                                                    'team_num_to': picking.etsi_teams_id.id,
                                                    'transfer_checker': False,
                                                    'return_checker': True,
                                                })
                                                break
                                    # if database is empty
                                    else:
                                        # Create data function for transfer items
                                        return_transfer_function = self.env['stock.transfer.team.return'].create({
                                            'product_id': t_hold.product_id.id,
                                            'quantity': 1.0,
                                            'issued': "Waiting",
                                            'etsi_serial_product': t_hold.etsi_serial_product,
                                            'etsi_mac_product':  t_hold.etsi_mac_product,
                                            'etsi_smart_card':  t_hold.etsi_smart_card,
                                            'source': source,
                                            'team_num_from': t_hold.teams.id,
                                            'team_num_to': picking.etsi_teams_id.id,
                                            'transfer_checker': False,
                                            'return_checker': True,
                                        })
                                        break
                
                # who transfered the item
                if team_return_transfer:
                    for t_hold in rec.transfer_list_ids:
                        listahan_ng_trans.append({
                            'product_id': t_hold.product_id.id,
                            'serial': t_hold.etsi_serial_product,
                            'mac': t_hold.etsi_mac_product,
                            'smart_card': t_hold.etsi_smart_card,
                            'source': t_hold.active_ako.id,
                            'team_from': t_hold.teams_from.id,
                            'team_to': t_hold.teams_to.id,
                        })
                    
                    for trans_to in listahan_ng_trans:
                        if trans_ako:
                            for trans_to2 in trans_ako:
                                if trans_to['serial'] == trans_to2.etsi_serial_product and trans_to2.issued == 'Waiting' and trans_to2.return_checker == True:
                                    print(trans_to2.etsi_serial_product, "UPDATE")
                                    trans_ako.update({
                                        'issued': "Done",
                                        'transfer_checker': True,
                                    })
                                    
                                    # Update record of product recipient's team issuance
                                    for move in trans_move:
                                        for inventory in transfer_picking:
                                            # Check if the floating data is ready - to update the product list on team issuance (Product reciever)
                                            if trans_to2.issued == 'Done' and trans_to2.transfer_checker == True and trans_to2.return_checker == True:
                                                # update stock.move
                                                if move.etsi_serials_field == trans_to2.etsi_serial_product:
                                                    move.update({'picking_id': trans_to2.source.id})
                                                    
                                                    # update etsi.inventory - team number
                                                    if inventory.etsi_serial == trans_to['serial']:
                                                        inventory.update({'etsi_team_in': picking.etsi_teams_id.id})
                                                        
                                                        # Delete floating data
                                                        self.ensure_one()
                                                        trans_to2.unlink()
                                                        return
                                
                                elif trans_to2.transfer_checker and trans_to['serial'] == trans_to2.etsi_serial_product:
                                    raise ValidationError("This serial is already transfered, Please wait the other team for updates!")
                                
                                else:
                                    # Create data function for transfer items
                                    return_transfer_function = self.env['stock.transfer.team.return'].create({
                                        'product_id': trans_to['product_id'],
                                        'quantity': 1.0,
                                        'issued': "Waiting",
                                        'etsi_serial_product': trans_to['serial'],
                                        'etsi_mac_product':  trans_to['mac'],
                                        'etsi_smart_card':  trans_to['smart_card'],
                                        'source': '',
                                        'team_num_from': trans_to['team_from'],
                                        'team_num_to': trans_to['team_to'],
                                        'transfer_checker': True,
                                        'return_checker': False,
                                    })
                                    break
                        # if database is empty
                        else:
                            # Create data function for transfer items
                            return_transfer_function = self.env['stock.transfer.team.return'].create({
                                'product_id': trans_to['product_id'],
                                'quantity': 1.0,
                                'issued': "Waiting",
                                'etsi_serial_product': trans_to['serial'],
                                'etsi_mac_product':  trans_to['mac'],
                                'etsi_smart_card':  trans_to['smart_card'],
                                'source': '',
                                'team_num_from': trans_to['team_from'],
                                'team_num_to': trans_to['team_to'],
                                'transfer_checker': True,
                                'return_checker': False,
                            })
                            break
                        
        # Damage Transaction
        if team_return_damaged: 
            issued_stats = self.env['stock.move'].search([])
            inventory_stats = self.env['etsi.inventory'].search([]) 
            picking_checker2 = self.env['stock.picking.type'].search([('name', '=', 'Damage Location')])
              
            final_return_list_damaged = []

            for line_return_damage in team_return_damaged:
                final_return_list_damaged.append((0,0,line_return_damage))
        
            # Appends the list for teams selected
            team_lst = []
            for team_line in picking.etsi_teams_line_ids:
                team_res = {
                    'team_members_lines': team_line.team_members_lines.id,
                    'etsi_teams_replace': team_line.etsi_teams_replace.id,
                    'etsi_teams_temporary': team_line.etsi_teams_temporary,
                }
                team_lst.append(team_res)

            team_new_list = []
            for team_line2 in team_lst:
                team_new_list.append((0,0,team_line2))

            stock_picking_db = self.env['stock.picking']
            return_damaged_function = stock_picking_db.create({
                    'picking_type_id': picking_checker2.id,
                    'move_lines':final_return_list_damaged,
                    # Damaged items
                    'damaged_items' : final_return_list_damaged, 
                    'location_id': picking_checker2.default_location_src_id.id,
                    'location_dest_id': picking_checker2.default_location_dest_id.id,
                    'etsi_teams_member_no': picking.etsi_teams_member_no,
                    'etsi_teams_member_name': picking.etsi_teams_member_name.id,
                    'etsi_teams_id':  picking.etsi_teams_id.id,
                    'etsi_teams_line_ids':  team_new_list,
                    'state' : 'done',
                    'teller' : 'damage'
                })
            # Execure the damaged function
            return_damaged_function.action_assign()

            # Update the status of created record for damaged items in stock.picking 

            search_picking = self.env['stock.move'].search([])

            for serial in search_picking:
                for list_serial in team_return_damaged:
                    search_picking_id = self.env['stock.move'].search([('etsi_serials_field','=',list_serial['etsi_serials_field'])])

                    if search_picking_id:
                        stock_picking = self.env['stock.picking'].search([('id','=', serial.picking_id.id)])

                        stock_picking.update({
                            'state' : 'done'
                        })
                   
            
            # Update quanity of serials from subscriber issuance
            product_lists_damaged = []
            product_serials_damaged = []

            for plines in rec.damage_list_ids:
                product_lists_damaged.append(plines.product_id)
                product_serials_damaged.append(plines.etsi_serial_product)

            # For damaged products - Code for updating status 
            if product_lists_damaged and product_serials_damaged:
                for issued_ids in issued_stats:
                    if issued_ids.etsi_serials_field in product_serials_damaged:
                        issued_ids.update({'issued_field': 'Damaged'})
        
                        for searched_ids in inventory_stats:
                            if searched_ids.etsi_product_id in product_lists_damaged:
                                if searched_ids.etsi_serial in product_serials_damaged:
                                    searched_ids.update({'etsi_status': 'damaged'})
        
        # if all transation is done update current form in done state
        picking.update({'state' : 'done'})

    @api.model
    def default_get(self, fields):
        res = super(Return_list_holder, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))

        # if form is in done state, raise a validation
        if picking.state == 'done':
            raise ValidationError("This form is no longer available to return. (Only in draft state)")
        
        # Declare return value in teller
        if picking.picking_type_id.name == "Team Return":
            picking.teller = "return"
        
        
        return_list_move = []
        damage_list_move = []
        transfer_list_move = []
        for p in picking:
            for move in p.return_list:
                if picking.return_list:
                    # If CATV is selected
                    if move.etsi_smart_card:
                        if move.return_checker:
                            return_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': 'Available',
                                'etsi_serial_product': move.etsi_serial_product, 
                                'etsi_smart_card': move.etsi_smart_card,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id,
                                'teams': move.teams.id
                            }))
                        if move.damage_checker:
                            damage_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': 'Damaged',
                                'dmg_type': move.dmg_type,
                                'etsi_serial_product': move.etsi_serial_product, 
                                'etsi_smart_card': move.etsi_smart_card,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id
                            }))
                        if move.transfer_checker:
                            transfer_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': move.issued,
                                'etsi_serial_product': move.etsi_serial_product, 
                                'etsi_smart_card': move.etsi_smart_card,
                                'teams_from': move.teams_from.id,
                                'teams_to': move.teams_to.id,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id,
                            }))
                    # If MODEM is selected
                    if move.etsi_mac_product:
                        if move.return_checker:
                            return_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': 'Available',
                                'etsi_serial_product': move.etsi_serial_product, 
                                'etsi_mac_product': move.etsi_mac_product,
                                'etsi_smart_card': move.etsi_smart_card,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id,
                                'teams': move.teams.id
                            }))
                        if move.damage_checker:
                            damage_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': 'Damaged',
                                'dmg_type': move.dmg_type,
                                'etsi_serial_product': move.etsi_serial_product, 
                                'etsi_mac_field': move.etsi_mac_product,
                                'etsi_smart_card': move.etsi_smart_card,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id
                            }))
                        if move.transfer_checker:
                            transfer_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': move.issued,
                                'etsi_serial_product': move.etsi_serial_product, 
                                'etsi_mac_product': move.etsi_mac_product,
                                'etsi_smart_card': move.etsi_smart_card,
                                'teams_from': move.teams_from.id,
                                'teams_to': move.teams_to.id,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id
                            }))
                    # If item has no MAC ID and Smart Card
                    if not move.etsi_smart_card and not move.etsi_mac_product:
                        if move.return_checker:
                            return_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': 'Available',
                                'etsi_serial_product': move.etsi_serial_product, 
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id,
                                'teams': move.teams.id
                            }))
                        if move.damage_checker:
                            damage_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': 'Damaged',
                                'dmg_type': move.dmg_type,
                                'etsi_serial_product': move.etsi_serial_product, 
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id
                            }))
                        if move.transfer_checker:
                            transfer_list_move.append((
                                0, 0, {
                                'product_id': move.product_id.id, 
                                'quantity': move.quantity, 
                                # 'move_id': move.id, 
                                'product_uom' : move.product_uom.id,
                                'issued': move.issued,
                                'etsi_serial_product': move.etsi_serial_product, 
                                'teams_from': move.teams_from.id,
                                'teams_to': move.teams_to.id,
                                'active_ako' : move.active_ako.id,
                                'active_name' : p.id,
                            }))
        
        if not return_list_move and not damage_list_move and not transfer_list_move:
            raise UserError(_("No products to return (only in team return operational type / please select transaction type to continue)!"))
        if 'return_list_move_holder' in fields or 'damage_list_ids' in fields or 'transfer_list_ids' in fields:
                # Return
                res.update({'return_list_move_holder': return_list_move})
                # Damage
                res.update({'damage_list_ids': damage_list_move})
                # Transfer
                res.update({'transfer_list_ids': transfer_list_move})
        if 'etsi_teams_id' in fields:
            res.update({'etsi_teams_id': picking.etsi_teams_id.id})
        return res

class TransferLists(models.Model):
    _name = "stock.transfer.team.return"
    
    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Product Status")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    transfer_checker = fields.Boolean("Transfer")
    return_checker = fields.Boolean("Return")
    source = fields.Many2one('stock.picking')
    team_num_from = fields.Many2one('team.configuration')
    team_num_to = fields.Many2one('team.configuration')
    date_transfered = fields.Date(default=datetime.today())
    

class Return_list_childs(models.TransientModel):
    _name = 'stock.picking.return.list'

    # Connects to return_list
    return_list_connector = fields.Many2one('stock.picking')
    # Connects to return_list_moves
    return_list_moves_connector = fields.Many2one('stock.picking.return.list.holder')

    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity',default=1.0)
    issued = fields.Char(string="Product Status")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)
    active_name = fields.Char('Active Name')
    
    transfer_checker = fields.Boolean("Transfer")
    damage_checker = fields.Boolean("Damage")
    dmg_type = fields.Selection([
        ('physical','Physical Damage'),
        ('boot','Not Bootable'),
        ('power','No Power')
    ], string="Damage Type")
    return_checker = fields.Boolean("Return")
    teams = fields.Many2one('team.configuration')
    teams_from = fields.Many2one('team.configuration', string="Teams From")
    teams_to = fields.Many2one('team.configuration', string="Teams To")
    
    teams_from_duplicate = fields.Many2one('team.configuration', related='teams_from')
    teams_to_duplicate = fields.Many2one('team.configuration')
    product_id_duplicate =  fields.Many2one('product.product', related="product_id") 
    product_uom_duplicate = fields.Many2one('product.uom', related="product_uom")
    issued_duplicate = fields.Char(related="issued")
    
    @api.multi 
    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def onchange_transfer(self):
        for rec in self:
            etsi_inv = self.env['etsi.inventory'].search([])
            
            # Auto Fill Function
            # search available products - stock.move model
            pm_search_sr = self.env['stock.move'].search([('etsi_serials_field','=', rec.etsi_serial_product)])
            pm_search_mc = self.env['stock.move'].search([('etsi_mac_field','=', rec.etsi_mac_product)])
            pm_search_sc = self.env['stock.move'].search([('etsi_smart_card_field','=', rec.etsi_smart_card)])
            
            ei_search_sr = self.env['etsi.inventory'].search([('etsi_serial','=', rec.etsi_serial_product)])
            ei_search_mc = self.env['etsi.inventory'].search([('etsi_mac','=', rec.etsi_mac_product)])
            ei_search_sc = self.env['etsi.inventory'].search([('etsi_smart_card','=', rec.etsi_smart_card)])
            
            search_name = self.env['stock.picking'].search([('name','=', rec.active_ako.name)])
            
            transfer_list = self.env['stock.transfer.team.return'].search([])
            
            list_ako = []
            
            # Valued data only passes
            if rec.etsi_serial_product != False or rec.etsi_mac_product != False or rec.etsi_smart_card != False:
                # Check if data inputted is available
                # MAC ID
                if rec.etsi_mac_product:
                    # # Validation for issued status
                    if pm_search_mc:
                        for mac in pm_search_mc:
                            for mac2 in ei_search_mc:
                                if mac.issued_field == "Deployed":
                                    # Auto fill statements
                                    rec.product_id = mac.product_id.id
                                    rec.etsi_serial_product = mac.etsi_serials_field
                                    rec.etsi_smart_card = mac.etsi_smart_card_field
                                    rec.issued = "Deployed"
                                    rec.active_ako = mac.picking_id.id
                                    rec.quantity = 1.00
                                    rec.product_uom = 1
                                    rec.teams = mac2.etsi_team_in.id
                                else:
                                    raise ValidationError("This Product is not Deployed / Already installed (Used)")
                    else:
                        raise ValidationError("This Product is not Deployed / Already installed (Used)")
                
                # Smart Card
                if rec.etsi_smart_card:
                    # Validation for issued status
                    if pm_search_sc:
                        for scard in pm_search_sc:
                            for scard2 in ei_search_sc:
                                if scard.issued_field == "Deployed":
                                    # Auto fill statements
                                    rec.product_id = scard.product_id.id
                                    rec.etsi_mac_product = scard.etsi_mac_field
                                    rec.etsi_serial_product = scard.etsi_serials_field
                                    rec.issued = "Deployed"
                                    rec.active_ako = scard.picking_id.id
                                    rec.quantity = 1.00
                                    rec.product_uom = 1
                                    rec.teams = scard2.etsi_team_in.id
                                else:
                                    raise ValidationError("This Product is not Deployed / Already installed (Used)")
                    else:
                        raise ValidationError("This Product is not Deployed / Already installed (Used)")
                        
                # Serial Number
                if rec.etsi_serial_product:
                    # Validation for issued status
                    if pm_search_sr:
                        # check stock.move
                        for ser in pm_search_sr:
                            # check etsi.inventory
                            for ser2 in ei_search_sr:
                                # check if transfer list is true
                                if transfer_list:
                                    # check stock.transfer.team.return
                                    for t_list in transfer_list:
                                        if ser.issued_field == "Deployed":
                                            # Auto fill statements
                                            rec.product_id = ser.product_id.id
                                            rec.etsi_mac_product = ser.etsi_mac_field
                                            rec.etsi_smart_card = ser.etsi_smart_card_field
                                            rec.issued = "Deployed"
                                            rec.active_ako = ser.picking_id.id
                                            rec.quantity = 1.00
                                            rec.product_uom = 1
                                            # rec.teams_from = s_name.etsi_teams_id.id
                                            rec.teams = ser2.etsi_team_in.id
                                        elif t_list.etsi_serial_product == rec.etsi_serial_product and t_list.issued == "Waiting":
                                            # Auto fill statements
                                            rec.product_id = ser.product_id.id
                                            rec.etsi_mac_product = ser.etsi_mac_field
                                            rec.etsi_smart_card = ser.etsi_smart_card_field
                                            rec.issued = "Deployed"
                                            rec.active_ako = ser.picking_id.id
                                            rec.quantity = 1.00
                                            rec.product_uom = 1
                                            # rec.teams_from = s_name.etsi_teams_id.id
                                            rec.teams = ser2.etsi_team_in.id
                                        else:
                                            raise ValidationError("This Product is not Deployed / Already installed (Used)")
                                else:
                                    # check stock.transfer.team.return
                                    if ser.issued_field == "Deployed":
                                        # Auto fill statements
                                        rec.product_id = ser.product_id.id
                                        rec.etsi_mac_product = ser.etsi_mac_field
                                        rec.etsi_smart_card = ser.etsi_smart_card_field
                                        rec.issued = "Deployed"
                                        rec.active_ako = ser.picking_id.id
                                        rec.quantity = 1.00
                                        rec.product_uom = 1
                                        # rec.teams_from = s_name.etsi_teams_id.id
                                        rec.teams = ser2.etsi_team_in.id
                                    else:
                                        raise ValidationError("This Product is not Deployed / Already installed (Used)")
                    else:
                        raise ValidationError("This Product is not Deployed / Already installed (Used)")
                    
    @api.multi
    @api.onchange('transfer_checker')   
    def checker_onchange(self):
        # If transfer checker is checked
        for rec in self:
            search_name = self.env['stock.picking'].search([('name','=', rec.active_ako.name)])
            
            if rec.transfer_checker:
                for s_name in search_name:
                    rec.teams_from = s_name.etsi_teams_id.id
            else:
                # Remove from vals
                rec.teams_from = False
                rec.teams_to = False
                rec.update({'teams_to': False})
                             
class Return_list_child(models.TransientModel):
    _name = 'stock.picking.return.list_2'

    # Connects to return_list
    return_list_connector = fields.Many2one('stock.picking')
    # Connects to return_list_moves
    return_list_moves_connector_2 = fields.Many2one('stock.picking.return.list.holder')

    damage_checker = fields.Boolean('Damaged')
    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Product Status")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    active_name = fields.Many2one('stock.picking')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)
    teams = fields.Many2one('team.configuration')
    # transfer_checker = fields.Boolean("Transfer")
    # teams = fields.Many2one('team.configuration')

class DamageLists(models.TransientModel):
    _name = "stock.picking.damage.list"
    
    # Connects to return_list_moves
    damage_list_id = fields.Many2one('stock.picking.return.list.holder')

    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Product Status")
    dmg_type = fields.Selection([
        ('physical','Physical Damage'),
        ('boot','Not Bootable'),
        ('power','No Power')
    ], string="Damage Type")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    active_name = fields.Many2one('stock.picking')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)
    
class TransferLists(models.TransientModel):
    _name = "stock.picking.transfer.list"
    
    # Connects to return_list_moves
    transfer_list_id = fields.Many2one('stock.picking.return.list.holder')

    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Product Status")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    active_name = fields.Many2one('stock.picking')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)
    teams_from = fields.Many2one('team.configuration', string="Teams From")
    teams_to = fields.Many2one('team.configuration', string="Teams To")


# Model for accepting returned items
class ReturnedItems(models.Model):
    _name='stock.picking.returned.item.list'
      # Connects to return_list
    return_item_connector = fields.Many2one('stock.picking')

    product_id =  fields.Many2one('product.product',string='Product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Product Status")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    active_name = fields.Many2one('stock.picking')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)
    teams = fields.Many2one('team.configuration')

# Model for accepting damaged items

class DamagedItems(models.Model):
    _name = 'stock.picking.damaged.item.list'

    damaged_item_connector = fields.Many2one('stock.picking')

    product_id =  fields.Many2one('product.product',string='Product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Product Status")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    active_ako = fields.Many2one('stock.picking')
    active_name = fields.Many2one('stock.picking')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)
    teams = fields.Many2one('team.configuration')
    dmg_type = fields.Selection([
        ('physical','Physical Damage'),
        ('boot','Not Bootable'),
        ('power','No Power')
    ], string="Damage Type")



class ValidationProcess(models.TransientModel):
    _inherit ='stock.immediate.transfer'
        # bypass mark as to do since it was remove
    @api.multi
    def process(self):
        self.ensure_one()
        # If still in draft => confirm and assign
        if self.pick_id.state == 'draft'  :
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



