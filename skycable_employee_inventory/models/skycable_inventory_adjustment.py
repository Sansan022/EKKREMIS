from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError

class ProductDetails(models.Model):
    _inherit = 'stock.inventory'
    
    # fields
    etsi_product_detail =  fields.One2many('etsi.product.detail.line','etsi_product_ids')

    # Line Id counter 
    lineidscount2 =  fields.Integer(compute='get_count_lineids2')

    @api.depends('line_ids')
    def get_count_lineids2(self):
        for rec in self:
            count = len(self.line_ids)
            rec.lineidscount2 = count

    @api.onchange('etsi_product_detail')
    def add_quantity_method(self): 
        for line in self.line_ids:
            count = line.theoretical_qty
            for line2 in self.etsi_product_detail:
                if line.product_id.id == line2.etsi_products.id:
                    count += 1
            line.product_qty = count
    
    # Newly added write
    def write(self, vals):
        result = super(ProductDetails, self).write(vals)
        if 'line_ids' in vals:
            is_empty = True
            for record in vals['line_ids']:
                if record[0] != 2:
                    is_empty = False

            if is_empty == True:
                raise ValidationError(('Inventory Details Table cant be Empty.'))
        return result
        
   

    # @api.multi
    # def prepare_inventory(self):
    #     res = super(ProductDetails, self).prepare_inventory()

    #     if self.state =='confirm':
    #         print("CONFIRM")
    #         print("CONFIRM")
    #         print("CONFIRM")
    #         print("CONFIRM")
    #         if len(vals['etsi_product_detail']) == 0:
    #             raise ValidationError(('Table cant be Empty.'))
    #     return res


    # overide actiondone

    @api.multi
    def action_done(self):


        res = super(ProductDetails, self).action_done()

        if len(self.line_ids) == 0:
            raise ValidationError(('Inventory details table can not be empty.'))

    
        if len(self.etsi_product_detail) == 0:
            raise ValidationError(('Product details table can not be empty.'))
        else:
            for line in self.etsi_product_detail:
                self.env['etsi.inventory'].create(
                    {'etsi_serial': line.etsi_serials,
                    'etsi_mac':line.etsi_macs,
                    # 'etsi_status':line.etsi_status,
                    'etsi_product_id':line.etsi_products.id,
                    'etsi_product_name':line.etsi_products.id,
                    })
                    


        return res

    @api.constrains('etsi_product_detail')
    def check_unique_pname(self):
        for rec in self.etsi_product_detail:
            etsi_serial_duplicate = self.env['etsi.inventory'].search_count([('etsi_serial', '=', rec.etsi_serials)])
            etsi_mac_duplicate = self.env['etsi.inventory'].search_count([('etsi_mac', '=', rec.etsi_macs)])
            if rec.etsi_serials == False and rec.etsi_macs == False:
                check3 = "Product must have either Serial NUmber or Mac Number"
                raise ValidationError(check3)
            if etsi_serial_duplicate >= 1:
                check = "Duplicate detected within the database \n Serial Number: {}".format(rec.etsi_serials)
                raise ValidationError(check)
            elif etsi_mac_duplicate >= 1:
                check2 = "Duplicate detected within the database \n MAC Number: {}".format(rec.etsi_macs)
                raise ValidationError(check2)

    # @api.model
    # def create(self, vals):
    #     res = super(ProductDetails, self).create(vals)
    #     if vals.get('state') =='confirm':
    #         if len(vals['etsi_product_detail']) == 0:
    #             raise ValidationError(('Table cant be Empty.'))

    #     return res

    # @api.multi
    # def write(self, vals):
    #     if 'etsi_product_detail' in vals:
    #         is_empty = True
    #         for record in vals['etsi_product_detail']:

    #             if record[0] != 2:
    #                 is_empty = False

    #         if is_empty == True:
    #             raise ValidationError(('Table cant be Empty.'))
                
    #         if len(vals['etsi_product_detail']) == 0:
    #             raise ValidationError(('Table cant be Empty.'))

    filter = fields.Selection(selection='_selection_filter_test')

    # ******    HIDE RADIO BUTTONS (WIDGET): ALL PRODUCTS AND ONE PRODUCT CATEGORY
    @api.model
    def _selection_filter_test(self):
        """ Get the list of filter allowed according to the options checked
        in 'Settings\Warehouse'. """
        res_filter = [
            ('product', _('One product only')),
            ('partial', _('Select products manually'))]

        if self.user_has_groups('stock.group_tracking_owner'):
            res_filter += [('owner', _('One owner only')), ('product_owner', _('One product for a specific owner'))]
        if self.user_has_groups('stock.group_production_lot'):
            res_filter.append(('lot', _('One Lot/Serial Number')))
        if self.user_has_groups('stock.group_tracking_lot'):
            res_filter.append(('pack', _('A Pack')))
        return res_filter


class ProductAdjustment(models.Model):
    _name = 'etsi.product.detail.line'
    
    # test = fields.Many2one('stock.inventory')
    etsi_product_ids = fields.Many2one('stock.inventory')
    etsi_serials = fields.Char(string="Serial ID", )
    etsi_macs = fields.Char(string="MAC ID")
    etsi_products = fields.Many2one('product.product', string="Products", domain="[('etsi_product_detail', '=', self.etsi_product_ids)]", required=True)

    @api.model
    def _selection_filter(self):
        res_filter = [
            ('none', _('All products')),
            ('category', _('One product category')),
            ('product', _('One product only')),
            ('partial', _('Select products manually'))]
        return res_filter
    
    etsi_filter = fields.Selection(
        string='Inventory of', selection='_selection_filter',
        default='none',
        help="If you do an entire inventory, you can choose 'All Products' and it will prefill the inventory with the current stock.  If you only do some products  "
             "(e.g. Cycle Counting) you can choose 'Manual Selection of Products' and the system won't propose anything.  You can also let the "
             "system propose for a single product / lot /... ")

            

    @api.constrains('etsi_serials')
    def check_unique_pname2(self):
        check3 = self.etsi_product_ids.etsi_product_detail - self
        for rec2 in check3:
            if rec2.etsi_serials == self.etsi_serials:
                check4 = "Duplicate detected within the Table \n Serial Number: {}".format(rec2.etsi_serials)
                raise ValidationError(check4)

    @api.constrains('etsi_macs')
    def check_unique_pname3(self):
        check3 = self.etsi_product_ids.etsi_product_detail - self
        for rec2 in check3:
            if rec2.etsi_macs == self.etsi_macs:
                check4 = "Duplicate detected within the Table \n Mac Number: {}".format(rec2.etsi_macs)
                raise ValidationError(check4)






    
        

