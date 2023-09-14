# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class tsc_StockPickingType(models.Model):

    _name = 'stock.picking.type'
    _inherit = ['stock.picking.type', 'mail.thread']
    
    tsc_picking_internal_use = fields.Boolean(string="Is it for Internal Purchases?", 
                                              help="Mark as checked if the operation will be used exclusively for internal purchases.",
                                              required=False,
                                              readonly=False,
                                              store=True,
                                              copy=False,
                                              tracking=False,
                                              default=False)

    tsc_picking_merchandise_use = fields.Boolean(string="Is it for Merchandise Purchases?", 
                                              help="Mark as checked if the operation will be used exclusively for merchandise purchases.",
                                              required=False,
                                              readonly=False,
                                              store=True,
                                              copy=False,
                                              tracking=False,
                                              default=False)

class tsc_StockPicking(models.Model):

    _name = 'stock.picking'
    _inherit = ['stock.picking', 'mail.thread']

    def tsc_in_internal_group(self):
        return self.env.user.has_group('tsc_adjustments_for_internal_purchases.tsc_internal_purchases_group')

    def tsc_in_merchandise_group(self):
        return self.env.user.has_group('tsc_adjustments_for_internal_purchases.tsc_merchandise_purchase_group')

    def tsc_check_type(self, vals):
        if vals.code == "incoming":
            tsc_user_in_internal_group = self.tsc_in_internal_group()
            tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()

            if (vals.tsc_picking_internal_use and not tsc_user_in_internal_group) or (vals.tsc_picking_merchandise_use and not tsc_user_in_internal_group):
                raise UserError(_("You are not currently allowed to create or modify inventory transfers. Merchandise purchase or internal purchase permissions are needed."))

    
    @api.model
    def create(self, vals):
        tsc_picking_type = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
        self.tsc_check_type(tsc_picking_type)
        return super(tsc_StockPicking, self).create(vals)

    def write(self, vals):
        for tsc_picking in self:
            tsc_picking_type = tsc_picking.picking_type_id
            if vals.get('picking_type_id'):
                tsc_picking_type = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
            if tsc_picking_type:
                self.tsc_check_type(tsc_picking_type)
        return super(tsc_StockPicking, self).write(vals)

    def read(self, fields=None, load='_classic_read'): 

        #raise UserError("?")
        return super(tsc_StockPicking, self).read(fields=fields, load=load) 

    """
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(tsc_StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu) 

        view = self.env.ref('stock.view_picking_form')
        tsc_picking_type = self.picking_type_id
        tsc_user_in_internal_group = self.tsc_in_internal_group()
        tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()


        if res["type"]=='form' and res["view_id"] == view: # or (view_search == view_id and view_type=='search'):
            
            if (tsc_picking_type.tsc_picking_internal_use and not tsc_user_in_internal_group) or (tsc_picking_type.tsc_picking_merchandise_use and not tsc_user_in_internal_group):
                raise UserError(_("You are not currently allowed to view this type of inventory transfer. Merchandise purchase or internal purchase permissions are needed."))
  
        return res   
    """


