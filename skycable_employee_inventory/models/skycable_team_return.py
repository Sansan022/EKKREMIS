from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class Validate_Team_Return(models.Model):
    _inherit = 'stock.picking'

    # picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
    teller = fields.Selection([('return', 'Return'),('others', 'Others')], default='others', readonly=True)
    # Maging many2one na to 
    source = fields.Char('Source')

    @api.model
    def default_get(self, fields):
        res = super(Validate_Team_Return, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        for rec in self:
            if picking: 
                self.teller = 'return'
        return res

    # One2many to list all items
    return_list = fields.One2many('stock.picking.return.list','return_list_connector')
    
    # Auto fill of return_list_code
    @api.onchange('source')
    def change_return_list(self):
        listahan = []
        for rec in self:
            
            search_first = self.env['stock.picking'].search([('name','=',rec.source)])

            for item in search_first:
                print(item.name)
                search_first2 = self.env['stock.move'].search([])
                for x in search_first2:
                    if x.picking_id.name == rec.source:
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
                            'active_ako' : x.picking_id.name
                        }
                        ))

        # Update the one2many table
            self.update({'return_list': listahan})
        # return super(TransferData, self).do_new_transfer()

# Transient Model to hold all that will be returned(same as product_return_moves)
class Return_list_holder(models.TransientModel):
    _name = 'stock.picking.return.list.holder'
    
    # One2many to list all items
    return_list_move = fields.One2many('stock.picking.return.list','return_list_moves_connector')
    return_list_move_holder =  fields.One2many('stock.picking.return.list_2','return_list_moves_connector_2')

    # Code when validate button is clicked 
    @api.multi
    def return_btn(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        database = self.env['stock.picking']
        Uom = self.env['product.uom'].search([], limit=1)
        # Pick up the return picking_type_id for return
        picking_type_id = picking.picking_type_id.id 
        # List for team return
        team_return = []
        # return for subscriber issuance
        subscriber_issuance = []
        team_return_damaged = []

        for line_ret in self.return_list_move_holder:
            # Damaged
            if line_ret.damage_checker == True:
                team_return_damaged.append({
                    'name':line_ret.product_id.product_tmpl_id.name,
                    'product_id': line_ret.product_id.id,
                    'etsi_serials_field': line_ret.etsi_serial_product,
                    'etsi_mac_field': line_ret.etsi_mac_product,
                    'etsi_smart_card_field': line_ret.etsi_smart_card,
                    'issued_field': "Return",
                    'product_uom': line_ret.product_id.product_tmpl_id.uom_id.id,
                    'quantity': line_ret.quantity, 
                    # Hard coded pa tong picking_type Id 
                    'picking_type_id': 6
                })

            else:
                team_return.append({
                'name':line_ret.product_id.product_tmpl_id.name,
                'product_id': line_ret.product_id.id,
                'etsi_serials_field': line_ret.etsi_serial_product,
                'etsi_mac_field': line_ret.etsi_mac_product,
                'etsi_smart_card_field': line_ret.etsi_smart_card,
                'issued_field': "Return",
                'product_uom': line_ret.product_id.product_tmpl_id.uom_id.id,
                'quantity': line_ret.quantity, 
                # Hard coded pa tong picking_type Id 
                'picking_type_id': 6
            })
            
        final_return_list = []
        final_return_list_damaged = []

        for line_return in team_return:
            final_return_list.append((0,0,line_return))
        
        for line_return_damage in team_return_damaged:
            final_return_list_damaged.append((0,0,line_return_damage))
    
        for items in final_return_list:
            print("Mga laman ng normal return list ")
            print(items)
        
        for items_damage in final_return_list_damaged:
            print("Mga laman ng damaged return list ")
            print(items_damage)
        
        # Pa bago pa ng name nito hehez
        listahan =[]
        listahan2 =[]
        listahan3 = []

        for rec in self:
            for lines in rec.return_list_move:
                listahan.append({
                'name': lines.product_id.product_tmpl_id.name,
                'product_id': lines.product_id.id,
                'serial': lines.etsi_serial_product, 
                'mac' : lines.etsi_mac_product,
                'smart_card' : lines.etsi_smart_card,
                'issue' : "Used",
                'product_uom' : lines.product_uom.id,
                'qty' : lines.quantity,
                'picking_type_id' : 6
                })
            for lines2 in rec.return_list_move_holder:
                listahan2.append(lines2.etsi_serial_product)  
        
        for fetch_serial_list in listahan:
            if fetch_serial_list['serial'] not in listahan2:
                listahan3.append(
                    ( 0,0,{
                    
                    'name' : fetch_serial_list['name'],
                    'product_id': fetch_serial_list['product_id'],
                    'etsi_serials_field' : fetch_serial_list['serial'],
                    'etsi_mac_field' : fetch_serial_list['mac'],
                    'issued_field': fetch_serial_list['issue'],
                    'product_uom': fetch_serial_list['product_uom'],
                    'quantity': fetch_serial_list['qty'], 
                    'picking_type_id': 6
                    }
                    ))

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

        # Create record for return 
        return_function = database.create({
            'picking_type_id': picking_type_id,
            # 'origin': self.picking_id.name,
            'move_lines': final_return_list,
            # create ka pa dito ng laman ng return_list(all items) 
            # Labo labo pa tong location_id 
            'location_id': 5,
            # Labo labo pa tong location_dest_id 
            'location_dest_id': 6,
            'state' : 'done',
            #Ayusin pa natin teams  
            'etsi_teams_id':  picking.etsi_teams_id.id,
            'etsi_teams_line_ids':  team_new_list,
            })

         # Create record for damaged return 
        picking_checker_damaged = self.env['stock.picking.type'].search([('name', '=', 'Warehouse to SkyCable Return')])
        # Create record for return 
        return_damaged_function = database.create({
            'picking_type_id': picking_checker_damaged.id,
            # 'origin': self.picking_id.name,
            'move_lines': final_return_list_damaged,
            # create ka pa dito ng laman ng return_list(all items) 
            # Labo labo pa tong location_id 
            'location_id': 5,
            # Labo labo pa tong location_dest_id 
            'location_dest_id': 6,
            'state' : 'done',
            #Ayusin pa natin teams  
            'etsi_teams_id':  picking.etsi_teams_id.id,
            'etsi_teams_line_ids':  team_new_list,
            })

        picking_checker = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
        
        # Create record for subscriber issuance
        issuance_function = database.create({
            # Shunn yung picking type id nito, hard code pa
            'picking_type_id': picking_checker.id,
            # 'origin': self.picking_id.name,
            'move_lines': listahan3,
            # Labo labo pa tong location_id 
            'location_id': 5,
            # Labo labo pa tong location_dest_id 
            'location_dest_id': 6,
            'state' : 'done',
            #Ayusin pa natin teams  
            # 'etsi_teams_id': self.etsi_teams_id2.id
            'etsi_teams_id':  picking.etsi_teams_id.id,
            'etsi_teams_line_ids':  team_new_list,
                
        })

        # Update quanity of serials from subscriber issuance
        # Code for updating status 
        product_lists = []
        product_serials = []

        product_lists_damaged = []
        product_serials_damaged = []

        product_lists_issued = []
        product_serials_issued = []

        final= []
        final_ids = []

        for rec in self:
            # if rec.picking_type_id.name == "Subscriber Return" or rec.picking_type_id.name == "Team Return":
            for plines_issued in rec.return_list_move:
                product_serials_issued.append(plines_issued.etsi_serial_product)
                product_lists_issued.append(plines_issued.product_id)

                for plines in rec.return_list_move_holder:
                    if plines.damage_checker == True:
                        product_lists_damaged.append(plines.product_id)
                        product_serials_damaged.append(plines.etsi_serial_product)
                    else:
                        product_lists.append(plines.product_id)
                        product_serials.append(plines.etsi_serial_product)

        for item in  product_serials_issued:
            if item not in product_serials:
                final.append(item)
        for items_ids in product_lists_issued:
            if items_ids in product_lists:
                final_ids.append(items_ids.id)
 
        issued_stats = self.env['stock.move'].search([])
        inventory_stats = self.env['etsi.inventory'].search([])

        if product_lists_damaged and product_serials_damaged:
            for issued_ids in issued_stats:
                if issued_ids.etsi_serials_field in product_serials_damaged:
                    issued_ids.update({'issued_field': 'Damaged'})
    
                    for searched_ids in inventory_stats:
                        if searched_ids.etsi_product_id in product_lists_damaged:
                            if searched_ids.etsi_serial in product_serials_damaged:
                                searched_ids.update({'etsi_status': 'used'})

        if product_lists and product_serials:
            for issued_ids in issued_stats:
                if issued_ids.etsi_serials_field in product_serials:
                    issued_ids.update({'issued_field': 'Available'})
    
                    for searched_ids in inventory_stats:
                        if searched_ids.etsi_product_id in product_lists:
                            if searched_ids.etsi_serial in product_serials:
                                searched_ids.update({'etsi_status': 'available'})

        if final and final_ids:
            for issued_ids in issued_stats:
                if issued_ids.etsi_serials_field in final:
                    issued_ids.update({'issued_field': 'Used'})

                    for searched_ids in inventory_stats:
                        if searched_ids.etsi_product_id.id in final_ids:
                            if searched_ids.etsi_serial in final:
                                searched_ids.update({'etsi_status': 'used'})

        # Update status of issued
        for fetch_serial_list in listahan:
            if fetch_serial_list['serial'] not in listahan2:
                listahan3.append(
                    ( 0,0,{
                    
                    'name' : fetch_serial_list['name'],
                    'product_id': fetch_serial_list['product_id'],
                    'etsi_serials_field' : fetch_serial_list['serial'],
                    'etsi_mac_field' : fetch_serial_list['mac'],
                    'issued_field': fetch_serial_list['issue'],
                    'product_uom': fetch_serial_list['product_uom'],
                    'quantity': fetch_serial_list['qty'], 
                    'picking_type_id': 6
                    }
                    ))

        # Execute the function 
        return_function.action_assign()
        issuance_function.action_assign()
        return_damaged_function.action_assign()

        return {
            'name': _("Team Return"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': return_function.id,
            # 'views': [(self.env.ref('survey.survey_form', False).id or False, 'form'), ],
            # 'context': {'show_mrf_number': True},
            'target': 'current',
        }

    @api.model
    def default_get(self, fields):
        res = super(Return_list_holder, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        return_list_move = []

        for move in picking.return_list:
            if picking.return_list:
                if move.etsi_smart_card:
                    return_list_move.append((
                        0, 0, {
                            'product_id': move.product_id.id, 
                            'quantity': move.quantity, 
                            # 'move_id': move.id, 
                            'product_uom' : move.product_uom.id,
                            'issued': move.issued,
                            'etsi_serial_product': move.etsi_serial_product, 
                            'etsi_smart_card': move.etsi_smart_card,
                            'subscriber' : move.subscriber,
                            'active_ako' : move.active_ako
                        }
                    ))

                # If MODEM is selected
                if move.etsi_mac_product:
                    return_list_move.append((
                        0, 0, {
                            'product_id': move.product_id.id, 
                            'quantity': move.quantity, 
                            # 'move_id': move.id, 
                            'product_uom' : move.product_uom.id,
                            'issued': move.issued,
                            'etsi_serial_product': move.etsi_serial_product, 
                            'etsi_mac_product': move.etsi_mac_product, 
                            'subscriber' : move.subscriber,
                            'active_ako' : move.active_ako
                        }
                    ))
        
        if not return_list_move:
            raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))

        if 'return_list_move' in fields:
                res.update({'return_list_move': return_list_move})

        if 'etsi_teams_id' in fields:

            res.update({'etsi_teams_id': picking.etsi_teams_id.id})
        return res


class Return_list_childs(models.TransientModel):
    _name = 'stock.picking.return.list'

    # Connects to return_list
    return_list_connector = fields.Many2one('stock.picking')
    # Connects to return_list_moves
    return_list_moves_connector = fields.Many2one('stock.picking.return.list.holder')

    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity')

    issued = fields.Char(string="Issued")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    subscriber = fields.Char("Subscriber")
    active_ako = fields.Char("Active Ako ")
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)


class Return_list_child(models.TransientModel):
    _name = 'stock.picking.return.list_2'

    # Connects to return_list
    return_list_connector = fields.Many2one('stock.picking')
    # Connects to return_list_moves
    return_list_moves_connector_2 = fields.Many2one('stock.picking.return.list.holder')

    damage_checker = fields.Boolean('Damaged')
    product_id =  fields.Many2one('product.product') 
    quantity = fields.Float('Quantity')
    issued = fields.Char(string="Issued")
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    subscriber = fields.Char("Subscriber")
    active_ako = fields.Char("Active Ako ")
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    product_uom_qty = fields.Float('Quantity',default=1.0)

    # Onchange Auto Fill Code     
    @api.multi 
    @api.onchange('etsi_serial_product','etsi_mac_product','etsi_smart_card')
    def onchange_transfer(self):
        # Validate Datas
        for rec in self:
            # search available products - stock.move model
            pm_search_sr = self.env['stock.move'].search([('etsi_serials_field','=', rec.etsi_serial_product)])
            pm_search_mc = self.env['stock.move'].search([('etsi_mac_field','=', rec.etsi_mac_product)])
            pm_search_sc = self.env['stock.move'].search([('etsi_smart_card_field','=', rec.etsi_smart_card)])
            
            # Lists
            p_lists_sr = []
            p_lists_mc = []
            p_lists_sc = []
            # search available products - stock.picking.return.list.holder model
            for p_holder in rec.return_list_moves_connector_2.return_list_move:
                # Store datas
                p_lists_sr.append(p_holder.etsi_serial_product)
                p_lists_mc.append(p_holder.etsi_mac_product)
                p_lists_sc.append(p_holder.etsi_smart_card)
            
            # Valued data only passes
            if rec.etsi_serial_product != False or rec.etsi_mac_product != False or rec.etsi_smart_card != False:
                # Check if data inputted is available
                # MAC ID
                if rec.etsi_mac_product:
                    if p_lists_mc[0] == False:
                        raise ValidationError("This product is CATV, there is no MAC ID!")
                    if rec.etsi_mac_product not in p_lists_mc:
                        raise ValidationError("MAC ID not available in returns!")
                    # Validation for issued status
                    for mac in pm_search_mc:
                        if mac.issued_field == "Yes":
                            raise ValidationError("This Product is already issued!")
                        if mac.issued_field == "Return":
                            raise ValidationError("Product is already returned!")
                            
                        # Auto fill statements
                        rec.product_id = mac.product_id.id
                        rec.etsi_serial_product = mac.etsi_serials_field
                        rec.etsi_smart_card = mac.etsi_smart_card_field
                        rec.issued = "Available"
                        rec.quantity = 1.00
                        rec.product_uom = 1
                        break
                    
                # Smart Card
                if rec.etsi_smart_card:
                    if p_lists_sc[0] == False:
                        raise ValidationError("This product is MODEM, there is no Smart Card!")
                    if rec.etsi_smart_card not in p_lists_sc:
                        raise ValidationError("Smart Card not available in returns!")
                    else:
                        # Validation for issued status
                        for scard in pm_search_sc:
                            if scard.issued_field == "Yes":
                                raise ValidationError("This Product is already issued!")
                            if scard.issued_field == "Return":
                                raise ValidationError("Product is already returned!")
                            
                            # Auto fill statements
                            rec.product_id = scard.product_id.id
                            rec.etsi_mac_product = scard.etsi_mac_field
                            rec.etsi_serial_product = scard.etsi_serials_field
                            rec.issued = "Available"
                            rec.quantity = 1.00
                            rec.product_uom = 1
                            break
                        
                # Serial Number
                if rec.etsi_serial_product:
                    if rec.etsi_serial_product not in p_lists_sr:
                        raise ValidationError("Serial not available in returns!")
                    else:
                        # Validation for issued status
                        for ser in pm_search_sr:
                            if ser.issued_field == "Yes":
                                raise ValidationError("This Product is already issued!")
                            if ser.issued_field == "Return":
                                raise ValidationError("Product is already returned!")
                            
                            # Auto fill statements
                            rec.product_id = ser.product_id.id
                            rec.etsi_mac_product = ser.etsi_mac_field
                            rec.etsi_smart_card = ser.etsi_smart_card_field
                            rec.issued = "Available"
                            rec.quantity = 1.00
                            rec.product_uom = 1
                            break