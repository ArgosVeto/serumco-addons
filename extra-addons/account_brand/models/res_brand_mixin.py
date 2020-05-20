# # Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResBrandMixin(models.AbstractModel):
    _inherit = 'res.brand.mixin'

    @api.constrains('brand_id', 'company_id')
    def _check_brand_requirement(self):
        for rec in self:
            if rec._name == 'account.move' and rec.type == 'entry':
                self -= rec
        return super(ResBrandMixin, self)._check_brand_requirement()
