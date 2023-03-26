# -*- coding: utf-8 -*-
# from odoo import http


# class ConstraintsOnBudgetsAndPos(http.Controller):
#     @http.route('/constraints_on_budgets_and__pos/constraints_on_budgets_and__pos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/constraints_on_budgets_and__pos/constraints_on_budgets_and__pos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('constraints_on_budgets_and__pos.listing', {
#             'root': '/constraints_on_budgets_and__pos/constraints_on_budgets_and__pos',
#             'objects': http.request.env['constraints_on_budgets_and__pos.constraints_on_budgets_and__pos'].search([]),
#         })

#     @http.route('/constraints_on_budgets_and__pos/constraints_on_budgets_and__pos/objects/<model("constraints_on_budgets_and__pos.constraints_on_budgets_and__pos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('constraints_on_budgets_and__pos.object', {
#             'object': obj
#         })
