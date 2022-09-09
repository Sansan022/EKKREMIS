from odoo import models, fields, api,_
from odoo.exceptions import UserError

class IssuedTransient(models.TransientModel):
    _name='stock.picking.issued'
    test_name = fields.Char(string="NAME: ")
    test_age = fields.Integer('AGE: ')  

    skycable_subscriber_id = fields.Many2one('res.partner', required=True)

    skycable_issued_subscriber_ids = fields.One2many(
        'stock.picking.issued.subscriber', 'skycable_issued_subscriber_id')
    



    @api.model
    def default_get(self, fields):

        res = super(IssuedTransient, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        product_all_values = []
        if picking:
            for move in picking.move_lines:
                if move.checker_box is True:
                    print("Nag trueeeee")
                    product_all_values.append((0,0,{'skycable_issued_product_name':move.product_id.id,
                                                    'skycable_issued_serial' : move.etsi_serials_field,
                                                    'skycable_issued_mac':move.etsi_mac_field, 
                                                    'skycable_issued_card': move.etsi_smart_card_field}))
            if not product_all_values:
                raise UserError(_("There are no products to be issued"))
            if 'skycable_issued_subscriber_ids' in fields:
                res.update({'skycable_issued_subscriber_ids':product_all_values})
            return res





    #edit ko pq to bukas -jaw
    def validate_btn(self):
      
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        product_all_values=[]
        if picking:
            for move in self.skycable_issued_subscriber_ids:
                for move2 in picking.move_lines:
                    if move.skycable_issued_serial == move2.etsi_serials_field:
                        move2.issued_field = "Yes"
                        move2.subscriber_field = self.skycable_subscriber_id.id
                        move2.checker_box = False
                        




class SubscribeIssued(models.TransientModel):
    _name = 'stock.picking.issued.subscriber'
    
    
    skycable_issued_subscriber_id = fields.Many2one('stock.picking.issued', 'list')
    skycable_issued_product_id = fields.Many2one('stock.move')
    skycable_issued_product_name = fields.Many2one(related='skycable_issued_product_id.product_id',string='Product ID')
    skycable_issued_serial = fields.Char('Serial ID')
    skycable_issued_mac = fields.Char('Mac ID')
    skycable_issued_card = fields.Char('Smart Card')


   
        


 
 

