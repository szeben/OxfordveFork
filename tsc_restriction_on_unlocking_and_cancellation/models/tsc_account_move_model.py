# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from lxml import etree


class tsc_AccountMove(models.Model):

    _inherit = 'account.move'

    tsc_posted_once = fields.Boolean(string="Was it posted once?", default=False)

    def button_cancel(self):
        """
        tsc_sale_order = self.invoice_origin
        self.tsc_posted_once = True
        if self.move_type == "out_invoice" and tsc_sale_order:
            tsc_picking_id = tsc_sale_order.picking_ids
            if tsc_picking_id.picking_type_code == "outgoing" and tsc_picking_id.state == "done":
                raise UserError(_("It is not possible to cancel the invoice that has confirmed merchandise already dispatched. Please try to generate a credit note."))
        """
        self.write({'auto_post': False, 'state': 'cancel'})

    
    def read(self, fields, load='_classic_read'):
        if self.check_access_rights('read', raise_exception=False):
            return super().read(fields, load=load)

    #@api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):

    
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        #raise UserError(f'{res}')


    
        doc = etree.XML(res['arch'])
    
        if view_type == 'form':
            for node_form in doc.xpath("//form"):
                node = doc.xpath("//field[@name='tsc_posted_once']")[0]
                #raise UserError(f'{node.get("context")}')
                node_form.set("edit", 'false')
                

        res['arch'] = etree.tostring(doc)
        return res




    def write(self,vals):
        #raise UserError(f'{self.tsc_posted_once}')
        return super().write(vals)