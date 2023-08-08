# -*- coding: utf-8 -*-
# from odoo import http


# class TscRestrictionsActionMenu(http.Controller):
#     @http.route('/tsc_restrictions_action_menu/tsc_restrictions_action_menu', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsc_restrictions_action_menu/tsc_restrictions_action_menu/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsc_restrictions_action_menu.listing', {
#             'root': '/tsc_restrictions_action_menu/tsc_restrictions_action_menu',
#             'objects': http.request.env['tsc_restrictions_action_menu.tsc_restrictions_action_menu'].search([]),
#         })

#     @http.route('/tsc_restrictions_action_menu/tsc_restrictions_action_menu/objects/<model("tsc_restrictions_action_menu.tsc_restrictions_action_menu"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsc_restrictions_action_menu.object', {
#             'object': obj
#         })
