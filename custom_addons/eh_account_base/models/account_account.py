# -*- encoding: utf-8 -*-
##############################################################################
#
# ERP Heritage
# Copyright (C) 2026 (https://www.erpheritage.com.au/)
#
##############################################################################
"""
account.account extension for reporting-cache freshness.

Renaming an account, changing its type or code, or moving it under another
parent account (the Odoo 20 chart hierarchy, which replaced account groups)
all change report output (labels, classification, subtotals) without posting
a journal entry. The reporting cache keys on the per-company
eh_move_version counter, so those edits must bump it or a cached report keeps
serving figures/labels computed under the old account metadata until an
unrelated move posts.
"""

from odoo import api, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    # Fields whose change alters report presentation or classification.
    _EH_FIGURE_FIELDS = frozenset({
        'code', 'code_store', 'code_mapping_ids', 'name', 'account_type',
        'parent_id', 'active', 'tag_ids', 'reconcile', 'company_ids', 'company_id',
        # A zero balance Trial Balance lists every active account.
        'deprecated',
    })

    def _eh_owning_company_ids(self, include_descendants=False):
        # Chart records can be visible to a branch-scoped accountant through
        # the account ``parent_of`` rule while res.company rules hide the root
        # (or another shared owner) from relational-field reads. Ownership is
        # an invalidation authority input, not caller-visible presentation, so
        # derive it under sudo before expanding the affected subtrees.
        authoritative_accounts = self.sudo()
        if include_descendants and self.ids:
            # A reparent rewrites every descendant's parent_path, and a
            # descendant shared with another company nests in that company's
            # report through this account's chain even when that company
            # does not own this account.
            authoritative_accounts = authoritative_accounts.with_context(
                active_test=False,
            ).search([('id', 'child_of', self.ids)])
        if 'company_ids' in self._fields:
            owner_ids = set(authoritative_accounts.mapped('company_ids.id'))
        else:
            owner_ids = set(authoritative_accounts.mapped('company_id.id'))
        if not owner_ids:
            return set()
        # Odoo 18/19 chart records owned by a root company are valid in every
        # descendant branch.  Report SQL resolves their code in that branch's
        # root context, so root metadata changes invalidate the full subtree,
        # not only the exact owner row.
        return set(self.env['res.company'].sudo().with_context(
            active_test=False,
        ).search([
            ('id', 'child_of', tuple(sorted(owner_ids))),
        ]).ids)

    @api.model_create_multi
    def create(self, vals_list):
        accounts = super().create(vals_list)
        # A new account joins every zero balance Trial Balance of its chart.
        company_ids = accounts._eh_owning_company_ids()
        if company_ids:
            self.env['res.company'].sudo()._eh_bump_move_version(company_ids)
        return accounts

    def write(self, vals):
        reparent = 'parent_id' in vals
        company_ids = (
            self._eh_owning_company_ids(include_descendants=reparent)
            if self._EH_FIGURE_FIELDS.intersection(vals) else set()
        )
        res = super().write(vals)
        if self and self._EH_FIGURE_FIELDS.intersection(vals):
            # Cover both sides of a company-scope rehome without making
            # unrelated source ledgers stale when only a dedicated
            # consolidation-chart account changes.
            company_ids.update(
                self._eh_owning_company_ids(include_descendants=reparent))
            self.env['res.company'].sudo()._eh_bump_move_version(company_ids)
        return res

    def unlink(self):
        company_ids = self._eh_owning_company_ids()
        result = super().unlink()
        if company_ids:
            self.env['res.company'].sudo()._eh_bump_move_version(company_ids)
        return result
