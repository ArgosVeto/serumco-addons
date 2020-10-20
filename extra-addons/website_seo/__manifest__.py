# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website SEO Suite",
  "summary"              :  """Website SEO Suite facilitates you to optimize your website in the search engine.""",
  "category"             :  "Website",
  "version"              :  "2.2.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-SEO-Suite.html",
  "description"          :  """Website SEO Suite
                                Website Search Engine Optimization Suite
                                Suite for SEO in Website
                                SEO
                                Search Engine Optimization
                                SEO Suite
                                Website
                                Website SEO
                                Optimize Website
                                SEO Suite in Website
                                Optimize Website
                                Odoo Website SEO Suite
                                Adding Keywords
                                SEO Toolkit""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_seo?version=13.0",
  "depends"              :  [
                             'website_sale',
                             'website_webkul_addons',
                             'wk_wizard_messages',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/res_config_view.xml',
                             'views/template.xml',
                             'views/website_seo.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'data/demo.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  59,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}