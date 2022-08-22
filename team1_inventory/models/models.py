# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class team1_inventory(models.Model):
    _inherit = 'product.template'

    description_txt = fields.Text(string="Description:")
    product_count = fields.Integer(compute ='get_product_count')

    # gawa ni llyod
    @api.multi
    def serial_location(self):
         
        return {
            'name': 'serials.items.list',
            'type': 'ir.actions.act_window',
            'res_model': 'etsi.inventory',
            'view_mode': 'tree,form',
            'domain': [('etsi_status_id.product_id', '=',self.id )]
        }

    def get_product_count(self):
        for rec in self:

            count = self.env['etsi.inventory'].search_count([('etsi_status_id.product_id', '=', rec.id)])
            rec.product_count = count

class testing(models.Model):
    _inherit = 'stock.picking'
    # subscriber_checkbox = fields.Boolean('Subscriber')
    min_date = fields.Datetime(compute='_compute_dates', inverse='_set_min_date', store=True,
        index=True, track_visibility='onchange',default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking.type'

    subscriber_checkbox = fields.Boolean('Subscriber')

    # @api.onchange('code')
    # def onchange_picking_code_2(self):
    #     if self.code == 'incoming':
    #         self.default_location_src_id = self.env.ref('stock.stock_location_suppliers').id
    #         self.default_location_dest_id =
    #  self.env.ref('stock.stock_location_stock').id
    #     elif self.code == 'outgoing':
    #         self.default_location_src_id = self.env.ref('stock.stock_location_stock').id
    #         self.default_location_dest_id = self.env.ref('stock.stock_location_customers').id



# gawa ni jawara

class InheritProduct(models.TransientModel):

    _inherit='stock.change.product.qty'
    # _rec_name='product_id'

    # inverse_value = fields.Float(default=1)
    new_quantity = fields.Float(string="testing")
    etsi_product_items_ids = fields.One2many('etsi.inventory', 'etsi_status_id')



    @api.onchange('etsi_product_items_ids')
    def update_product_qty(self):
        # self.new_quantity = 0
        for record in self.etsi_product_items_ids:
            self.new_quantity = self.new_quantity + record.etsi_quantity

    
    @api.onchange('etsi_product_items_ids')
    def get_product_count2(self):
        # count3 = self.search([('etsi_status_id.product_id','=',vals['etsi_status_id.product_id'])])
        # if len(count3) > 0:
        #     raise ValidationError("Product/Material exists!")
        print("outside")
        for rec in self:
            print("inside")
            # count = self.env['etsi.inventory'].search_count([('etsi_status_id.product_id', '=', rec.product_id.id)])
            count = self.env['etsi.inventory'].search([('etsi_status_id.product_id', '=', rec.product_id.id)])

            print("count=",count)
            print("countlen=",len(count))

            rec.new_quantity = len(count)
            # rec.write({'new_quantity':len(count)})
            # self.new_quantity.write({'result':0})
            print(self.new_quantity)


    # def _inverse_count(self):
    #     for rec in self:
    #         rec.inverse_value = rec.inverse_value + 10


    # oNLOAD

    # @api.model
    # def default_get(self, fields):
    #     nat = True
    #     if nat:
    #         print("nah")
    #         result = super(InheritProduct, self).default_get(fields)
    #         result['new_quantity'] = 3.00
    #         return result

    @api.onchange('location_id')
    def onchange_location_id(self):
        # count3 = self.search([('etsi_status_id.product_id','=',vals['etsi_status_id.product_id'])])
        # if len(count3) > 0:
        #     raise ValidationError("Product/Material exists!")
        print("outside")
        for rec in self:
            print("inside")
            # count = self.env['etsi.inventory'].search_count([('etsi_status_id.product_id', '=', rec.product_id.id)])
            count = self.env['etsi.inventory'].search([('etsi_status_id.product_id', '=', rec.product_id.id)])

            print("count=",count)
            print("countlen=",len(count))

            # rec.new_quantity = len(count)
            # self.new_quantity= len(count)
            rec.write({'new_quantity':len(count)})
            # self.new_quantity.write({'result':0})
            print(self.new_quantity)


class Product(models.TransientModel):

    _name = 'etsi.inventory'
    _rec_name = 'etsi_status_id'


    etsi_serial = fields.Char(string="Serial ID", required=True)
    etsi_mac = fields.Char(string="MAC ID")
    etsi_status = fields.Selection([('new', 'New'),('used', 'Used')], string="Status", default='new', readonly=True)
    etsi_quantity = fields.Float(string= "Quantity", readonly=True, default=1)
    etsi_status_id = fields.Many2one('stock.change.product.qty')
    id_domain = fields.Many2one(related='etsi_status_id.product_id')