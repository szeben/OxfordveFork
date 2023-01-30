# -*- coding: utf-8 -*-
# from odoo import http


# class FeesForOrderLines(http.Controller):
#     @http.route('/fees_for_order_lines/fees_for_order_lines', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fees_for_order_lines/fees_for_order_lines/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fees_for_order_lines.listing', {
#             'root': '/fees_for_order_lines/fees_for_order_lines',
#             'objects': http.request.env['fees_for_order_lines.fees_for_order_lines'].search([]),
#         })

#     @http.route('/fees_for_order_lines/fees_for_order_lines/objects/<model("fees_for_order_lines.fees_for_order_lines"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fees_for_order_lines.object', {
#             'object': obj
#         })
