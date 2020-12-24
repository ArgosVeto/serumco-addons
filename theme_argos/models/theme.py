# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import models


class themeArgos(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_argos_post_copy(self, mod):
        self.disable_view('website_blog.opt_blog_cover_post')
        self.disable_view('website_blog.opt_posts_loop_show_author')

