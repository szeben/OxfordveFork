# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class restrict_reprocessing_validated_extract(models.Model):
#     _name = 'restrict_reprocessing_validated_extract.restrict_reprocessing_validated_extract'
#     _description = 'restrict_reprocessing_validated_extract.restrict_reprocessing_validated_extract'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
