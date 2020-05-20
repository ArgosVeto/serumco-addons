# # Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResBrand(models.Model):
    _name = 'res.brand'
    _description = 'Brand'

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, index=True, auto_join=True, delegate=True, ondelete='restrict')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        Override to filter by company
        :param args:
        :param offset:
        :param limit:
        :param order:
        :param count:
        :param access_rights_uid:
        :return:
        """
        if self._context.get('search_brand_by_company'):
            args.append(('company_id', '=', self._context.get('search_brand_by_company')))
        return super(ResBrand, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                             access_rights_uid=access_rights_uid)
