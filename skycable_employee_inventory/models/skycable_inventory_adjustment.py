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

    @api.multi
    @api.onchange('line_ids')
    def remove_connected(self):
        checker1 =[]
        result =[]
        result2 =[]
        for rec in self:
            for checkdata in self.line_ids:
                checker1.append(checkdata.product_id.id)

            for record in self.line_ids:
                for line in self.etsi_product_detail:
                    if line.etsi_products.id not in checker1:
                        pass
                    else:
                        result.append((
                         0, 0, {
                        'etsi_serials':line.etsi_serials,
                        'etsi_macs': line.etsi_macs,
                        'etsi_products': line.etsi_products.id,
                        }))
            
            for record in self.line_ids:
                for line in self.etsi_product_detail_2:
                    if line.etsi_products_2.id not in checker1:
                        pass
                    else:
                        result2.append((
                         0, 0, {
                        'etsi_serials_2':line.etsi_serials_2,
                        'etsi_smart_card_2': line.etsi_smart_card_2,
                        'etsi_products_2': line.etsi_products_2.id,
                        }))
            a = [ item for pos,item in enumerate(result) if result.index(item)==pos ]
            b = [ item for pos,item in enumerate(result2) if result2.index(item)==pos ]

            self.etsi_product_detail = a
            self.etsi_product_detail_2 = b

    
    @api.depends('line_ids')
    def get_count_lineids2(self):
        for rec in self:
            count = len(self.line_ids)
            rec.lineidscount2 = count

    @api.multi
    @api.onchange('etsi_product_detail','etsi_product_detail_2')
    def add_quantity_method(self): 
        for rec in self:
            test2 = []
            test = []

            for line in self.line_ids:
                if line not in test2:
                    test2.append(line.product_id.id)


            for line2 in self.etsi_product_detail:
                test.append((
                    0, 0, {
                        'product_id': line2.etsi_products.id,
                        'location_id': self.location_id.id,
                        'company_id': self.company_id.id,
                        'product_uom_id': line2.etsi_products.product_tmpl_id.uom_id.id,
                        
                    }
                ))

            for line2 in self.etsi_product_detail_2:
                test.append((
                    0, 0, {
                        'product_id': line2.etsi_products_2.id,
                        'location_id': self.location_id.id,
                        'company_id': self.company_id.id,
                        'product_uom_id': line2.etsi_products_2.product_tmpl_id.uom_id.id,
                        
                    }
                ))

            
            removing_duplicate = [ item for pos,item in enumerate(test) if test.index(item)==pos ]


            self.line_ids = removing_duplicate
          

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

    # @api.onchange('etsi_product_detail_2')
    # def add_quantity_method2(self):

    #     for rec in self:
    #         test2 = []
    #         test = []

    #         for line in self.line_ids:
    #             if line not in test2:
    #                 test2.append(line.product_id.id)


    #         for line2 in self.etsi_product_detail_2:
    #             test.append((
    #                 0, 0, {
    #                     'product_id': line2.etsi_products_2.id,
    #                     'location_id': self.location_id.id,
    #                     'company_id': self.company_id.id,
    #                     'product_uom_id': line2.etsi_products_2.product_tmpl_id.uom_id.id,
                        
    #                 }
    #             ))

            
    #         removing_duplicate = [ item for pos,item in enumerate(test) if test.index(item)==pos ]


    #         self.line_ids = removing_duplicate

        


    #     for line in self.line_ids:
    #         count = line.theoretical_qty
    #         for line2 in self.etsi_product_detail:
    #             if line.product_id.id == line2.etsi_products.id:
    #                 count += 1
    #         line.product_qty = count
    #         for line3 in self.etsi_product_detail_2:
    #             if line.product_id.id == line3.etsi_products_2.id:
    #                 count += 1
    #         line.product_qty = count
      
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
                
        # VALIDATION FOR MODEM: NO SERIAL AND MAC ID DUPLICATE
        if 'etsi_product_detail'  in vals:
            # Validation for empty table
            is_empty = True
            for record in vals['etsi_product_detail']:
                if record[0] != 2:
                    is_empty = False
            if is_empty == True:
                raise ValidationError(('Modem Table cant be Empty.'))
            
            # container of created datas
            created_serial = []
            created_mac = []
            # container of updated datas
            updated_serial = []
            updated_mac = []
            
            # Search all data from database -> etsi.product.detail.line
            search = self.env['etsi.product.detail.line'].search([]) 
            # count data
            counter = 0
            # Fetch product detail
            for rec in vals['etsi_product_detail']:
                # Get dictionary data
                test = rec[2]
                if rec[0] == 0: # If created data triggered
                    serials = []
                    smart = []
                    # count existing serial and mac id in CATV
                    search_data = self.env['etsi.product.detail.line.two'].search([]) # OR Statement
                                                                                 
                    for yawa in search_data:
                        serials.append(yawa.etsi_serials_2)
                        smart.append(yawa.etsi_smart_card_2)
                    
                    # Serial Duplicate
                    if test['etsi_serials'] in serials:
                        check = "Serial number already exists! \n Serial Number: {}".format(test['etsi_serials'])
                        raise ValidationError(check)
                    # if smart card and MODEM serial is the same
                    if test['etsi_serials'] in smart:
                        check = "Smart card and Serial cannot be the same! \n Duplicate: {}".format(test['etsi_serials'])
                        raise ValidationError(check)
                    # if smart card and MAC Id is the same
                    if test['etsi_macs'] in smart:
                        check = "Smart card and MAC ID cannot be the same! \n Duplicate: {}".format(test['etsi_macs'])
                        raise ValidationError(check)
                    # if CATV serial and MAC Id is the same
                    if test['etsi_macs'] in serials:
                        check = "Serial and MAC ID cannot be the same! \n Duplicate: {}".format(test['etsi_macs'])
                        raise ValidationError(check)
                    # if smart card and MODEM serial is the same
                    if test['etsi_serials'] in smart:
                        check = "Smart card and serial cannot be the same! \n Duplicate: {}".format(test['etsi_serials'])
                        raise ValidationError(check)
                    
                    # append all data to existing list
                    if 'etsi_serials' in test:
                        created_serial.append(test['etsi_serials'])
                    if 'etsi_macs' in test:
                        created_mac.append(test['etsi_macs'])
                    
                elif rec[0] == 1: # If edit / update data triggered
                    serials = []
                    smart = []
                    # count existing serial and mac id in CATV
                    search_data = self.env['etsi.product.detail.line.two'].search([]) # OR Statement
                                                                                 
                    for yawa in search_data:
                        serials.append(yawa.etsi_serials_2)
                        smart.append(yawa.etsi_smart_card_2)
                    
                    # Serial Duplicate
                    if test['etsi_serials'] in serials:
                        check = "Serial number already exists! \n Serial Number: {}".format(test['etsi_serials'])
                        raise ValidationError(check)
                    # if smart card and MODEM serial is the same
                    if test['etsi_serials'] in smart:
                        check = "Smart card and Serial cannot be the same! \n Duplicate: {}".format(test['etsi_serials'])
                        raise ValidationError(check)
                    # if smart card and MAC Id is the same
                    if test['etsi_macs'] in smart:
                        check = "Smart card and MAC ID cannot be the same! \n Duplicate: {}".format(test['etsi_macs'])
                        raise ValidationError(check)
                    # if CATV serial and MAC Id is the same
                    if test['etsi_macs'] in serials:
                        check = "Serial and MAC ID cannot be the same! \n Duplicate: {}".format(test['etsi_macs'])
                        raise ValidationError(check)
                    # if smart card and MODEM serial is the same
                    if test['etsi_serials'] in smart:
                        check = "Smart card and serial cannot be the same! \n Duplicate: {}".format(test['etsi_serials'])
                        raise ValidationError(check)
                    
                    # append all data to existing list
                    if 'etsi_serials' in test:
                        updated_serial.append(test['etsi_serials'])
                    if 'etsi_macs' in test:
                        updated_mac.append(test['etsi_macs'])
                if test:
                    if 'etsi_serials' in test:
                        # Check if the serial field is null
                        if test['etsi_serials'] == False:
                            raise ValidationError(_('Serial Number cannot be empty!'))

            # Fetch all data
            for searched in search:
                # Validation: NO Duplicate serial number
                if searched.etsi_serials in updated_serial or searched.etsi_serials in created_serial:
                    check = "Serial number already exists! \n Serial Number: {}".format(searched.etsi_serials)
                    raise ValidationError(check)
                # Validation: NO Duplicate MAC ID
                if searched.etsi_macs == updated_mac or searched.etsi_macs in created_mac:
                    if searched.etsi_macs == False:
                        pass
                    else:
                        check = "MAC ID already exists! \n MAC ID: {}".format(searched.etsi_macs)
                        raise ValidationError(check)
                # Validation: NO Serial and MAC Id is the same
                for val_serial in created_serial:
                    if val_serial in created_mac:
                        check = "Duplicate detected within the form Serial and MAC ID is the same \n Serial Number and MAC: {}".format(val_serial)
                        raise ValidationError(check)
                for val_serial2 in updated_serial:
                    # Within the database / Line one in O2M 
                    # if Serial Number triggered
                    if val_serial2 == searched.etsi_macs:
                        check = "Duplicate detected within the form Serial and MAC ID is the same \n Serial Number and MAC: {}".format(val_serial2)
                        raise ValidationError(check)
                    if val_serial2 == searched.etsi_macs:
                        check = "Duplicate detected within the form Serial and MAC ID is the same \n Serial Number and MAC: {}".format(val_serial2)
                        raise ValidationError(check)
                    # Within the table of O2M
                    if val_serial2 in updated_mac:
                        check = "Duplicate detected within the form Serial and MAC ID is the same \n Serial Number and MAC: {}".format(val_serial2)
                        raise ValidationError(check)
                # if MAC ID triggered
                for valMac in updated_mac:
                    if valMac == searched.etsi_serials:
                        check = "Duplicate detected within the form Serial and MAC ID is the same \n Serial Number and MAC: {}".format(valMac)
                        raise ValidationError(check)
          
        # VALIDATION FOR CATV: NO SERIAL AND SMART CARD DUPLICATE
        if 'etsi_product_detail_2' in vals:
            # Validation for empty table
            is_empty = True
            for record in vals['etsi_product_detail_2']:
                if record[0] != 2:
                    is_empty = False
            if is_empty == True:
                raise ValidationError(('CATV Table cant be Empty.'))
            
            # container of created datas
            created_serial = []
            created_card = []
            # container of updated datas
            updated_serial = []
            updated_card = []
            # count data
            counter = 0
            # Fetch product detail
            for rec in vals['etsi_product_detail_2']:
                counter += 1
                # Search all data from database -> etsi.product.detail.line.two
                search = self.env['etsi.product.detail.line.two'].search([]) 
                # Get dictionary data
                test = rec[2]
                if rec[0] == 0: # If created data triggered
                    serials = []
                    mac = []
                    # search MODEM db
                    search_data = self.env['etsi.product.detail.line'].search([])
                                                                                 
                    for yawa in search_data:
                        serials.append(yawa.etsi_serials)
                        mac.append(yawa.etsi_mac)
                    
                    # Serial Duplicate
                    if test['etsi_serials_2'] in serials:
                        check = "Serial number already exists! \n Serial Number: {}".format(test['etsi_serials_2'])
                        raise ValidationError(check)
                    # if MAC and MODEM serial is the same
                    if test['etsi_serials_2'] in mac:
                        check = "MAC ID and serial number cannot be the same! \n Duplicate: {}".format(test['etsi_serials_2'])
                        raise ValidationError(check)
                    # if smart card and MAC Id is the same
                    if test['etsi_smart_card_2'] in mac:
                        check = "MAC ID and Smart card cannot be the same! \n Duplicate: {}".format(test['etsi_smart_card_2'])
                        raise ValidationError(check)
                    # if CATV serial and MAC Id is the same
                    if test['etsi_smart_card_2'] in serials:
                        check = "Serial and MAC ID cannot be the same! \n Duplicate: {}".format(test['etsi_smart_card_2'])
                        raise ValidationError(check)
                    # if smart card and MODEM serial is the same
                    if test['etsi_serials_2'] in mac:
                        check = "Smart card and serial cannot be the same! \n Duplicate: {}".format(test['etsi_serials_2'])
                        raise ValidationError(check)
                    
                    # append all data to existing list
                    if 'etsi_serials_2' in test:
                        created_serial.append(test['etsi_serials_2'])
                    if 'etsi_smart_card_2' in test:
                        created_card.append(test['etsi_smart_card_2'])

                elif rec[0] == 1: # If edit / update data triggered
                    serials = []
                    mac = []
                    # search MODEM db
                    search_data = self.env['etsi.product.detail.line'].search([])
                                                                                 
                    for yawa in search_data:
                        serials.append(yawa.etsi_serials)
                        mac.append(yawa.etsi_mac)
                    
                    # Serial Duplicate
                    if test['etsi_serials_2'] in serials:
                        check = "Serial number already exists! \n Serial Number: {}".format(test['etsi_serials_2'])
                        raise ValidationError(check)
                    # if MAC and MODEM serial is the same
                    if test['etsi_serials_2'] in mac:
                        check = "MAC ID and serial number cannot be the same! \n Duplicate: {}".format(test['etsi_serials_2'])
                        raise ValidationError(check)
                    # if smart card and MAC Id is the same
                    if test['etsi_smart_card_2'] in mac:
                        check = "MAC ID and Smart card cannot be the same! \n Duplicate: {}".format(test['etsi_smart_card_2'])
                        raise ValidationError(check)
                    # if CATV serial and MAC Id is the same
                    if test['etsi_smart_card_2'] in serials:
                        check = "Serial and MAC ID cannot be the same! \n Duplicate: {}".format(test['etsi_smart_card_2'])
                        raise ValidationError(check)
                    # if smart card and MODEM serial is the same
                    if test['etsi_serials_2'] in mac:
                        check = "Smart card and serial cannot be the same! \n Duplicate: {}".format(test['etsi_serials_2'])
                        raise ValidationError(check)
                    
                    # append all data to existing list
                    if 'etsi_serials_2' in test:
                        updated_serial.append(test['etsi_serials_2'])
                    if 'etsi_smart_card_2' in test:
                        updated_card.append(test['etsi_smart_card_2'])
                        
                if test:
                    if 'etsi_serials_2' in test:
                        # Check if the serial field is null
                        if test['etsi_serials_2'] == False:
                            raise ValidationError(_('Serial Number cannot be empty!'))
                        
            # Fetch all data
            for searched in search:
                # Validation: NO Duplicate serial number
                if searched.etsi_serials_2 in updated_serial or searched.etsi_serials_2 in created_serial:
                    check = "Serial number already exists! \n Serial Number: {}".format(searched.etsi_serials_2)
                    raise ValidationError(check)
                # Validation: NO Duplicate Smart card
                if searched.etsi_smart_card_2 in updated_card or searched.etsi_smart_card_2 in created_card:
                    if searched.etsi_smart_card_2 == False:
                        pass
                    else:
                        check = "Smart Card already exists! \n Smart Card: {}".format(searched.etsi_smart_card_2)
                        raise ValidationError(check)
                # Validation: NO Serial and Smart card is the same
                # Create Data
                for val_serial in created_serial:
                    # Within the table
                    if val_serial in created_card:
                        check = "Duplicate detected within the form Serial and Smart Card is the same \n Serial Number and Smart Card: {}".format(val_serial)
                        raise ValidationError(check)
                # Update Data
                for val_serial2 in updated_serial:
                    # Within the database / Line one in O2M 
                    # if Serial Number triggered
                    if val_serial2 == searched.etsi_smart_card_2:
                        check = "Duplicate detected within the form Serial and Smart Card is the same \n Serial Number and Smart Card: {}".format(val_serial2)
                        raise ValidationError(check)
                    # Within the table of O2M
                    if val_serial2 in updated_card:
                        check = "Duplicate detected within the form Serial and Smart Card is the same \n Serial Number and Smart Card: {}".format(val_serial2)
                        raise ValidationError(check)
                # if Smart Card triggered
                for valCard in updated_card:
                    if valCard == searched.etsi_serials_2:
                        check = "Duplicate detected within the form Serial and Smart Card is the same \n Serial Number and Smart Card: {}".format(valCard)
                        raise ValidationError(check)

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
        elif self.filter2=='others':
            pass
            
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
              