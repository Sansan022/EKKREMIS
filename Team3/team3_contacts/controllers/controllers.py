# -*- coding: utf-8 -*-
from odoo import http

# class Team3Contacts(http.Controller):
#     @http.route('/team3_contacts/team3_contacts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/team3_contacts/team3_contacts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('team3_contacts.listing', {
#             'root': '/team3_contacts/team3_contacts',
#             'objects': http.request.env['team3_contacts.team3_contacts'].search([]),
#         })

#     @http.route('/team3_contacts/team3_contacts/objects/<model("team3_contacts.team3_contacts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('team3_contacts.object', {
#             'object': obj
#         })