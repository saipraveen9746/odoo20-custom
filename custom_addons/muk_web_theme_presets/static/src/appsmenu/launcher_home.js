import { patch } from '@web/core/utils/patch';
import { useBus } from '@web/core/utils/hooks';
import { onWillDestroy } from '@odoo/owl';
import { NavBar } from '@web/webclient/navbar/navbar';
import { WebClient } from '@web/webclient/webclient';

import { AppsMenu } from '@muk_web_theme/webclient/appsmenu/appsmenu';

const OPEN_LAUNCHER_EVENT = 'MUK_WEB_THEME:OPEN_APP_LAUNCHER';
const CLOSE_LAUNCHER_EVENT = 'MUK_WEB_THEME:CLOSE_APP_LAUNCHER';
const LAUNCHER_VISIBILITY_EVENT = 'MUK_WEB_THEME:APP_LAUNCHER_VISIBILITY';

// The "database neutralized" banner is rendered above the webclient and pushes
// the navbar down. The launcher is fixed-positioned, so it must be offset by
// the banner height to stay aligned with the navbar.
function syncBannerOffset() {
    const banner = document.getElementById('oe_neutralize_banner');
    const height = banner ? Math.ceil(banner.getBoundingClientRect().height) : 0;
    document.documentElement.style.setProperty('--mk-banner-offset', `${height}px`);
}

patch(WebClient.prototype, {
    _loadDefaultApp() {
        this.env.bus.trigger(OPEN_LAUNCHER_EVENT);
    },
});

patch(AppsMenu.prototype, {
    setup() {
        super.setup(...arguments);
        window.addEventListener('resize', syncBannerOffset);
        onWillDestroy(() => window.removeEventListener('resize', syncBannerOffset));
        useBus(this.env.bus, OPEN_LAUNCHER_EVENT, () => this.state.open());
        useBus(this.env.bus, CLOSE_LAUNCHER_EVENT, () => this.state.close());
    },

    onOpened() {
        super.onOpened(...arguments);
        syncBannerOffset();
        this.env.bus.trigger(LAUNCHER_VISIBILITY_EVENT, true);
    },

    onClosed() {
        super.onClosed(...arguments);
        this.env.bus.trigger(LAUNCHER_VISIBILITY_EVENT, false);
    },
});

patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        useBus(this.env.bus, OPEN_LAUNCHER_EVENT, () => {
            const isSmall = this.ui?.isSmall ?? this.env.isSmall;
            if (isSmall) {
                this.state.isAppMenuSidebarOpened = true;
                this.state.isAllAppsMenuOpened = true;
            }
        });
        useBus(this.env.bus, LAUNCHER_VISIBILITY_EVENT, (event) => {
            const isOpen = typeof event?.detail === 'boolean' ? event.detail : Boolean(event);
            const el = typeof this.root === 'function' ? this.root() : this.root?.el;
            el?.classList.toggle('mk_app_launcher_open', isOpen);
        });
    },

    onNavBarDropdownItemSelection(menu) {
        super.onNavBarDropdownItemSelection(...arguments);
        this.env.bus.trigger(CLOSE_LAUNCHER_EVENT);
    },
});

