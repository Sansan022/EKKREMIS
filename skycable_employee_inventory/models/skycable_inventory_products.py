from odoo import api, fields, models, tools, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.addons import decimal_precision as dp

class ProductTemplateInheritance(models.Model):
    _inherit = 'product.template'
    # _rec_name = 'etsi_product_id'

    description_txt = fields.Text(string="Description:")
    product_type = fields.Selection([('product','Product'),('material','Material')] , default ="product", string ="Product Type:")
    internal_ref_name = fields.Selection([('catv5', 'CATV5'), ('modem', 'MODEM')], string = "Internal Reference", default='catv5')
    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True,default='catv5')
    product_count = fields.Integer(compute ='get_product_count')

    @api.onchange('internal_ref_name')
    def product_type_func(self):
        print('safsafsafsasfa')
        if self.internal_ref_name == 'catv5':
            self.default_code = 'CATV5'
        else:
            self.default_code = 'MODEM'

    @api.multi
    def serial_location(self):
         
        return {
            'name': 'serials.items.list',
            'type': 'ir.actions.act_window',
            'res_model': 'etsi.inventory',
            'view_mode': 'tree,form',
            'domain': [('etsi_product_id', '=', self.name )]
        }

    def get_product_count(self):
        for rec in self:
            count = self.env['etsi.inventory'].search_count([('etsi_product_id', '=', rec.name)])
            rec.product_count = count



# serial smart button content

class Product_Serial_SmartButton(models.Model):

    _name = 'etsi.inventory'
    # _rec_name = 'etsi_product_id'


    etsi_serial = fields.Char(string="Serial ID")
    etsi_mac = fields.Char(string="MAC ID")
    etsi_status = fields.Selection([('available', 'Available'),('used', 'Used')], string="Status", default='available', readonly=True)
    etsi_product_id = fields.Many2one('product.product',string="Product")
    etsi_product_name = fields.Many2one('product.product',string="Product")

# update quantity on hand one2many content

class Product_Quanty_On_Hand_Model(models.TransientModel):

    _name = 'etsi.inventory.product'
    _rec_name = 'etsi_product_id_product'


    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card_product = fields.Char(string="Smart Card ID")
    etsi_status_product = fields.Selection([('available', 'Available'),('used', 'Used')], string="Status", default='available', readonly=True)
    etsi_product_id_product = fields.Many2one('stock.change.product.qty')
    etsi_product_name_product = fields.Many2one(related='etsi_product_id_product.product_id',string="Product")
    etsi_quantity = fields.Float(string= "Quantity", readonly=True, default=1)

    etsi_product_type = fields.Selection(related='etsi_product_name_product.internal_ref_name')

class Product_Quanty_On_Hand_Model_2(models.TransientModel):

    _name = 'etsi.inventory.product_2'
    _rec_name = 'etsi_product_id_product_2'


    etsi_serial_product_2 = fields.Char(string="Serial ID")
    etsi_mac_product_2 = fields.Char(string="MAC ID")
    etsi_smart_card_product_2 = fields.Char(string="Smart Card ID")
    etsi_status_product_2 = fields.Selection([('available', 'Available'),('used', 'Used')], string="Status", default='available', readonly=True)
    etsi_product_id_product_2 = fields.Many2one('stock.change.product.qty')
    etsi_product_name_product_2 = fields.Many2one(related='etsi_product_id_product_2.product_id',string="Product")
    etsi_quantity_2 = fields.Float(string= "Quantity", readonly=True, default=1)

    etsi_product_type_2 = fields.Selection(related='etsi_product_name_product_2.internal_ref_name')

class Inherit_Product_Quantity(models.TransientModel):

    _inherit='stock.change.product.qty'

    etsi_product_items = fields.One2many('etsi.inventory.product', 'etsi_product_id_product')
    etsi_product_items_2 = fields.One2many('etsi.inventory.product_2', 'etsi_product_id_product_2')
    new_quantity = fields.Float()
    new_quantity2 = fields.Float(compute='update_product_qty2', string='New Quantity on Hand')

    internal_ref_name_2 = fields.Selection(related='product_id.internal_ref_name', string = "Internal Reference")

    @api.onchange('etsi_product_items')
    def update_product_qty1(self):
 
        count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])
        self.new_quantity = len(count)
        self.new_quantity2 = len(count)

        for record in self.etsi_product_items:
            self.new_quantity += record.etsi_quantity
            self.new_quantity2 = self.new_quantity 

    def update_product_qty2(self):

        count = self.env['etsi.inventory'].search([('etsi_product_id.id', '=', self.product_id.id)])
        self.new_quantity = len(count)
        self.new_quantity2 = len(count)

        for record in self.etsi_product_items:
            self.new_quantity += record.etsi_quantity
            self.new_quantity2 = self.new_quantity 

    @api.multi
    def change_product_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        Inventory = self.env['stock.inventory']
        for wizard in self:
            product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
            line_data = wizard._prepare_inventory_line()
            # line_data2 = wizard._prepare_product_line()

            lst = []
            if self.internal_ref_name_2 == 'catv5':
                for line in self.etsi_product_items:
                    res = {
                        'etsi_serials': line.etsi_serial_product,
                        'etsi_macs': line.etsi_mac_product,
                        'etsi_products': line.etsi_product_name_product.id
                    }
                    lst.append(res)
            else:
                for line in self.etsi_product_items:
                    res = {
                        'etsi_serials': line.etsi_serial_product_2,
                        'etsi_smartcard': line.etsi_mac_product_2,
                        'etsi_products': line.etsi_product_name_product_2.id
                    }
                    lst.append(res)

            
            new_lst = []
            for x in lst:
                new_lst.append((0, 0, x))


            if wizard.product_id.id and wizard.lot_id.id:
                inventory_filter = 'none'
            elif wizard.product_id.id:
                inventory_filter = 'product'
            else:
                inventory_filter = 'none'
            inventory = Inventory.create({
                'name': _('INV: %s') % tools.ustr(wizard.product_id.name),
                'filter': inventory_filter,
                'product_id': wizard.product_id.id,
                'location_id': wizard.location_id.id,
                'lot_id': wizard.lot_id.id,
                'line_ids': [(0, 0, line_data)],
                'etsi_product_detail': new_lst,
            })
            inventory.action_done()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _prepare_inventory_line(self):
        product = self.product_id.with_context(location=self.location_id.id, lot_id=self.lot_id.id)
        th_qty = product.qty_available

        res = {
               'product_qty': self.new_quantity,
               'location_id': self.location_id.id,
               'product_id': self.product_id.id,
               'product_uom_id': self.product_id.uom_id.id,
               'theoretical_qty': th_qty,
               'prod_lot_id': self.lot_id.id,
        }

        return res

    @api.multi
    def _prepare_product_line(self):

        lst = []
        for line in self.etsi_product_items:
            res = {
                'etsi_serials': line.etsi_serial_product,
                'etsi_macs': line.etsi_mac_product,
                'etsi_products': line.etsi_product_name_product.id
            }
            lst.append(res[line])
        return lst



    # @api.multi
    # def change_product_qty(self):

    #     for line in self.etsi_product_items:
    #             self.env['etsi.product.detail.line'].create(
    #                 {'etsi_serials': line.etsi_serial_product,
    #                 'etsi_macs':line.etsi_mac_product,
    #                 'etsi_products':line.etsi_product_name_product.id
    #                 })

    #     res = super(Inherit_Product_Quantity, self).change_product_qty()
    #     return res

