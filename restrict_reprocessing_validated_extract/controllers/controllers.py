# -*- coding: utf-8 -*-
# from odoo import http


# class RestrictReprocessingValidatedExtract(http.Controller):
#     @http.route('/restrict_reprocessing_validated_extract/restrict_reprocessing_validated_extract', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/restrict_reprocessing_validated_extract/restrict_reprocessing_validated_extract/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('restrict_reprocessing_validated_extract.listing', {
#             'root': '/restrict_reprocessing_validated_extract/restrict_reprocessing_validated_extract',
#             'objects': http.request.env['restrict_reprocessing_validated_extract.restrict_reprocessing_validated_extract'].search([]),
#         })

#     @http.route('/restrict_reprocessing_validated_extract/restrict_reprocessing_validated_extract/objects/<model("restrict_reprocessing_validated_extract.restrict_reprocessing_validated_extract"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('restrict_reprocessing_validated_extract.object', {
#             'object': obj
#         })
