# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from lxml import etree
import simplejson

class tsc_AccountMove(models.Model):

    _inherit = 'account.move'

    def button_cancel(self):
        if self.move_type == "out_invoice":
            tsc_sale_order = self.invoice_origin
            if tsc_sale_order:
                tsc_sale_order_search = self.env['sale.order'].search([('name','=',tsc_sale_order)])
                if tsc_sale_order_search.exists():
                    tsc_picking_ids = tsc_sale_order_search.picking_ids
                    if tsc_picking_ids.picking_type_code == 'outgoing' and tsc_picking_ids.state == 'done':
                       raise UserError(_("It is not possible to cancel the invoice that has confirmed merchandise already dispatched. Please try to generate a credit note."))
        self.write({'auto_post': False, 'state': 'cancel'})

    
    #@api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):

        res = super().fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])    
        
        if view_type == 'form':
            for node in doc.xpath("//field"):
                modifiers = simplejson.loads(node.get("modifiers"))
                if 'readonly' not in modifiers:
                    modifiers['readonly'] = [['posted_before','=',True], ['move_type','in',["out_invoice", "out_refund"]]]
                elif type(modifiers['readonly']) != bool:
                        modifiers['readonly'].insert(0, '|')
                        modifiers['readonly'] += ['&', ['posted_before','=',True], ['move_type','in',["out_invoice", "out_refund"]]]
                node.set('modifiers', simplejson.dumps(modifiers)) 
                

        res['arch'] = etree.tostring(doc)
        return res
     