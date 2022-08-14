# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class team1_inventory(models.Model):
    _inherit = 'product.template'

    description_txt = fields.Text(string="Description:")

class testing(models.Model):
    _inherit = 'stock.picking'

    min_date = fields.Datetime(compute='_compute_dates', inverse='_set_min_date', store=True,
        index=True, track_visibility='onchange',default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

    # datetodayfield = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    # print(datetodayfield)

    # @api.multi
    # def _compute_picking_count(self):
    #     domains = {
    #         'count_picking_draft': [('state', '=', 'draft')],
    #         'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
    #         'count_picking_ready': [('state', 'in', ('assigned', 'partially_available'))],
    #         'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed', 'partially_available'))],
    #         'count_picking_late': [('min_date', '=', '2000/01/01 00:00:00'), ('state', 'in', ('assigned', 'waiting', 'confirmed', 'partially_available'))],
    #         'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting', 'partially_available'))],
    #     }
    #     res = super(testing,self)._compute_picking_count()
    #     return res