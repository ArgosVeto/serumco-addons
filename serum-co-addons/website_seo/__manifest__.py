# -*- coding: utf-8 -*-
{
  "name"                 :  "Website SEO Suite",
  "summary"              :  """Website SEO Suite facilitates you to optimize your website in the search engine.""",
  "category"             :  "Website",
  "version"              :  "2.2.1",
  "sequence"             :  1,
  "author"               :  "Apagen Solutions Pvt. Ltd.",
  "license"              :  "Other proprietary",
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