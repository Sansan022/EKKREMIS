# -*- coding: utf-8 -*-
from odoo import http

# class Team1Inventory(http.Controller):
#     @http.route('/team1_inventory/team1_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/team1_inventory/team1_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('team1_inventory.listing', {
#             'root': '/team1_inventory/team1_inventory',
#             'objects': http.request.env['team1_inventory.team1_inventory'].search([]),
#         })

#     @http.route('/team1_inventory/team1_inventory/objects/<model("team1_inventory.team1_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('team1_inventory.object', {
#             'object': obj
#         })