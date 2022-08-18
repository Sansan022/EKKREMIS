# -*- coding: utf-8 -*-
from odoo import http

# class Team-configuration(http.Controller):
#     @http.route('/team-configuration/team-configuration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/team-configuration/team-configuration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('team-configuration.listing', {
#             'root': '/team-configuration/team-configuration',
#             'objects': http.request.env['team-configuration.team-configuration'].search([]),
#         })

#     @http.route('/team-configuration/team-configuration/objects/<model("team-configuration.team-configuration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('team-configuration.object', {
#             'object': obj
#         })