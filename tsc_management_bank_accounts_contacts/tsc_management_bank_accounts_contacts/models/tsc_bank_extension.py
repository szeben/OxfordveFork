# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class tsc_BankExtension(models.Model):

    _name = 'res.partner.bank'
    _inherit = ['res.partner.bank', 'mail.thread']

    tsc_verified = fields.Boolean(string="Verified",
                                 help="Determines if the contact's bank account has been verified",
                                 default=False,
                                 required=False,
                                 readonly=False,
                                 store=True,
                                 copy=True,
                                 tracking=True,
                                 )

class tsc_PartnerExtension(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread', 'mail.activity.mixin']

    def write(self, vals):
        original_banks = self.bank_ids
        if vals and 'bank_ids' in vals:
            for index, b in enumerate(vals['bank_ids']):
                if b[2]:
                    og_bank = {
                        "bank_id": original_banks[index].bank_id.name,
                        "acc_number": original_banks[index].acc_number,
                        "tsc_verified": _("Yes") if original_banks[index].tsc_verified else "No",
                    }

                    og_bank_final = f"""
                        ({og_bank['bank_id']}, {og_bank['acc_number']}, {og_bank['tsc_verified']})
                    """
                    
                    new_bank = {**og_bank}
                    if 'tsc_verified' in b[2]:
                        new_value = "Yes" if b[2].get("tsc_verified") else "No"
                        b[2].update({"tsc_verified": new_value})
                    new_bank.update(b[2])

                    new_bank_final = f"""
                        ({new_bank['bank_id']}, {new_bank['acc_number']}, {new_bank['tsc_verified']})
                    """
                    message = _('Bank')
                    message = message + f': {og_bank_final} => {new_bank_final}'
                    self.message_post(body=f"{message}")

        return super(tsc_PartnerExtension, self).write(vals)

