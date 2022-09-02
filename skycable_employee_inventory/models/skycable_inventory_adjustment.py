from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError

class ProductDetails(models.Model):
    _inherit = 'stock.inventory'
    
    # fields
    etsi_product_detail =  fields.One2many('etsi.product.detail.line','etsi_product_ids')
    etsi_product_detail_2 =  fields.One2many('etsi.product.detail.line.two','etsi_product_ids_2')
    # Line Id counter 
    lineidscount2 =  fields.Integer(compute='get_count_lineids2')

    filter = fields.Selection(selection='_selection_filter_test')
    filter2 = fields.Selection(related='product_id.internal_ref_name')

    # Inventory Adjustment Sequence 
    name = fields.Char(required=True, copy=False, readonly=True, default = lambda self : ('New'))
    
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
            for line3 in self.etsi_product_detail_2:
                if line.product_id.id == line3.etsi_products_2.id:
                    count += 1
            line.product_qty = count

    @api.onchange('etsi_product_detail_2')
    def add_quantity_method2(self): 
        for line in self.line_ids:
            count = line.theoretical_qty
            for line2 in self.etsi_product_detail:
                if line.product_id.id == line2.etsi_products.id:
                    count += 1
            line.product_qty = count
            for line3 in self.etsi_product_detail_2:
                if line.product_id.id == line3.etsi_products_2.id:
                    count += 1
            line.product_qty = count
      
    # CREATE VALIDATION  
    @api.model
    def create(self, vals):
        vals['name']  = self.env['ir.sequence'].next_by_code('skycable.inventory.adjustment.sequence') or _('New')
        res = super(ProductDetails, self).create(vals)
        return res

    # WRITE VALIDATION
    @api.multi
    def write(self, vals):
        # FILTER VALIDATION: PREVENTS THE USER FROM ADDING DATA IF FILTER IS ONE PRODUCT ONLY
        if self.filter == 'product':
            # iF line_ids in vals
            if 'line_ids' in vals:
                counter = 0
                for line in vals['line_ids']:
                    counter += 1
                if counter != 1:
                    raise ValidationError('Product must not exceed to more than 1!')
                
        # # VALIDATION: NO SERIAL DUPLICATE
        # if 'etsi_product_detail'  in vals:
        #     # Fetch product etail
        #     for rec in vals['etsi_product_detail']:
        #         # Get dictionary data
        #         test = rec[2]
        #         if test: # If test == True
        #             # Search all data from database -> etsi.product.detail.line
        #             search = self.env['etsi.product.detail.line'].search([]) 
        #             # Fetch all data
        #             for searched in search:
        #                 # Validation: NO Duplicate serial number
        #                 if test['etsi_serials'] in searched.etsi_serials:
        #                     raise ValidationError('Serial number is already exists!')
        #                 # Validation: NO Duplicate MAC ID
        #                 if test['etsi_macs'] == searched.etsi_macs:
        #                     raise ValidationError('MAC ID is already exists!')
        
        # # VALIDATION: NO SMART CARD DUPLICATE
        # if 'etsi_product_detail_2' in vals:
        #     o2m_datas = []
        #     # fetch one2many datas
        #     for data in self.etsi_product_detail_2:
        #         print(data.etsi_serials_2)
        #         # store the datas to list
        #         o2m_datas.append(data.etsi_serials_2)
            
        #     # validate within the table
            
        #     # Fetch product detail
        #     # for rec in vals['etsi_product_detail_2']:
        #     #     # Get dictionary data\
        #     #     test = rec[2]
        #     #     if test: # If test == True
        #     #         # Search all data from database -> etsi.product.detail.line
        #     #         search = self.env['etsi.product.detail.line.two'].search([]) 
        #     #         # Fetch all data
        #     #         for searched in search:
        #     #             # Validation: NO Duplicate serial number
        #     #             if test['etsi_serials_2'] in searched.etsi_serials_2:
        #     #                 raise ValidationError('Serial number is already exists!', test['etsi_serials_2'])
        #     #             # Validation: NO Duplicate Smart Card
        #     #             if test['etsi_smart_card_2'] == searched.etsi_smart_card_2:
        #     #                 raise ValidationError('Smart Card is already exists!')
                        
        #     # [0, False, {u'etsi_filter': u'partial', u'etsi_products': 3, u'etsi_macs': False, u'etsi_serials': u'121212121212'}]


        # VALIDATION FOR INVENTORY DETAILS, CAN'T BE EMPTY
        if 'line_ids' in vals:
            is_empty = True
            for record in vals['line_ids']:
                if record[0] != 2:
                    is_empty = False

            if is_empty == True:
                raise ValidationError(('Inventory Details Table cant be Empty.'))
            
        return super(ProductDetails, self).write(vals)

    # overide actiondone
    @api.multi
    def action_done(self):
        res = super(ProductDetails, self).action_done()
        if len(self.line_ids) == 0:
            raise ValidationError(('Inventory details table can not be empty.'))

        if self.filter2 == 'modem':
            if len(self.etsi_product_detail) == 0:
                raise ValidationError(('Product details table can not be empty.'))
            for line in self.etsi_product_detail:
                self.env['etsi.inventory'].create(
                    {'etsi_serial': line.etsi_serials,
                    'etsi_mac':line.etsi_macs,
                    # 'etsi_status':line.etsi_status,
                    'etsi_product_id':line.etsi_products.id,
                    'etsi_product_name':line.etsi_products.id,
                    })
        elif self.filter2 == 'catv5':
            if len(self.etsi_product_detail_2) == 0:
                raise ValidationError(('Product details table can not be empty.'))
            for line in self.etsi_product_detail_2:
                self.env['etsi.inventory'].create(
                    {'etsi_serial': line.etsi_serials_2,
                    'etsi_smart_card':line.etsi_smart_card_2,
                    'etsi_product_id':line.etsi_products_2.id,
                    'etsi_product_name':line.etsi_products_2.id,
                    })
        else:
            if len(self.etsi_product_detail) == 0 and len(self.etsi_product_detail_2) == 0:
                raise ValidationError(('Product details table can not be empty.'))
            else:
                for line in self.etsi_product_detail:
                    self.env['etsi.inventory'].create(
                        {'etsi_serial': line.etsi_serials,
                        'etsi_mac':line.etsi_macs,
                        'etsi_product_id':line.etsi_products.id,
                        'etsi_product_name':line.etsi_products.id,
                        })
                for line in self.etsi_product_detail_2:
                    self.env['etsi.inventory'].create(
                        {'etsi_serial': line.etsi_serials_2,
                        'etsi_smart_card':line.etsi_smart_card_2,
                        'etsi_product_id':line.etsi_products_2.id,
                        'etsi_product_name':line.etsi_products_2.id,
                        })
        return res

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
    etsi_products = fields.Many2one('product.product', string="Products", required=True)
    type_checker = fields.Selection(related='etsi_products.internal_ref_name')

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
    def check_unique_serial(self):
        check1 = self.etsi_product_ids.etsi_product_detail - self
        for rec2 in check1:
            if rec2.etsi_serials == self.etsi_serials:
                check2 = "Duplicate detected within the Table \n Serial Number: {}".format(rec2.etsi_serials)
                raise ValidationError(check2)

    @api.constrains('etsi_macs')
    def check_unique_mac(self):
        check3 = self.etsi_product_ids.etsi_product_detail - self
        for rec2 in check3:
            if rec2.etsi_macs == self.etsi_macs:
                check4 = "Duplicate detected within the Table \n Mac Number: {}".format(rec2.etsi_macs)
                raise ValidationError(check4)

class ProductAdjustment_02(models.Model):
    _name = 'etsi.product.detail.line.two'

    etsi_product_ids_2 = fields.Many2one('stock.inventory')
    etsi_serials_2 = fields.Char(string="Serial ID")
    etsi_smart_card_2 = fields.Char(string="Smart Card")
    etsi_products_2 = fields.Many2one('product.product', string="Products", required=True)
    type_checker_2 = fields.Selection(related='etsi_products_2.internal_ref_name')

    @api.model
    def _selection_filter(self):
        res_filter = [
            ('none', _('All products')),
            ('category', _('One product category')),
            ('product', _('One product only')),
            ('partial', _('Select products manually'))]
        return res_filter

    
    etsi_filter_2 = fields.Selection(
        string='Inventory of', selection='_selection_filter',
        default='none',
        help="If you do an entire inventory, you can choose 'All Products' and it will prefill the inventory with the current stock.  If you only do some products  "
             "(e.g. Cycle Counting) you can choose 'Manual Selection of Products' and the system won't propose anything.  You can also let the "
             "system propose for a single product / lot /... ")
    
    @api.constrains('etsi_serials_2')
    def check_unique_serial_2(self):
        check5 = self.etsi_product_ids_2.etsi_product_detail_2 - self
        for rec2 in check5:
            if rec2.etsi_serials_2 == self.etsi_serials_2:
                check6 = "Duplicate detected within the Table \n Serial Number: {}".format(rec2.etsi_serials_2)
                raise ValidationError(check6)

    @api.constrains('etsi_smart_card_2')
    def check_unique_smart_card_2(self):
        check7 = self.etsi_product_ids_2.etsi_product_detail_2 - self
        for rec2 in check7:
            if rec2.etsi_smart_card_2 == self.etsi_smart_card_2:
                check8 = "Duplicate detected within the Table \n Smart Card: {}".format(rec2.etsi_smart_card_2)
                raise ValidationError(check8)

