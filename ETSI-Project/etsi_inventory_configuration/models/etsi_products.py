from odoo import api, fields, models
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class ProductTemplateInheritance(models.Model):
    _inherit = 'product.template'
    description_txt = fields.Text(string="Description:")

    product_count = fields.Integer(compute ='get_product_count')

    @api.multi
    def serial_location(self):
         
        return {
            'name': 'serials.items.list',
            'type': 'ir.actions.act_window',
            'res_model': 'etsi.inventory',
            'view_mode': 'tree,form',
            'domain': [('etsi_product_id.id', '=', self.id )]
        }

    def get_product_count(self):
        for rec in self:
            count = self.env['etsi.inventory'].search_count([('etsi_product_id.id', '=', rec.id)])
            rec.product_count = count



# serial smart button content

class Product_Serial_SmartButton(models.Model):

    _name = 'etsi.inventory'
    _rec_name = 'etsi_product_id'


    etsi_serial = fields.Char(string="Serial ID", required=True)
    etsi_mac = fields.Char(string="MAC ID")
    etsi_status = fields.Selection([('available', 'Available'),('used', 'Used')], string="Status", default='available', readonly=True)
    etsi_product_id = fields.Many2one('product.product',string="Product")
    etsi_product_name = fields.Many2one('product.product',string="Product")

