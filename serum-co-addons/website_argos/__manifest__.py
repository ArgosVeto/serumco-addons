# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

{
    'name': 'Website Argos',
    'category': 'Website',
    'version': '13.0.0.0',
    'summary': '''Website Argos''',
    'description': """Website Argos""",
    'depends': [
        # 'theme_argos',
        'argos_hr',
        'website_blog',
        'website_sale',
        'argos_planning',
        'crm',
        'hr_recruitment',
        'website_hr_recruitment',
        'argos_operating_unit',
        'website_sale_comparison',
        'mass_mailing',
        'website_sale_wishlist',
        'sale_operating_unit',
        'website_rating',
    ],
    'data': [
        'data/data.xml',
        'data/operating_unit_data.xml',
        'data/questiondata.xml',
        'views/assets.xml',
        'data/menu.xml',
        'security/ir.model.access.csv',
        'security/operating_unit_security.xml',
        'views/operating_unit_view.xml',
        'views/clinic_views.xml',
        'views/agglomeration_view.xml',
        'views/contact_questions_view.xml',
        'views/contact_questions_view.xml',
        'views/crm_lead_view.xml',
        'views/hr_applicant_view.xml',
        'views/product_view.xml',
        'views/product_view_inherited.xml',
        'views/operating_unit_service_view.xml',


        'views/homepage.xml',
        'views/homepage_two.xml',
        'views/homepage_three.xml',
        'views/homepage_four.xml',
        'views/homepage_five.xml',
        'views/homepage_six.xml',
        'views/shop_home_template.xml',
        'views/group_argos_template.xml',
        'views/Service_hospitalisation_template.xml',
        'views/blog_template.xml',
        'views/blog_view.xml',
        'views/blog_snippet_inherited.xml',
        'views/dynamicslider.xml',
        'views/slider_snippets.xml',
        'views/header.xml',
        'views/footer.xml',
        'views/megamenu1.xml',
        'views/megamenu2.xml',
        'views/megamenu3.xml',
        'views/website_argos_inherited.xml',
        'views/shop_page_template.xml',
        'views/address_view.xml',
        'views/legal_notice.xml',
        'views/gtc.xml',
        'views/privacy_policy.xml',

        'views/blog_page_snippet_content.xml',
        'views/blog_page_snippet_content1.xml',
        'views/blog_page_snippet_content2.xml',
        'views/blog_page_snippet_content3.xml',
        'views/blog_page_snippet_content4.xml',
        'views/blog_page_snippet_content5.xml',
        'views/blog_page_snippet_content6.xml',
        'views/blog_page_snippet_content7.xml',


        # 'views/partner_view.xml',
        'views/clinic_template.xml',
        'views/clinic_detail_template.xml',
        'views/product_page_template.xml',
        'views/rating_template.xml',
        'views/gdpr_template.xml',
        'views/contact_us.xml', 
        'views/portal_template.xml',
        'views/signup_tmp.xml',        
        'views/checkout_page_inherit.xml',
        'views/candidate_template.xml',
        'views/application_template.xml',
        'views/menus.xml',
        'views/my_clinic.xml',
        'views/all_appointment.xml',
        'views/service_template.xml',        
        # 'views/clinic_views.xml',        
        # 'views/cart_template.xml',
        'views/rejoindre_argos.xml',
        'views/job_detail_snippet.xml',
        'views/job_fiche.xml',
    ],
    'qweb': [
        'static/src/xml/portal_chatter.xml',
    ],
    'demo': [
    
    ],

    'images': [
       
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}