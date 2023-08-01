# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartner(models.Model):

    _inherit = "res.partner"

    def action_archive(self):
        res = super().action_archive()

        for record in self:
            record.message_post(body=_("Archived contact"))

        return res
    
    def action_unarchive(self):
        res = super().action_unarchive()

        for record in self:
            record.message_post(body=_("Unarchived contact"))


        return res