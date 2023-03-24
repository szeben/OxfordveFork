# -*- coding: utf-8 -*-
# from odoo import http


# class StockReplenishmentReport(http.Controller):
#     @http.route('/stock_replenishment_report/stock_replenishment_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_replenishment_report/stock_replenishment_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_replenishment_report.listing', {
#             'root': '/stock_replenishment_report/stock_replenishment_report',
#             'objects': http.request.env['stock_replenishment_report.stock_replenishment_report'].search([]),
#         })

#     @http.route('/stock_replenishment_report/stock_replenishment_report/objects/<model("stock_replenishment_report.stock_replenishment_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_replenishment_report.object', {
#             'object': obj
#         })
