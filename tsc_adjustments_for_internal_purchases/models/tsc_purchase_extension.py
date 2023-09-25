  # -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

class tsc_PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def tsc_in_internal_group(self):
        return self.env.user.has_group('tsc_adjustments_for_internal_purchases.tsc_internal_purchases_group')

    def tsc_in_merchandise_group(self):
        return self.env.user.has_group('tsc_adjustments_for_internal_purchases.tsc_merchandise_purchase_group')
    
    @api.model
    def _get_picking_type(self, company_id):
        tsc_user_in_internal_group = self.tsc_in_internal_group()
        tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()
        
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])

        if tsc_user_in_internal_group and not tsc_user_in_merchandise_group:
            picking_type = picking_type.search([('tsc_picking_internal_use', '=', True)])

        if tsc_user_in_merchandise_group and not tsc_user_in_internal_group:
            picking_type = picking_type.search([('tsc_picking_merchandise_use', '=', True)])
            
        return picking_type[:1]

    @api.model_create_multi
    def create(self, vals_list):
        self.tsc_check_values(vals_list[0])     
        return super(tsc_PurchaseOrder, self).create(vals_list)

    def write(self, vals):
        self.tsc_check_values(vals)
        return super(tsc_PurchaseOrder, self).write(vals)

    def tsc_raise_error(self):
        raise UserError(_("You are not currently allowed to create or modify purchase orders. Merchandise purchase or internal purchase permissions are needed."))
        
    def tsc_check_values(self, vals):
        tsc_user_in_internal_group = self.tsc_in_internal_group()
        tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()

        if 'picking_type_id' in vals:
            tsc_picking_type_id = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
                
            if (not tsc_user_in_internal_group and tsc_picking_type_id.tsc_picking_internal_use) and not (tsc_user_in_merchandise_group and tsc_picking_type_id.tsc_picking_merchandise_use):
                self.tsc_raise_error()
                
            if (not tsc_user_in_merchandise_group and tsc_picking_type_id.tsc_picking_merchandise_use) and not (tsc_user_in_internal_group and tsc_picking_type_id.tsc_picking_internal_use):
                self.tsc_raise_error()

    def button_confirm(self):   
        tsc_properties_getter = { "picking_type_id": self.picking_type_id.id }
        self.tsc_check_values(tsc_properties_getter)
        return super(tsc_PurchaseOrder, self).button_confirm() 


    
      
                    

    
    

 







                
        

