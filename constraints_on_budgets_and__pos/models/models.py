# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare, lazy_property
from odoo.tools.misc import format_date, get_lang

from collections import defaultdict

import re

USER_PRIVATE_FIELDS = []
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')

class Users(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        list_groups = [
            'Confirmar órdenes de compra', 
            'Gestionar órdenes de compra', 
            'Confirmar facturas de compra', 
            'Gestionar facturas de compras'
        ]
        print('vals_list---->', vals_list)
        for val in set(map(lambda i: f"in_group_{i}", self.env['res.groups'].search([('name', 'in', list_groups)]).ids)).intersection(set(vals_list[0])):
            if vals_list[0].get(val) == True:
                print('si men', vals_list[0].get(val))
                for key, value in vals_list[0].items():
                    if key.startswith('sel_groups_') and not key == 'sel_groups_1_9_10_146':
                        print('si hay sel_groups')
                        vals_list[0].update({
                            key: False
                        })
                    if key.startswith('in_group_') and not key == (val):
                        print('si hay in_group_')
                        vals_list[0].update({
                            key: False
                        })

        users = super(Users, self).create(vals_list)
        for user in users:
            # if partner is global we keep it that way
            if user.partner_id.company_id:
                user.partner_id.company_id = user.company_id
            user.partner_id.active = user.active
        return users

    def write(self, values):
        if values.get('active') and SUPERUSER_ID in self._ids:
            raise UserError(_("You cannot activate the superuser."))
        if values.get('active') == False and self._uid in self._ids:
            raise UserError(_("You cannot deactivate the user you're currently logged in as."))

        if values.get('active'):
            for user in self:
                if not user.active and not user.partner_id.active:
                    user.partner_id.toggle_active()
        if self == self.env.user:
            writeable = self.SELF_WRITEABLE_FIELDS
            for key in list(values):
                if not (key in writeable or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if values['company_id'] not in self.env.user.company_ids.ids:
                        del values['company_id']
                # safe fields only, so we write as super-user to bypass access rights
                self = self.sudo().with_context(binary_field_real_user=self.env.user)


        # print(values, self.groups_id, self.groups_id.ids)
        # for i in list(self.groups_id.category_id):
        #     print(i.xml_id)
        # for x in list(self.groups_id):
        #     print(x.name)

        list_groups = [
            'Confirmar órdenes de compra', 
            'Gestionar órdenes de compra', 
            'Confirmar facturas de compra', 
            'Gestionar facturas de compras'
        ]
        for val in set(map(lambda i: f"in_group_{i}", self.env['res.groups'].search([('name', 'in', list_groups)]).ids)).intersection(values):
            if values.get(val) == True:
                print('uno de los mios esta en True')
                full_query = self.env['res.groups'].search([
                    '|', '|', '|', '|', '|', '|', '|', '|','|',  
                    ('category_id.name', '=', 'Inventario'), 
                    ('category_id.name', '=', 'Ventas'), 
                    ('category_id.name', '=', 'Contabilidad'), 
                    ('category_id.parent_id.name', '=', 'Servicios'), 
                    ('category_id.parent_id.name', '=', 'Recursos Humanos'), 
                    ('category_id.name', '=', 'Rama'), 
                    ('category_id.name', '=', 'Administración'), 
                    ('category_id.name', '=', 'Técnico'), 
                    ('category_id.name', '=', 'Permisos extra'),
                    ('category_id.name', '=', 'Compra')
                ]).ids
                for val2 in full_query:
                    if val2 in self.groups_id.ids:
                        if val2 in self.env['res.groups'].search([('name', 'in', list_groups)]).ids:
                            pass
                        else:
                            values.update({
                                'in_group_' + str(val2): False
                            })

        print(self, values)
        res = super(Users, self).write(values)
        if 'company_id' in values:
            for user in self:
                # if partner is global we keep it that way
                if user.partner_id.company_id and user.partner_id.company_id.id != values['company_id']:
                    user.partner_id.write({'company_id': user.company_id.id})

        if 'company_id' in values or 'company_ids' in values:
            # Reset lazy properties `company` & `companies` on all envs
            # This is unlikely in a business code to change the company of a user and then do business stuff
            # but in case it happens this is handled.
            # e.g. `account_test_savepoint.py` `setup_company_data`, triggered by `test_account_invoice_report.py`
            for env in list(self.env.transaction.envs):
                if env.user in self:
                    lazy_property.reset_all(env)

        # clear caches linked to the users
        if self.ids and 'groups_id' in values:
            # DLE P139: Calling invalidate_cache on a new, well you lost everything as you wont be able to take it back from the cache
            # `test_00_equipment_multicompany_user`
            self.env['ir.model.access'].call_cache_clearing_methods()

        # per-method / per-model caches have been removed so the various
        # clear_cache/clear_caches methods pretty much just end up calling
        # Registry._clear_cache
        invalidation_fields = {
            'groups_id', 'active', 'lang', 'tz', 'company_id',
            *USER_PRIVATE_FIELDS,
            *self._get_session_token_fields()
        }
        if (invalidation_fields & values.keys()) or any(key.startswith('context_') for key in values):
            self.clear_caches()

        return res

class Groups(models.Model):
    _inherit = 'res.groups'

    def write(self, vals):
        list_groups = [
            'Confirmar órdenes de compra', 
            'Gestionar órdenes de compra', 
            'Confirmar facturas de compra', 
            'Gestionar facturas de compras'
        ]
        if 'users' in vals:
            print(len(vals.get('users')[0][2]))
        if self.id in self.env['res.groups'].search([('name', 'in', list_groups)]).ids:
            print('se esta modificando un grupo mio')
            if ('name' or 'comment' or 'category_id') not in vals:
                print('y justamente no es porque se creó')
                if len(self.users.ids) < len(vals.get('users')[0][2]):
                    print('es una añadicion')
                    print('pendiente con una vaina menor')
                    usuario = vals.get('users')[0][2][-1]
                    print('usuario', usuario)
                    full_query = self.env['res.groups'].search([
                            '|', '|', '|', '|', '|', '|', '|', '|', '|', 
                            ('category_id.name', '=', 'Inventario'), 
                            ('category_id.name', '=', 'Ventas'), 
                            ('category_id.name', '=', 'Contabilidad'), 
                            ('category_id.parent_id.name', '=', 'Servicios'), 
                            ('category_id.parent_id.name', '=', 'Recursos Humanos'), 
                            ('category_id.name', '=', 'Rama'), 
                            ('category_id.name', '=', 'Administración'), 
                            ('category_id.name', '=', 'Técnico'), 
                            ('category_id.name', '=', 'Permisos extra'),
                            ('category_id.name', '=', 'Compra')
                        ]).ids
                    values = {}
                    for val in full_query:
                        if val in self.env['res.groups'].search([('users', '=', usuario)]).ids:
                            if val in self.env['res.groups'].search([('name', 'in', list_groups)]).ids:
                                pass
                            else:
                                values.update({
                                    'in_group_' + str(val): False
                                })
                    super(Users, self.env['res.users'].search([('id', '=', usuario)])).write(values)
                else:
                    print('es una eleminiacion')

        if 'name' in vals:
            if vals['name'].startswith('-'):
                raise UserError(_('The name of the group can not start with "-"'))
        # invalidate caches before updating groups, since the recomputation of
        # field 'share' depends on method has_group()
        # DLE P139
        if self.ids:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['res.users'].has_group.clear_cache(self.env['res.users'])
        print('self------>', self, 'vals------>', vals, 'self.users', self.users.ids, len(self.users.ids))
        return super(Groups, self).write(vals)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def write(self, vals):
        vals, partner_vals = self._write_partner_values(vals)
        res = super().write(vals)
        if partner_vals:
            self.partner_id.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        if self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos'):
            if vals.get('group_id'):
                return res
            elif vals.get('state'):
                pass
            else:
                raise UserError(_('No tiene permisos para editar la orden de compra. Por favor comuníquese con su supervisor'))
        elif not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos'):
            raise UserError(_('No tiene permisos para editar la orden de compra. Por favor comuníquese con su supervisor'))
        else:
            return res

    def button_confirm(self):
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos'):
            raise UserError(_('No tiene permisos para confirmar la orden de compra. Por favor comuníquese con su supervisor'))
        else:
            return super(PurchaseOrder, self).button_confirm()

    def action_create_invoice(self):
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos_bills'):
            raise UserError(_('No tiene permisos para crear la factura para el proveedor. Por favor comuníquese con su supervisor'))
        else:
            return super(PurchaseOrder, self).action_create_invoice()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def write(self, values):
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos'):
            raise UserError(_('No tiene permisos para editar la orden de compra. Por favor comuníquese con su supervisor'))
        else:
            return super(PurchaseOrderLine, self).write(values)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        for move in self:
            if (move.restrict_mode_hash_table and move.state == "posted" and set(vals).intersection(INTEGRITY_HASH_MOVE_FIELDS)):
                raise UserError(_("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(INTEGRITY_HASH_MOVE_FIELDS))
            if (move.restrict_mode_hash_table and move.inalterable_hash and 'inalterable_hash' in vals) or (move.secure_sequence_number and 'secure_sequence_number' in vals):
                raise UserError(_('You cannot overwrite the values ensuring the inalterability of the accounting.'))
            if (move.posted_before and 'journal_id' in vals and move.journal_id.id != vals['journal_id']):
                raise UserError(_('You cannot edit the journal of an account move if it has been posted once.'))
            if (move.name and move.name != '/' and 'journal_id' in vals and move.journal_id.id != vals['journal_id']):
                raise UserError(_('You cannot edit the journal of an account move if it already has a sequence number assigned.'))

            # You can't change the date of a move being inside a locked period.
            if 'date' in vals and move.date != vals['date']:
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            # You can't post subtract a move to a locked period.
            if 'state' in vals and move.state == 'posted' and vals['state'] != 'posted':
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            if move.journal_id.sequence_override_regex and vals.get('name') and vals['name'] != '/' and not re.match(move.journal_id.sequence_override_regex, vals['name']):
                if not self.env.user.has_group('account.group_account_manager'):
                    raise UserError(_('The Journal Entry sequence is not conform to the current format. Only the Advisor can change it.'))
                move.journal_id.sequence_override_regex = False
        
        if self._move_autocomplete_invoice_lines_write(vals):
            res = True
        else:
            vals.pop('invoice_line_ids', None)
            res = super(AccountMove, self.with_context(check_move_validity=False, skip_account_move_synchronization=True)).write(vals)

        # You can't change the date of a not-locked move to a locked period.
        # You can't post a new journal entry inside a locked period.
        if 'date' in vals or 'state' in vals:
            self._check_fiscalyear_lock_date()
            self.mapped('line_ids')._check_tax_lock_date()

        if ('state' in vals and vals.get('state') == 'posted'):
            for move in self.filtered(lambda m: m.restrict_mode_hash_table and not(m.secure_sequence_number or m.inalterable_hash)).sorted(lambda m: (m.date, m.ref or '', m.id)):
                new_number = move.journal_id.secure_sequence_id.next_by_id()
                vals_hashing = {'secure_sequence_number': new_number,
                                'inalterable_hash': move._get_new_hash(new_number)}
                res |= super(AccountMove, move).write(vals_hashing)

        # Ensure the move is still well balanced.
        if 'line_ids' in vals and self._context.get('check_move_validity', True):
            self._check_balanced()

        self._synchronize_business_models(set(vals.keys()))
        if self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos_bills'):
            if vals.get('sequence_prefix'):
                pass
            elif vals.get('sequence_number'):
                pass
            elif vals.get('state') and vals.get('posted_before'):
                return res
            else:
                raise UserError(_('No tiene permisos para editar la factura. Por favor comuníquese con su supervisor'))
        elif not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos_bills'):
            raise UserError(_('No tiene permisos para editar la factura. Por favor comuníquese con su supervisor'))
        else:
            return res
    
    def _post(self, soft=True):
        """Post/Validate the documents.

        Posting the documents will give it a number, and check that the document is
        complete (some fields might not be required if not posted but are required
        otherwise).
        If the journal is locked with a hash table, it will be impossible to change
        some fields afterwards.

        :param soft (bool): if True, future documents are not immediately posted,
            but are set to be auto posted automatically at the set accounting date.
            Nothing will be performed on those documents before the accounting date.
        :return Model<account.move>: the documents that have been posted
        """
        if soft:
            future_moves = self.filtered(lambda move: move.date > fields.Date.context_today(self))
            future_moves.auto_post = True
            for move in future_moves:
                msg = _('This move will be posted at the accounting date: %(date)s', date=format_date(self.env, move.date))
                move.message_post(body=msg)
            to_post = self - future_moves
        else:
            to_post = self

        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice') and not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos_bills'):
            raise AccessError(_("No tienes acceso para publicar una factura. Por favor comuníquese con su supervisor"))
        for move in to_post:
            if move.partner_bank_id and not move.partner_bank_id.active:
                raise UserError(_("The recipient bank account link to this invoice is archived.\nSo you cannot confirm the invoice."))
            if move.state == 'posted':
                raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.context_today(self):
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s", date_msg))
            if not move.journal_id.active:
                raise UserError(_(
                    "You cannot post an entry in an archived journal (%(journal)s)",
                    journal=move.journal_id.display_name,
                ))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0, precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(
                    _("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            if move.display_inactive_currency_warning:
                raise UserError(_("You cannot validate an invoice with an inactive currency: %s",
                                  move.currency_id.name))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date:
                if move.is_sale_document(include_receipts=True):
                    move.invoice_date = fields.Date.context_today(self)
                    move.with_context(check_move_validity=False)._onchange_invoice_date()
                elif move.is_purchase_document(include_receipts=True):
                    raise UserError(_("The Bill/Refund date is required to validate this document."))

            # When the accounting date is prior to the tax lock date, move it automatically to today.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (move.line_ids.tax_ids or move.line_ids.tax_tag_ids):
                move.date = move._get_accounting_date(move.invoice_date or move.date, True)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        to_post.mapped('line_ids').create_analytic_lines()
        to_post.write({
            'state': 'posted',
            'posted_before': True,
        })

        for move in to_post:
            move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])

            # Compute 'ref' for 'out_invoice'.
            if move._auto_compute_invoice_reference():
                to_write = {
                    'payment_reference': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['payment_reference']}))
                move.write(to_write)

        for move in to_post:
            if move.is_sale_document() \
                    and move.journal_id.sale_activity_type_id \
                    and (move.journal_id.sale_activity_user_id or move.invoice_user_id).id not in (self.env.ref('base.user_root').id, False):
                move.activity_schedule(
                    date_deadline=min((date for date in move.line_ids.mapped('date_maturity') if date), default=move.date),
                    activity_type_id=move.journal_id.sale_activity_type_id.id,
                    summary=move.journal_id.sale_activity_note,
                    user_id=move.journal_id.sale_activity_user_id.id or move.invoice_user_id.id,
                )

        customer_count, supplier_count = defaultdict(int), defaultdict(int)
        for move in to_post:
            if move.is_sale_document():
                customer_count[move.partner_id] += 1
            elif move.is_purchase_document():
                supplier_count[move.partner_id] += 1
        for partner, count in customer_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('customer_rank', count)
        for partner, count in supplier_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('supplier_rank', count)

        # Trigger action for paid invoices in amount is zero
        to_post.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        # Force balance check since nothing prevents another module to create an incorrect entry.
        # This is performed at the very end to avoid flushing fields before the whole processing.
        to_post._check_balanced()
        return to_post

    def action_post(self):
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos_bills'):
            raise UserError(_('No tiene permisos para confirmar la factura. Por favor comuníquese con su supervisor'))
        else:
            return super(AccountMove, self).action_post()

