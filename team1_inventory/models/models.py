# -*- coding: utf-8 -*-

from odoo import models, fields, api

class team1_inventory(models.Model):
    _inherit = 'product.template'

    description_txt = fields.Text(string="Description:")

class testing(models.Model):
    _inherit = 'stock.picking.type'

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