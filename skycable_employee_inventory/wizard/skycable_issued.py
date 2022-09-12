from odoo import models, fields, api,_
from odoo.exceptions import UserError

class IssuedTransient(models.TransientModel):
    _name='stock.picking.issued'
    test_name = fields.Char(string="NAME: ")
    test_age = fields.Integer('AGE: ')  

    skycable_subscriber_id = fields.Many2one('res.partner', required=True)
    skycable_issued_destination_location = fields.Many2one('stock.location')

    skycable_issued_subscriber_ids = fields.One2many(
        'stock.picking.issued.subscriber', 'skycable_issued_subscriber_id')
    

# .write
# .create

    @api.model
    def default_get(self, fields):

        res = super(IssuedTransient, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        create_subscriber = self.env['stock.picking']
        product_all_values = []
        product_all_values2 = []
        if picking:
            print(picking.location_dest_id.name)
            print(picking.location_dest_id.name)
            print(picking.location_dest_id.name)
            print(picking.location_dest_id.name)


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

           

        # if create_subscriber:
        #     for subs in create_subscriber.move_lines:
        #         product_all_values2.append((0,0,{
        #             'skycable_issued_product_name':move.product_id.id,
        #             'skycable_issued_serial' : move.etsi_serials_field,
        #             'skycable_issued_mac':move.etsi_mac_field, 
        #             'skycable_issued_card': move.etsi_smart_card_field
        #         }))
        



        return res





    #edit ko pq to bukas -jaw
    @api.multi
    def validate_btn(self):

      
        # picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        # # create_picking = self.
        # sub = self.env['stock.picking']
       
        # if picking:
        #     for move in self.skycable_issued_subscriber_ids:
        #         product_all_values=[]
        #         product_all_values_new=[]
        #         for move2 in picking.move_lines:
        #             if move.skycable_issued_serial == move2.etsi_serials_field:

        #                 move2.origin = move2.name
        #                 move2.issued_field = "Yes"
        #                 move2.subscriber_field = self.skycable_subscriber_id.id
        #                 move2.checker_box = False
                        
        lst = []
        for line in self.skycable_issued_subscriber_ids:
            res = {
                'etsi_serials_field': line.skycable_issued_serial,
                'etsi_mac_field': line.skycable_issued_mac,
                'etsi_smart_card_field': line.skycable_issued_card,
            }

            lst.append(res)

        new_list = []

        for line2 in lst:
            new_list.append((0,0,line2))

        get_all_data = self.env['stock.picking']
        
        
        picking_checker = self.env['stock.picking.type'].search([('name', '=', 'Subscriber Issuance')])
        Uom = self.env['product.uom']
        stock_shot = self.env['stock.move']

        get_all_data.create({
            'picking_type_id': picking_checker.id,
            'partner_id': self.skycable_subscriber_id.id,
            'move_lines': new_list,
            'location_id': picking_checker.default_location_src_id.id,
            'location_dest_id': picking_checker.default_location_dest_id.id,
            # 'product_uom': Uom.id,
            })


        stock_shot.create({
            'product_uom': Uom.id,
        })
        # get_all_data.do_new_transfer()
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        print(picking_checker.id)
        return




class SubscribeIssued(models.TransientModel):
    _name = 'stock.picking.issued.subscriber'
    
    
    skycable_issued_subscriber_id = fields.Many2one('stock.picking.issued', 'list')
    skycable_issued_product_id = fields.Many2one('stock.move')
    skycable_issued_product_name = fields.Many2one(related='skycable_issued_product_id.product_id',string='Product ID')
    skycable_issued_serial = fields.Char('Serial ID')
    skycable_issued_mac = fields.Char('Mac ID')
    skycable_issued_card = fields.Char('Smart Card')
    


   
        


 
 

