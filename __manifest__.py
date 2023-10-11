{
    'name': "Performance Tracker",
    'author': 'Rizwaan',
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base','mail','hr','logic_digital_tracker','logic_miscellaneous','yes_plus','upaya','one_to_one','qualitative_analysis','exam_logic','logic_sfc','logic_cip','mock_interview'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/digital_performance_views.xml',
        'views/employee_views.xml',

    ],
    # 'assets':{'web.assets_qweb': [


    # ],
    # },
    'qweb': ["static/src/xml/dashboard_templates.xml"],
    'assets': {
    'web.assets_backend': [
        '/logic_performance_tracker/static/src/js/dashboard_card_view.js',
        '/logic_performance_tracker/static/src/scss/dashboard_card_view.scss',
        '/logic_performance_tracker/static/src/css/dashboard_card_view.css',
        '/logic_performance_tracker/static/src/css/lib/jquery.orgchart.css',
        '/logic_performance_tracker/static/src/css/lib/orgchart_styles.css',
        '/logic_performance_tracker/static/src/css/lib/other_styles.css',
    ]},
    'demo': [],
    'summary': "Performance Tracker",
    'description': "",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}