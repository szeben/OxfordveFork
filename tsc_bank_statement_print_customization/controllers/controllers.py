# -*- coding: utf-8 -*-
# from odoo import http


# class TscBankStatementPrintCustomization(http.Controller):
#     @http.route('/tsc_bank_statement_print_customization/tsc_bank_statement_print_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsc_bank_statement_print_customization/tsc_bank_statement_print_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsc_bank_statement_print_customization.listing', {
#             'root': '/tsc_bank_statement_print_customization/tsc_bank_statement_print_customization',
#             'objects': http.request.env['tsc_bank_statement_print_customization.tsc_bank_statement_print_customization'].search([]),
#         })

#     @http.route('/tsc_bank_statement_print_customization/tsc_bank_statement_print_customization/objects/<model("tsc_bank_statement_print_customization.tsc_bank_statement_print_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsc_bank_statement_print_customization.object', {
#             'object': obj
#         })
