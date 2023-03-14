# -*- coding: utf-8 -*-
# from odoo import http


# class ConstraintsOnProducts(http.Controller):
#     @http.route('/constraints_on_products/constraints_on_products', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/constraints_on_products/constraints_on_products/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('constraints_on_products.listing', {
#             'root': '/constraints_on_products/constraints_on_products',
#             'objects': http.request.env['constraints_on_products.constraints_on_products'].search([]),
#         })

#     @http.route('/constraints_on_products/constraints_on_products/objects/<model("constraints_on_products.constraints_on_products"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('constraints_on_products.object', {
#             'object': obj
#         })
