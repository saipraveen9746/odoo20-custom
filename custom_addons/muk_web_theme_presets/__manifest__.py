{
    'name': 'MuK Web Theme CSS Presets',
    'summary': 'CSS background presets for the MuK apps menu',
    'version': '20.0.1.0.0',
    'category': 'Themes/Backend',
    'license': 'LGPL-3',
    'author': 'MuK IT',
    'website': 'http://www.mukit.at',
    'depends': ['muk_web_theme'],
    'data': [
        'views/res_config_settings.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'muk_web_theme_presets/static/src/appsmenu/theme_presets.js',
            'muk_web_theme_presets/static/src/appsmenu/launcher_home.js',
            'muk_web_theme_presets/static/src/appsmenu/theme_presets.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
