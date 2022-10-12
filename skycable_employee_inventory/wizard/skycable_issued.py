
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class IssuedTransient(models.TransientModel):
    # _inherit ='stock.immediate.transfer'
    _name='stock.picking.issued'
    test_name = fields.Char(string="NAME: ")
    test_age = fields.Integer('AGE: ')  

    skycable_subscriber_id = fields.Many2one('res.partner', required=True)
    skycable_issued_destination_location = fields.Many2one('stock.location')

    skycable_issued_subscriber_ids = fields.One2many(
        'stock.picking.issued.subscriber', 'skycable_issued_subscriber_id')

    @api.model
    def default_get(self, fields):
        res = super(IssuedTransient, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        create_subscriber = self.env['stock.picking']
        product_all_values = []
        product_all_values2 = []
        if picking:
            for move in picking.move_lines:
                if move.checker_box is True:
         
                    product_all_values.append((0,0,{'skycable_issued_product_name':move.product_id.id,
                                                    'skycable_issued_serial' : move.etsi_serials_field,
                                                    'skycable_issued_mac':move.etsi_mac_field, 
                                                    'skycable_issued_card': move.etsi_smart_card_field}))
            if not product_all_values:
                raise UserError(_("There are no products to be issued"))
            if 'skycable_issued_subscriber_ids' in fields:
                res.update({'skycable_issued_subscriber_ids':product_all_values})

        return res

    @api.multi
    def validate_btn(self):
      
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        picking_checker = self.env['stock.picking.type'].search([('code', '=', 'outgoing'),('subscriber_checkbox', '=', True),('return_picking_type_id', '!=', False)])
        # sub = self.env['stock.picking']
       
        if picking:
            for move in self.skycable_issued_subscriber_ids:
                for move2 in picking.move_lines:
                    if move.skycable_issued_serial == move2.etsi_serials_field:
                        move2.checker_box = False

        Uom = self.env['product.uom'].search([], limit=1)
        lst = []
        for line in self.skycable_issued_subscriber_ids:
            res = {
                'name':line.skycable_issued_product_id.product_tmpl_id.name,
                'origin':line.skycable_issued_product_id.product_tmpl_id.name,
                'product_id': line.skycable_issued_product_id.id,
                'etsi_serials_field': line.skycable_issued_serial,
                'etsi_mac_field': line.skycable_issued_mac,
                'etsi_smart_card_field': line.skycable_issued_card,
                'subscriber_field': self.skycable_subscriber_id.id,
                'issued_field': "Yes",
                'product_uom': line.skycable_issued_product_id.product_tmpl_id.uom_id.id,
                'picking_type_id': picking_checker.id,
            }

            lst.append(res)

        new_list = []

        for line2 in lst:
            new_list.append((0,0,line2))


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

        get_all_data = self.env['stock.picking']
        # stock_immediate  = self.env['stock.immediate.transfer'].search([], limit=1).process()
        # picking_checker = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])

        if picking:
        
            runfunctiontest = get_all_data.create({
                'etsi_team_issuance_id': picking.id,
                'picking_type_id': picking_checker.id,
                'partner_id': self.skycable_subscriber_id.id,
                'origin': picking.name,
                'move_lines': new_list,
                'location_id': picking_checker.default_location_src_id.id,
                'location_dest_id': picking_checker.default_location_dest_id.id,
                'etsi_teams_id':  picking.etsi_teams_id.id,
                'etsi_teams_line_ids':  team_new_list,
                
                
                })

        runfunctiontest.action_assign()
     
        return {
                    'name': _("Subscriber Issuance"),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.picking',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': runfunctiontest.id,
                    # 'views': [(self.env.ref('survey.survey_form', False).id or False, 'form'), ],
                    # 'context': {'show_mrf_number': True},
                    'target': 'current',
                }

class SubscribeIssued(models.TransientModel):
    _name = 'stock.picking.issued.subscriber'
    
    
    skycable_issued_subscriber_id = fields.Many2one('stock.picking.issued', 'list')
    skycable_issued_product_id = fields.Many2one('product.product')
    skycable_issued_product_name = fields.Many2one(related='skycable_issued_product_id',string='Product ID')
    skycable_issued_serial = fields.Char('Serial ID')
    skycable_issued_mac = fields.Char('Mac ID')
    skycable_issued_card = fields.Char('Smart Card')
    


    
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

class functionWizard(models.Model):
    _inherit = 'stock.move'

    def testing1212(self):
        return {

            'name': 'Convert Transient',
            'res_model': 'stock.move.test',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('skycable_employee_inventory.stock_move_test_transient').id,
            'context': {'default_matcode':self.product_id.id}
            
            # 'test':self.id
            
        }

class convert_transient(models.TransientModel):
    _name='stock.move.test'

    matcode = fields.Many2one('product.product' , string="Material Code:",readonly="True")
    currentquantity = fields.Integer(string="Current Quantity",compute='_get_current_quantity',readonly="True")
    employeename = fields.Char(string="Employee Name", default=lambda self: self.env.user.name)
    current_unit = fields.Char(readonly=True, string="Units", related='matcode.product_tmpl_id.uom_id.name')


    sky_drops_reference_wiz = fields.Char(related='matcode.product_tmpl_id.drops_reference_id.drops_references')

    # NEXT LINE IS OUR MATERIAL CODE 
    drops_type_convert_to = fields.Many2one('product.template')
    initial_current_quantity= fields.Float(compute='_get_initial_current_quantity')    
    converted_units = fields.Char(related='drops_type_convert_to.uom_id.name',readonly=True)


    quantity_you_want_to_convert = fields.Float(required=True)

    @api.multi
    @api.depends('currentquantity','matcode' )
    def _get_current_quantity(self):
        product = self.env['product.product'].browse(self.matcode.id)
        current = product.with_context({'location' : 'WH/Stock'}).qty_available
        self.currentquantity = current

    @api.depends('initial_current_quantity', 'drops_type_convert_to')
    def _get_initial_current_quantity(self):
        product = self.env['product.product'].browse(self.drops_type_convert_to.id)
        current = product.with_context({'location' : 'WH/Stock'}).qty_available
        self.initial_current_quantity = current


    

    @api.multi
    def convert_btn(self):
        if(self.drops_type_convert_to.id != False and self.quantity_you_want_to_convert != 0):
            # product01
            if(self.matcode.product_tmpl_id.uom_id.uom_type == 'reference'):
                product01_uom_value = 1
            elif(self.matcode.product_tmpl_id.uom_id.uom_type == 'bigger'):
                product01_uom_value = self.matcode.product_tmpl_id.uom_id.factor_inv
            else:
                product01_uom_value = self.matcode.product_tmpl_id.uom_id.factor

            # product02
            if(self.drops_type_convert_to.uom_id.uom_type == 'reference'):
                product02_uom_value = 1
            elif(self.drops_type_convert_to.uom_id.uom_type == 'bigger'):
                product02_uom_value = self.drops_type_convert_to.uom_id.factor_inv
            else:
                product02_uom_value = self.drops_type_convert_to.uom_id.factor
            
            if(product01_uom_value < product02_uom_value):
                availabletoconvert = self.quantity_you_want_to_convert/product02_uom_value
                
                if(int(availabletoconvert) <= 0):
                    print("error")
                else:
                    convertedvalue = int(availabletoconvert) * product02_uom_value
                    product01newvalue = self.currentquantity - convertedvalue
                    product02newvalue = self.initial_current_quantity + int(availabletoconvert)
                    print("product01 new value:" , product01newvalue)
                    print("product02 new value:" , product02newvalue)
                    print("value added to product02:" , int(availabletoconvert))
            else:
                availabletoconvert = self.quantity_you_want_to_convert * product01_uom_value

                if(int(availabletoconvert) <= 0):
                    print("error")
                else:
                    convertedvalue = int(availabletoconvert) / product02_uom_value
                    product01newvalue = self.currentquantity - self.quantity_you_want_to_convert
                    product02newvalue = self.initial_current_quantity + convertedvalue
                    print("product01 new value:" , product01newvalue)
                    print("product02 new value:" , product02newvalue)
                    print("value added to product02:" , int(convertedvalue))
                