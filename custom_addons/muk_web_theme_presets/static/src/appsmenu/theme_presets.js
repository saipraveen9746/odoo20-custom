import { user } from '@web/core/user';
import { patch } from '@web/core/utils/patch';

import { AppsMenu } from '@muk_web_theme/webclient/appsmenu/appsmenu';

const themeClasses = {
    midnight: 'mk_app_menu_theme_midnight',
    glass: 'mk_app_menu_theme_glass',
    lagoon: 'mk_app_menu_theme_lagoon',
    orchard: 'mk_app_menu_theme_orchard',
    aurora: 'mk_app_menu_theme_aurora',
    sunset: 'mk_app_menu_theme_sunset',
    slate: 'mk_app_menu_theme_slate',
    cosmic: 'mk_app_menu_theme_cosmic',
    emerald: 'mk_app_menu_theme_emerald',
    ceramic: 'mk_app_menu_theme_ceramic',
    oceanic: 'mk_app_menu_theme_oceanic',
    frost: 'mk_app_menu_theme_frost',
    linen: 'mk_app_menu_theme_linen',
    pearl: 'mk_app_menu_theme_pearl',
    canvas: 'mk_app_menu_theme_canvas',
    blush: 'mk_app_menu_theme_blush',
    sandstone: 'mk_app_menu_theme_sandstone',
};

patch(AppsMenu.prototype, {
    onOpened() {
        super.onOpened(...arguments);

        const menu = typeof this.menuRef === 'function' ? this.menuRef() : this.menuRef?.el;
        if (!menu) {
            return;
        }

        const existingThemes = Array.from(menu.classList).filter((cls) =>
            cls.startsWith('mk_app_menu_theme_')
        );
        if (existingThemes.length) {
            menu.classList.remove(...existingThemes);
        }

        const theme = user.activeCompany.apps_menu_theme;
        const themeClass = themeClasses[theme];
        if (themeClass) {
            menu.style.backgroundImage = '';
            menu.classList.add(themeClass);
        }
    },
});
