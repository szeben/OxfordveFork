# -*- coding: utf-8 -*-
# from odoo import http


# class BranchDefaults(http.Controller):
#     @http.route('/branch_defaults/branch_defaults', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/branch_defaults/branch_defaults/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('branch_defaults.listing', {
#             'root': '/branch_defaults/branch_defaults',
#             'objects': http.request.env['branch_defaults.branch_defaults'].search([]),
#         })

#     @http.route('/branch_defaults/branch_defaults/objects/<model("branch_defaults.branch_defaults"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('branch_defaults.object', {
#             'object': obj
#         })
