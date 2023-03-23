# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare, lazy_property
from odoo.tools.misc import format_date, get_lang

from collections import defaultdict

import re

USER_PRIVATE_FIELDS = []
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    """
    Modelo heredado para aplicar ciertas restricciones cuando se está creando, editando
    o eliminando una orden de compra. Tambien para aplicar restricciones en el botón
    "Confirmar Orden" de compra, y para "Crear Factura" de compra
    """

    def write(self, vals):
        vals, partner_vals = self._write_partner_values(vals)
        res = super().write(vals)
        if partner_vals:
            self.partner_id.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        # Se verifica si el usuario tiene el grupo "Gestionar ordenes de compra"; si es True, se
        # procede a seguir con la función de manera normal. En caso contrario, levantará un UserError
        # indicando que no tiene permisos para editar la orden de compra. En caso tal de pertenecer al grupo
        # "Confirmar ordenes de compra", se debe verificar ciertos campos ya que al confirmar la orden de compra
        # también se está entrando a esta funcion para escribir datos.
        if self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos'):
            if vals.get('group_id'):
                return res
            elif vals.get('state'):
                pass
            elif self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos'):
                pass
            else:
                # En caso de que se pertenezca al grupo "Confirmar ordenes de compra" pero se esté intentando editar
                # otro campo que no es debido, levantará el error.
                raise UserError(_('No tiene permisos para editar la orden de compra. Por favor comuníquese con su supervisor'))
        elif not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos'):
            raise UserError(_('No tiene permisos para editar la orden de compra. Por favor comuníquese con su supervisor'))
        else:
            return res

    def button_confirm(self):
        # Restriccion sencilla para el boton de confirmar orden de compra. Si no pertenece al grupo debido
        # levantará el error.
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos'):
            raise UserError(_('No tiene permisos para confirmar la orden de compra. Por favor comuníquese con su supervisor'))
        else:
            return super(PurchaseOrder, self).button_confirm()

    def action_create_invoice(self):
        # También se aplica una restricción para la creación de factura. No hay mucho que manipular acá,
        # ya que poco se adentra en el módulo purchase porque ya lo hace directamente con account y account.move
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos_bills'):
            raise UserError(_('No tiene permisos para crear la factura para el proveedor. Por favor comuníquese con su supervisor'))
        else:
            return super(PurchaseOrder, self).action_create_invoice()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    """
        Modelo heredado para aplicar una restricción dentro de las lineas de ordenes de compra
        dentro de una orden de compra. Si no pertenece al grupo acorde, se levantará un error
    """


    def write(self, values):
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos'):
            raise UserError(_('No tiene permisos para editar la orden de compra. Por favor comuníquese con su supervisor'))
        else:
            return super(PurchaseOrderLine, self).write(values)


class AccountMove(models.Model):
    _inherit = 'account.move'
    """
        Modelo heredado para aplicar unas restricciones al final del código, que permitirá manejar
        el control de los permisos que tiene los miembros de los grupos "Gestionar facturas de compra" y
        "Confirmar facturas de compras"
    """


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

        # Se verifica si el usuario está dentro del grupo "Gestionar facturas de compra". En caso contrario,
        # levantará un error. También los que confirman las facturas pasarán por esta funcion, ya que se estan
        # escribiendo datos sobre las facturas; entonces, se debe verificar (para ambos casos) que la edición
        # de la factura sea únicamente sobre 'in_invoice' (facturas de proveedor), para que no ocasione choques
        # con las otras facturas
        # Se modificó la función. Ahora iterará sobre cada factura que se esté editando, y verificará primero si 
        # es una factura de tipo 'in_invoice', para aplicarle ciertas restricciones. Si no, no hara nada.
        # Se debe iterar ya que en los modelos de conciliación de bancos, se pueden editar varias facturas a la vez
        for move in self:
            if move.move_type == 'in_invoice':
                if self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_manage_pos_bills'):
                    pass
                elif not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos_bills'):
                    # Si cualquier otra persona quiere modificar la factura de compra y no tiene los permisos, levantará
                    # el siguiente error
                    raise UserError(_('No tiene permisos para editar la factura. Por favor comuníquese con su supervisor'))
            else:
                pass
        return res
    
    def _post(self, soft=True):
        """
            Modelo heredado para añadir el permiso de confirmar factura al grupo
            "Confirmar facturas de compras" para que pueda ejecutar el botón
            sin pertenecer a cualquier grupo de Contabilidad
        """
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
        # La restricción solo aplicaba para aquellos que pertenecía a Contabilidad/Facturación. Se añadió
        # "Confirmar facturas de compras" para poder que el miembro del grupo pueda ejecutar la acción
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
        # Restricción sencilla que aplica si el miembro no es perteneciente al grupo "Confirmar facturas de compras"
        # al ejecutar la acción "Confirmar Factura"
        if not self.env.user.has_group('constraints_on_budgets_and__pos.group_purchase_confirm_pos_bills') and self.move_type == 'in_invoice':
            raise UserError(_('No tiene permisos para confirmar la factura. Por favor comuníquese con su supervisor'))
        else:
            return super(AccountMove, self).action_post()

