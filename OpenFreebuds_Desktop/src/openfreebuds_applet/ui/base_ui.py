import logging
import os
import webbrowser

import openfreebuds_backend
from pystray import MenuItem, Menu

from openfreebuds import event_bus
from openfreebuds.events import EVENT_UI_UPDATE_REQUIRED
from openfreebuds_applet import tools, tool_server, tool_actions, tool_update, tool_hotkeys
from openfreebuds_applet.l18n import t, setup_language, setup_auto, ln


# noinspection PyUnresolvedReferences,PyProtectedMember
def get_quiting_menu():
    return [
        MenuItem(t("state_quiting"), None, enabled=False),
        MenuItem(t("action_kill_app"),
                 action=lambda: os._exit(0))
    ]


def get_header_menu_part(applet):
    head = []

    # Build update menu item
    has_update, new_version = tool_update.get_result()
    if has_update:
        head.append(MenuItem(t("action_update").format(new_version),
                             action=tool_update.show_update_message))
        head.append(Menu.SEPARATOR)

    # Build device submenu
    head.append(MenuItem(applet.settings.device_name, action=Menu(
        MenuItem(t("submenu_device_info"), action=lambda: show_device_info(applet)),
        MenuItem(t("action_unpair"), action=applet.drop_device)
    )))

    # Build connect/disconnect action
    if applet.manager.state == applet.manager.STATE_CONNECTED:
        action_connection_mgmt = MenuItem(t("action_disconnect"), action=applet.force_disconnect)
    else:
        action_connection_mgmt = MenuItem(t("action_connect"), action=applet.force_connect)
    head.append(action_connection_mgmt)

    # Ready
    head.append(Menu.SEPARATOR)
    return head


def get_app_menu_part(applet):
    if applet.settings.compact_menu:
        # Compact Menu
        return [
            MenuItem(t("submenu_app"),
                     action=Menu(
                         *get_about_menu_items(),
                         *get_base_settings(applet),
                         get_theme_menu_item(applet),
                         get_language_menu_item(applet),
                         Menu.SEPARATOR,
                         get_hotkeys_menu_item(applet),
                         get_server_menu_item(applet),
                         *get_footer_items(applet)
                     ))
        ]
    else:
        # High menu
        return [
            Menu.SEPARATOR,
            get_theme_menu_item(applet),
            get_hotkeys_menu_item(applet),
            get_server_menu_item(applet),
            get_language_menu_item(applet),
            MenuItem(t("submenu_app"), Menu(
                *get_about_menu_items(),
                *get_base_settings(applet)
            )),
            *get_footer_items(applet)
        ]


def get_footer_items(applet):
    return [
        MenuItem(t("action_open_appdata"),
                 action=tools.open_app_storage_dir),
        Menu.SEPARATOR,
        MenuItem(t("action_exit"),
                 action=lambda: applet.exit())
    ]


def get_about_menu_items():
    version, _ = tools.get_version()

    return [
        MenuItem("OpenFreebuds ({})".format(version),
                 action=lambda: webbrowser.open("https://melianmiko.ru/openfreebuds")),
        MenuItem(t("action_donate"),
                 action=lambda: webbrowser.open("https://melianmiko.ru/donate")),
        MenuItem("by MelianMiko", None, enabled=False),
        Menu.SEPARATOR
    ]


def get_base_settings(applet):
    settings = applet.settings
    run_at_boot = openfreebuds_backend.is_run_at_boot()

    def on_update_dialog():
        settings.enable_update_dialog = not settings.enable_update_dialog
        settings.write()
        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    def on_compact_menu():
        settings.compact_menu = not settings.compact_menu
        settings.write()
        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    def on_run_at_boot():
        openfreebuds_backend.set_run_at_boot(not run_at_boot)
        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    return [
        MenuItem(t("option_compact"),
                 action=on_compact_menu,
                 checked=lambda _: settings.compact_menu),
        MenuItem(t("option_show_update_dialog"),
                 action=on_update_dialog,
                 checked=lambda _: settings.enable_update_dialog),
        MenuItem(t("option_run_at_boot"),
                 action=on_run_at_boot,
                 checked=lambda _: run_at_boot)
    ]


def get_hotkeys_menu_item(applet):
    settings = applet.settings
    config = settings.hotkeys_config
    all_actions = tool_actions.get_action_names()

    def on_main_toggle():
        applet.settings.enable_hotkeys = not applet.settings.enable_hotkeys
        applet.settings.write()
        tool_hotkeys.start(applet)

        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    hotkey_items = [
        MenuItem(t("prop_enabled"),
                 action=on_main_toggle,
                 checked=lambda _: settings.enable_hotkeys),
        Menu.SEPARATOR
    ]

    for a in all_actions:
        if a in config:
            _add_hotkey_item(hotkey_items, applet, a, all_actions[a], config[a])
        else:
            _add_hotkey_item(hotkey_items, applet, a, all_actions[a], "")

    return MenuItem(t("submenu_hotkeys"), Menu(*hotkey_items))


def get_server_menu_item(applet):
    settings = applet.settings

    def toggle():
        settings.enable_server = not settings.enable_server
        settings.write()
        tool_server.start(applet)

        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    def do_toggle_access(result):
        if not result:
            return

        settings.server_access = not settings.server_access
        settings.write()
        tool_server.start(applet)

        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    def toggle_access():
        if not applet.settings.server_access:
            openfreebuds_backend.ask_question(t("server_global_warn"), do_toggle_access)
        else:
            do_toggle_access(True)

    server_items = [
        MenuItem(t("prop_enabled"),
                 action=toggle,
                 checked=lambda _: settings.enable_server),
        MenuItem(t("prop_server_access"),
                 action=toggle_access,
                 checked=lambda _: settings.server_access),
        Menu.SEPARATOR,
        MenuItem(t("webserver_port") + " " + str(tool_server.get_port()),
                 action=None,
                 enabled=False)
    ]

    return MenuItem(t("submenu_server"), Menu(*server_items))


def get_theme_menu_item(applet):
    current = applet.settings.theme

    theme_picker = [
        # MenuItem(t("submenu_theme"), None, enabled=False),
        MenuItem(t("theme_auto"),
                 action=lambda: applet.set_theme("auto"),
                 checked=lambda _: current == "auto"),
        MenuItem(t("theme_light"),
                 action=lambda: applet.set_theme("light"),
                 checked=lambda _: current == "light"),
        MenuItem(t("theme_dark"),
                 action=lambda: applet.set_theme("dark"),
                 checked=lambda _: current == "dark")
    ]

    return MenuItem(t("submenu_theme"), Menu(*theme_picker))


def get_language_menu_item(applet):
    variants = os.listdir(tools.get_assets_path() + "/locale")
    variants.sort()

    languages = [
        _create_lang_menu_item("", applet),
        Menu.SEPARATOR
    ]

    for a in variants:
        languages.append(_create_lang_menu_item(a, applet))

    return MenuItem(t("submenu_language"), Menu(*languages))


def show_device_info(applet):
    if applet.manager.state != applet.manager.STATE_CONNECTED:
        openfreebuds_backend.show_message(t("mgr_state_2"))
        return

    dev = applet.manager.device

    message = "{} ({})\n\n".format(applet.settings.device_name, applet.settings.address)
    message += "Model: {}\n".format(dev.get_property("device_model", "---"))
    message += "HW ver: {}\n".format(dev.get_property("device_ver", "---"))
    message += "FW ver: {}\n".format(dev.get_property("software_ver", "---"))
    message += "OTA ver: {}\n".format(dev.get_property("ota_version", "---"))
    message += "S/N: {}\n".format(dev.get_property("serial_number", "---"))
    message += "Headphone in: {}\n".format(dev.get_property("is_headphone_in", "---"))

    openfreebuds_backend.show_message(message)


def _add_hotkey_item(items, applet, basename, pretty_name, current_value):
    # Current value
    value = t("hotkey_disabled")
    if current_value != "":
        value = "Ctrl-Alt-" + current_value.upper()

    # On Change action
    def on_change():
        openfreebuds_backend.ask_string(t("change_hotkey_message"),
                                        callback=do_change)

    def do_change(new_value):
        if new_value is None:
            return

        new_value = new_value.lower()
        logging.debug("Set new hotkey for " + basename + " to value " + new_value)
        applet.settings.hotkeys_config[basename] = new_value
        applet.settings.write()
        tool_hotkeys.start(applet)

        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    # Build
    items.append(MenuItem(pretty_name + " (" + value + ")",
                          action=on_change))


def _create_lang_menu_item(value, applet):
    current = applet.settings.language
    value = value.replace(".json", "")

    def on_select():
        applet.settings.language = value
        applet.settings.write()

        if value == "":
            setup_auto()
        else:
            setup_language(value)

        event_bus.invoke(EVENT_UI_UPDATE_REQUIRED)

    return MenuItem("System" if value == "" else ln(value),
                    action=on_select,
                    checked=lambda _: current == value)
