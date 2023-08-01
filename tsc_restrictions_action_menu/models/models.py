# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class tsc_restrictions_action_menu(models.Model):
#     _name = 'tsc_restrictions_action_menu.tsc_restrictions_action_menu'
#     _description = 'tsc_restrictions_action_menu.tsc_restrictions_action_menu'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
