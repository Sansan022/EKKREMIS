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


    @api.multi
    def _validating_data(self):

        picking = self.env['stock.picking'].browse(self.env.context['active_id'])
        return_subscriber = self.skycable_issued_subscriber_ids.mapped('skycable_issued_product_name')

        for sub in return_subscriber:
            just_check_subs = self.env['stock.move'] | move.skycable_issued_serial

            while just_check_subs:
                current_subs = just_check_subs[-1]
                just_check_subs = just_check_subs[:1]

                print("current_subs {}".format(current_subs))
                print("current_subs {}".format(current_subs))
                print("current_subs {}".format(current_subs))
                print("current_subs {}".format(current_subs))

                print("check subs {}".format(just_check_subs))
                print("check subs {}".format(just_check_subs))
                print("check subs {}".format(just_check_subs))
                print("check subs {}".format(just_check_subs))
                if current_subs.state not in ('done','cancel') and current_subs.reserved_quant_ids:
                    print("pasok sa banga")

        new_picking =  picking.copy({
            'move_lines':[],
        })

        return picking

        



    #edit ko pq to bukas -jaw
    def validate_btn(self):
        print("HELO")
        print("HELO")
        print("HELO")
        print("HELO")
        print("HELO")
        print("HELO")

        # for _inWizard in self:

        #     #picking = _inWizard._validating_data()

        #     print(picking)
        #     print(picking)
        #     print(picking)

            
        #     print(_inWizard.skycable_subscriber_id.name)
        #     print(_inWizard.skycable_subscriber_id.name)
        #     print(_inWizard.skycable_subscriber_id.name)
        #     print(_inWizard.skycable_subscriber_id.name)
        #     print(_inWizard.skycable_subscriber_id.id)
        #     print(_inWizard.skycable_subscriber_id.id)
        #     print(_inWizard.skycable_subscriber_id)
        #     print(_inWizard.skycable_subscriber_id)
        #     print(_inWizard)
        #     print(_inWizard)
        #     print(_inWizard)
        




class SubscribeIssued(models.TransientModel):
    _name = 'stock.picking.issued.subscriber'
    
    
    skycable_issued_subscriber_id = fields.Many2one('stock.change.product.qty', 'list')
    skycable_issued_product_id = fields.Many2one('stock.move')
    skycable_issued_product_name = fields.Many2one(related='skycable_issued_product_id.product_id',string='Product ID')
    skycable_issued_serial = fields.Char('Serial ID')
    skycable_issued_mac = fields.Char('Mac ID')
    skycable_issued_card = fields.Char('Smart Card')


    skycable_issued_subscriber_ids = fields.One2many(
            'stock.picking.issued.subscriber', 'skycable_issued_subscriber_id', string="Issued"
        )


    
        


 
 

