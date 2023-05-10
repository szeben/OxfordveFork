# -*- coding: utf-8 -*-
# from odoo import http


# class VerificationInvoiceAgainstPo(http.Controller):
#     @http.route('/verification_invoice_against_po/verification_invoice_against_po', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/verification_invoice_against_po/verification_invoice_against_po/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('verification_invoice_against_po.listing', {
#             'root': '/verification_invoice_against_po/verification_invoice_against_po',
#             'objects': http.request.env['verification_invoice_against_po.verification_invoice_against_po'].search([]),
#         })

#     @http.route('/verification_invoice_against_po/verification_invoice_against_po/objects/<model("verification_invoice_against_po.verification_invoice_against_po"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('verification_invoice_against_po.object', {
#             'object': obj
#         })
