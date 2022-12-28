# -*- coding: utf-8 -*-
# from odoo import http


# class Name(http.Controller):
#     @http.route('/name/name', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/name/name/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('name.listing', {
#             'root': '/name/name',
#             'objects': http.request.env['name.name'].search([]),
#         })

#     @http.route('/name/name/objects/<model("name.name"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('name.object', {
#             'object': obj
#         })
