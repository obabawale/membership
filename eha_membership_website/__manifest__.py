# -*- coding: utf-8 -*-
{
    'name': "EHA Membership Website Module",

    'summary': """
        EHA Membership Module.""",

    'description': """
        This module is designed to handle EHA's Membership 
    """,

    'author': "EHA Clinics Ltd",
    'website': "https://www.eha.ng",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base', 'web', 'portal', 'website_sale', 'eha_website','eha_membership'
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'views/website_template.xml',
        'views/website_family_membership_view.xml',
    ],
}