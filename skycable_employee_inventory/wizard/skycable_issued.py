
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
        picking_checker = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
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
        picking_checker = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])

        if picking:
        
            runfunctiontest = get_all_data.create({
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
    


   
        


 
 

