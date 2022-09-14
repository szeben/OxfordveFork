# -*- coding: utf-8 -*-
# from odoo import http


# class ProductAvailableByBranchKanban(http.Controller):
#     @http.route('/product_available_by_branch_kanban/product_available_by_branch_kanban', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_available_by_branch_kanban/product_available_by_branch_kanban/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_available_by_branch_kanban.listing', {
#             'root': '/product_available_by_branch_kanban/product_available_by_branch_kanban',
#             'objects': http.request.env['product_available_by_branch_kanban.product_available_by_branch_kanban'].search([]),
#         })

#     @http.route('/product_available_by_branch_kanban/product_available_by_branch_kanban/objects/<model("product_available_by_branch_kanban.product_available_by_branch_kanban"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_available_by_branch_kanban.object', {
#             'object': obj
#         })
