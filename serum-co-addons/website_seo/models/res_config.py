# -*- coding: utf-8 -*-
from odoo import api, fields, models

class res_config_settings(models.TransientModel):
    _name = 'website.seo.config.settings'
    _inherit = 'res.config.settings'
    wk_seo_website_meta_image_alt_text = fields.Char(
        string="Image Alt-Text",
        readonly=1,
        default='Records Name',
        help="""Add Alt Text to an Image."""

    )
    wk_seo_website_meta_title_size = fields.Integer(
        string="Max Length Of Title",
        default= 70,
        required=1,
        help="""The maximum length of "title" meta-tags."""

    )
    wk_seo_website_meta_description_size = fields.Integer(
        string="Max Length of Description",
        default=165,
        required=1,
        help="""The maximum length of "Description" meta-tags."""

    )
    wk_seo_website_meta_keywords_size = fields.Integer(
        string="Max Length Of Keyword",
        default=21,
        required=1,
        help="""The maximum length of "Keyword" meta-tags."""

    )
    wk_seo_website_meta_keywords_number = fields.Integer(
        string="Max No. of Keywords",
        default=27,
        required=1,
        help="""The maximum length of "Description" meta-tags."""

    )

    @api.model
    def get_values(self):
        res = super(res_config_settings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            {
                'wk_seo_website_meta_image_alt_text':IrDefault.get('website.seo.config.settings', 'wk_seo_website_meta_image_alt_text') or 'Records Name',
                'wk_seo_website_meta_title_size':IrDefault.get('website.seo.config.settings', 'wk_seo_website_meta_title_size') or 70,
                'wk_seo_website_meta_description_size':IrDefault.get('website.seo.config.settings', 'wk_seo_website_meta_description_size') or 165,
                'wk_seo_website_meta_keywords_size':IrDefault.get('website.seo.config.settings', 'wk_seo_website_meta_keywords_size') or 27,
                'wk_seo_website_meta_keywords_number':IrDefault.get('website.seo.config.settings', 'wk_seo_website_meta_keywords_number') or 21,
            }
        )
        return res

    @api.model
    def set_values(self):
        super(res_config_settings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        for config in self:
            IrDefault.set(
                'website.seo.config.settings',
                'wk_seo_website_meta_image_alt_text',
                config.wk_seo_website_meta_image_alt_text or 'Records Name'
            )
            IrDefault.set(
                'website.seo.config.settings',
                'wk_seo_website_meta_title_size',
                config.wk_seo_website_meta_title_size or ''
            )
            IrDefault.set(
                'website.seo.config.settings',
                'wk_seo_website_meta_description_size',
                config.wk_seo_website_meta_description_size or ''
            )
            IrDefault.set(
                'website.seo.config.settings',
                'wk_seo_website_meta_keywords_size',
                config.wk_seo_website_meta_keywords_size or ''
            )
            IrDefault.set(
                'website.seo.config.settings',
                'wk_seo_website_meta_keywords_number',
                config.wk_seo_website_meta_keywords_number or ''
            )
        return True
