from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError


class Team_issuance(models.Model):
    _inherit = 'stock.move'
    product_id_duplicate = fields.Many2one(related="product_id")
    etsi_serials_field = fields.Char(string="Serial ID")
    etsi_mac_field = fields.Char(string="Mac ID")
    etsi_smart_card_field = fields.Char(string="Smart Card")

    checker_box = fields.Boolean(string="Status")

    issued_field = fields.Char(string="Issued",default="No")
    subscriber_field = fields.Many2one('res.partner',string="Subcscriber")

    @api.multi
    @api.onchange('etsi_serials_field')
    def auto_fill_details_01(self): 
        for rec in self:
            database = self.env['etsi.inventory']
            duplicate_count = self.env['etsi.inventory'].search_count([('etsi_serial', '=', rec.etsi_serials_field)])

            if duplicate_count < 1 or rec.etsi_serials_field == False:
               pass
            else:
                test = database.search([('etsi_serial','=',rec.etsi_serials_field)])
                rec.product_id = test.etsi_product_id.id
                rec.etsi_serials_field = test.etsi_serial
                rec.etsi_mac_field = test.etsi_mac
                rec.etsi_smart_card_field = test.etsi_smart_card



class Team_issuance_stock_picking(models.Model):
    _inherit = 'stock.picking'


    move_lines = fields.One2many('stock.move', 'picking_id', string="Stock Moves", copy=True)