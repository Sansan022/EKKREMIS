# -*- coding: utf-8 -*-

from odoo import models, fields, api

<<<<<<< HEAD:team1_inventory/models/models.py
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
=======
# class sky_inventory(models.Model):
#     _name = 'sky_inventory.sky_inventory'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
>>>>>>> 31235fa86106c67a5653f66d376a1998cf995b1c:team2_sky_inventory/models/models.py
