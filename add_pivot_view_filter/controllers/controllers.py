# -*- coding: utf-8 -*-
# from odoo import http


# class PivotViewFilter(http.Controller):
#     @http.route('/pivot_view_filter/pivot_view_filter', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pivot_view_filter/pivot_view_filter/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pivot_view_filter.listing', {
#             'root': '/pivot_view_filter/pivot_view_filter',
#             'objects': http.request.env['pivot_view_filter.pivot_view_filter'].search([]),
#         })

#     @http.route('/pivot_view_filter/pivot_view_filter/objects/<model("pivot_view_filter.pivot_view_filter"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pivot_view_filter.object', {
#             'object': obj
#         })
