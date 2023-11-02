# -*- coding: utf-8 -*-
# from odoo import http


# class TscNewSalesAnalysis(http.Controller):
#     @http.route('/tsc_new_sales_analysis/tsc_new_sales_analysis', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsc_new_sales_analysis/tsc_new_sales_analysis/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsc_new_sales_analysis.listing', {
#             'root': '/tsc_new_sales_analysis/tsc_new_sales_analysis',
#             'objects': http.request.env['tsc_new_sales_analysis.tsc_new_sales_analysis'].search([]),
#         })

#     @http.route('/tsc_new_sales_analysis/tsc_new_sales_analysis/objects/<model("tsc_new_sales_analysis.tsc_new_sales_analysis"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsc_new_sales_analysis.object', {
#             'object': obj
#         })
