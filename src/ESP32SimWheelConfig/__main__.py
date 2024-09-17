#!/usr/bin/env python3
# ****************************************************************************
# @file __main__.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-21
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

if __package__:
    from . import esp32simwheel
else:
    import esp32simwheel

from nicegui import ui, app, run
import webview
from json import dumps, loads
from appstrings import gettext, set_translation_locale
from lang_en import EN
from lang_es import ES  # NOSONAR
from lang_zh import ZH  # NOSONAR
from rename_devices import get_display_name_from_registry, set_display_name_in_registry
import os
import sys

## NOTE: Must avoid non-ASCII characters at print()

##################################################################################################

print("ESP32SimWheelConfig --------------------------------------------")

for arg in sys.argv:
    arg_cf = arg.casefold()
    if arg_cf == "en":
        print("Language: English")
        set_translation_locale("en")
    if arg_cf == "es":
        print("Language: Espanol")
        set_translation_locale("es")
    if arg_cf == "zh":
        print("Language: Chinese")
        set_translation_locale("zh")

##################################################################################################

_ = gettext

STR = EN
MAX_DISPLAY_NAME_LENGTH = 72
DEFAULT_GROUP_CLASSES = "text-h6 w-full"

##################################################################################################

device = esp32simwheel.SimWheel()

PROFILE_FILE_TYPE = ("Device profiles (*.swjson)",)

##################################################################################################

buttons_map_data = []

__buttons_map_columns = [
    {
        "headerName": _(STR.FIRMWARE_DEFINED),
        "field": "firmware",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
    {
        "headerName": _(STR.USER_DEFINED),
        "field": "user",
        "editable": True,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
    {
        "headerName": _(STR.USER_DEFINED_ALT),
        "field": "userAltMode",
        "editable": True,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
]


def is_running_in_windows() -> bool:
    return os.name == "nt"


def get_16bit_value(value_as_string: str) -> int | None:
    try:
        v = int(value_as_string)
    except Exception:
        try:
            v = int(value_as_string, 16)
        except Exception:
            return None
    if (v > 0) and (v <= 0xFFFF):
        return v
    else:
        return None


def hardware_id_validate(value: str) -> bool:
    return get_16bit_value(value) != None


def please_wait():
    notification = ui.notification(timeout=None)
    notification.message = _(STR.WAIT)
    notification.spinner = True
    return notification


def notify_done(result: bool = True):
    if result:
        ui.notify(_(STR.DONE))
    else:
        ui.notify(_(STR.ERROR), type="negative")


def _refresh_available_devices():
    print("Refreshing device list")
    available_devices_ph.clear()
    count = 0
    for sim_wheel in esp32simwheel.enumerate():
        count += 1
        with available_devices_ph:
            with ui.card() as card:
                card.classes(add="w-full q-ma-xs")
                ui.label(sim_wheel.product_name).classes("text-overline")
                ui.label(sim_wheel.manufacturer).classes("font-thin")
                ui.label(f"S/N: {sim_wheel.device_id:X}").classes("font-thin")
                ui.label(f"VID: {sim_wheel.vid:X}, PID: {sim_wheel.pid:X}").classes("font-thin")
                ui.button(_(STR.SELECT), icon="task_alt").classes("self-center").on(
                    "click", lambda path=sim_wheel.path: select_device(path)
                )
        sim_wheel.close()
    if count == 0:
        with available_devices_ph:
            ui.label(_(STR.NO_DEVICES_FOUND)).classes(
                replace="text-negative", add="text-weight-bold"
            )


async def refresh_available_devices():
    notification = please_wait()
    await run.io_bound(_refresh_available_devices)
    notification.dismiss()


def select_device(path: str):
    device.path = path
    print(f"Selecting {device.path}")
    drawer.toggle()


def auto_select_device():
    for sim_wheel in esp32simwheel.enumerate():
        device.path = sim_wheel.path
        break


def device_refresh():
    device.is_alive


async def on_app_startup():
    print("Starting")
    await refresh_available_devices()
    ui.timer(2.0, device_refresh)


def set_bite_point(value):
    device.bite_point = value


def buttons_group_enable(value: bool):
    # buttons_map_group.set_enabled(value)
    btn_map_reload.set_enabled(value)
    btn_map_save.set_enabled(value)
    btn_map_defaults.set_enabled(value)
    buttons_map_grid.set_visibility(value)


def buttons_map_value_change(changes):
    row_index = changes.args["rowIndex"]
    column_key = changes.args["colId"]
    value = changes.args["value"]
    if (value < 0) or (value > 127):
        ui.notify(
            _(STR.INVALID_BTN),
            type="negative",
            multi_line=True,
        )
    else:
        buttons_map_data[row_index][column_key] = value
        device.set_button_map_tuple(buttons_map_data[row_index])
        # Ensure that the new value was accepted by the device
        try:
            btn_map = device.get_button_map(buttons_map_data[row_index]["firmware"])
            if btn_map != {}:
                buttons_map_data[row_index] = btn_map
        except Exception:
            pass
    buttons_map_grid.update()


def _reload_buttons_map():
    print("Loading buttons map")
    buttons_map_data.clear()
    try:
        for map in device.enumerate_buttons_map():
            buttons_map_data.append(map)
        print(f"Buttons map: {len(buttons_map_data)} items")
        print("Buttons map: Done!")
    except Exception:
        buttons_map_data.clear()
        print("Buttons map: Failed !")


async def reload_buttons_map():
    buttons_group_enable(False)
    notification = please_wait()
    await run.io_bound(_reload_buttons_map)
    buttons_map_grid.update()
    buttons_group_enable(True)
    notification.dismiss()


async def save_now():
    buttons_group_enable(False)
    device.save_now()
    notify_done()
    buttons_group_enable(True)


async def buttons_map_factory_defaults():
    device.reset_buttons_map()
    await reload_buttons_map()
    await save_now()


def profile_group_enable(enabled: bool = True):
    profile_group.enabled = enabled
    btn_load_profile.enabled = enabled
    btn_save_profile.enabled = enabled
    check_profile_buttons_map.enabled = enabled
    check_profile_same_device.enabled = enabled


def _load_profile(filename: str) -> bool:
    print("Loading profile from file")
    try:
        f = open(filename, "r", encoding="utf-8")
        try:
            json = f.read()
            content = loads(json)
            if check_profile_same_device.value:
                id_check_ok = ("deviceID" in content) and (
                    content["deviceID"] == device.device_id
                )
            else:
                id_check_ok = True
            if not id_check_ok:
                f.close()
                return False
            if not check_profile_buttons_map.value:
                content.pop("ButtonsMap", None)
            device.deserialize(content)
        finally:
            f.close()
        return True
    except Exception:
        return False


async def load_profile():
    filename = await app.native.main_window.create_file_dialog(
        allow_multiple=False, file_types=PROFILE_FILE_TYPE
    )
    if filename:
        notification = please_wait()
        profile_group_enable(False)
        done = await run.io_bound(_load_profile, filename[0])
        notification.dismiss()
        profile_group_enable(True)
        notify_done(done)


def _save_profile(filename: str) -> bool:
    print("Saving profile to file")
    try:
        content = device.serialize()
        content["deviceID"] = device.device_id
        if not check_profile_buttons_map.value:
            content.pop("ButtonsMap", None)
        json = dumps(content)
        f = open(filename, "w", encoding="utf-8")
        try:
            f.write(json)
        finally:
            f.close()
        return True
    except Exception:
        return False


async def save_profile():
    filename = await app.native.main_window.create_file_dialog(
        allow_multiple=False,
        dialog_type=webview.SAVE_DIALOG,
        file_types=PROFILE_FILE_TYPE,
    )
    if filename:
        notification = please_wait()
        profile_group_enable(False)
        done = await run.io_bound(_save_profile, filename)
        notification.dismiss()
        profile_group_enable(True)
        notify_done(done)


def on_update_hardware_id():
    vid = device.custom_vid
    pid = device.custom_pid
    custom_vid_input.value = vid
    custom_pid_input.value = pid
    display_name_input.value = get_display_name_from_registry(vid, pid)


async def hardware_id_factory_defaults():
    try:
        device.reset_custom_hardware_id()
        vid = device.custom_vid
        pid = device.custom_pid
        if is_running_in_windows():
            set_display_name_in_registry(vid, pid, None)
        on_update_hardware_id()
        notify_done()
    except Exception:
        notify_done(False)


async def hardware_id_set():
    try:
        display_name = display_name_input.value
        if (display_name != None) and (len(display_name) > MAX_DISPLAY_NAME_LENGTH):
            raise RuntimeError("Display name is too long")
        vid = get_16bit_value(custom_vid_input.value)
        pid = get_16bit_value(custom_pid_input.value)
        device.set_custom_hardware_id(vid, pid)
        if is_running_in_windows():
            set_display_name_in_registry(vid, pid, display_name)
        on_update_hardware_id()
        notify_done()
    except Exception:
        notify_done(False)


async def reverse_left_axis_click():
    try:
        device.reverse_left_axis()
        notify_done()
    except Exception:
        notify_done(False)


async def reverse_right_axis_click():
    try:
        device.reverse_right_axis()
        notify_done()
    except Exception:
        notify_done(False)


##################################################################################################

# Top header

with ui.header():
    with ui.row():
        ui.button(icon="menu").on("click", lambda: drawer.toggle()).props(
            "flat color=white dense"
        )
        headerLabel = ui.label().classes("text-h3 align-middle tracking-wide ellipsis")
        headerLabel.bind_text_from(
            device,
            "is_alive",
            backward=lambda is_alive_value: (
                device.product_name if is_alive_value else _(STR.NO_DEVICE)
            ),
        )

# Drawer

drawer = ui.left_drawer(value=False).props("behavior=desktop")
drawer.on("show", refresh_available_devices)
with drawer:
    with ui.row().classes("w-full"):
        ui.label(_(STR.AVAILABLE_DEVICES)).classes("text-h7")
        ui.space()
        ui.button(icon="refresh").props("flat dense").on(
            "click", refresh_available_devices, throttle=1
        )
    ui.separator()
    available_devices_ph = ui.column().classes("w-full justify-center")

# Main content

## Security lock

read_only_notice = ui.label(_(STR.READ_ONLY_NOTICE))
read_only_notice.classes("self-center").tailwind.font_size("lg").text_color("red-600")
read_only_notice.bind_visibility_from(device, "is_read_only")

## ALT buttons group

alt_buttons_group = ui.expansion(_(STR.ALT_BUTTONS), value=True, icon="touch_app")
alt_buttons_group.classes(DEFAULT_GROUP_CLASSES)
alt_buttons_group.tailwind.font_weight("bold")
alt_buttons_group.bind_visibility_from(device, "has_alt_buttons")
with alt_buttons_group:
    ui.toggle({True: _(STR.ALT_MODE), False: _(STR.REGULAR_BUTTON)}).bind_value(
        device, "alt_buttons_working_mode"
    ).classes("self-center")

## DPAD group

dpad_group = ui.expansion(_(STR.DPAD), value=True, icon="gamepad")
dpad_group.classes(DEFAULT_GROUP_CLASSES)
dpad_group.tailwind.font_weight("bold")
dpad_group.bind_visibility_from(device, "has_dpad")
with dpad_group:
    ui.toggle({True: _(STR.NAV), False: _(STR.REGULAR_BUTTON)}).bind_value(
        device, "dpad_working_mode"
    ).classes("self-center")

## Clutch paddles group

clutch_paddles_group = ui.expansion(_(STR.CLUTCH_PADDLES), value=True, icon="garage")
clutch_paddles_group.classes(DEFAULT_GROUP_CLASSES)
clutch_paddles_group.tailwind.font_weight("bold")
clutch_paddles_group.bind_visibility_from(device, "has_clutch")
with clutch_paddles_group:
    ui.toggle(
        {0: _(STR.CLUTCH), 1: _(STR.AXIS), 2: _(STR.ALT_MODE), 3: _(STR.BUTTON)}
    ).classes("self-center").bind_value(device, "clutch_working_mode")
    ui.label(_(STR.BITE_POINT)).classes("self-center").tailwind.font_size("sm")
    bite_point_slider = ui.slider(min=0, max=254, step=1)
    bite_point_slider.bind_value_from(device, "bite_point")
    bite_point_slider.bind_enabled_from(
        device,
        "clutch_working_mode",
        backward=lambda value: (value == esp32simwheel.ClutchPaddlesWorkingMode.CLUTCH),
    )
    bite_point_slider.on(
        "update:model-value",
        lambda e: set_bite_point(e.args),
        throttle=0.25,
        leading_events=False,
    )
    ui.label(_(STR.ANALOG_AXES)).classes("self-center").bind_visibility_from(
        device, "has_analog_clutch_paddles"
    ).tailwind.font_size("sm")
    ui.button(
        _(STR.RECALIBRATE),
        icon="autorenew",
        on_click=lambda: device.recalibrate_analog_axes(),
    ).bind_visibility_from(device, "has_analog_clutch_paddles").classes("self-center")
    with ui.row().classes("self-center"):
        btn_reverse_left_axis = ui.button(
            _(STR.REVERSE_LEFT_AXIS),
            icon="invert_colors",
            on_click=reverse_left_axis_click,
        ).bind_visibility_from(device, "has_analog_clutch_paddles")
        btn_reverse_right_axis = ui.button(
            _(STR.REVERSE_RIGHT_AXIS),
            icon="invert_colors",
            on_click=reverse_right_axis_click,
        ).bind_visibility_from(device, "has_analog_clutch_paddles")


## Battery group

battery_group = ui.expansion(_(STR.BATTERY), value=True, icon="battery_full")
battery_group.classes(DEFAULT_GROUP_CLASSES)
battery_group.tailwind.font_weight("bold")
battery_group.bind_visibility_from(device, "has_battery")
with battery_group:
    ui.label(_(STR.SOC)).classes("self-center").tailwind.font_size("sm")
    ui.linear_progress(show_value=False).bind_value_from(
        device, "battery_soc", backward=lambda v: v / 100
    )
    ui.button(
        _(STR.RECALIBRATE),
        icon="autorenew",
        on_click=lambda: device.recalibrate_battery(),
    ).bind_visibility_from(device, "battery_calibration_available").classes(
        "self-center"
    )

## Buttons map group

buttons_map_group = ui.expansion(_(STR.BUTTONS_MAP), value=False, icon="map")
buttons_map_group.classes(DEFAULT_GROUP_CLASSES)
buttons_map_group.tailwind.font_weight("bold")
buttons_map_group.bind_visibility_from(device, "has_buttons_map")
with buttons_map_group:
    with ui.row().classes("self-center"):
        btn_map_reload = ui.button(
            _(STR.RELOAD), icon="sync", on_click=reload_buttons_map
        )
        btn_map_save = ui.button(_(STR.SAVE), icon="save", on_click=save_now)
        btn_map_defaults = ui.button(
            _(STR.DEFAULTS), icon="factory", on_click=buttons_map_factory_defaults
        )

    buttons_map_grid = ui.aggrid(
        {
            "columnDefs": __buttons_map_columns,
            "rowData": buttons_map_data,
            "rowSelection": "single",
            "stopEditingWhenCellsLoseFocus": True,
        }
    ).on("cellValueChanged", buttons_map_value_change)

## Profile group

profile_group = ui.expansion(_(STR.LOCAL_PROFILE), value=False, icon="inventory_2")
profile_group.classes(DEFAULT_GROUP_CLASSES)
profile_group.tailwind.font_weight("bold")
profile_group.bind_visibility_from(device, "is_alive")
with profile_group:
    check_profile_same_device = ui.checkbox(_(STR.CHECK_ID), value=True)
    check_profile_same_device.tailwind.font_size("sm")
    with check_profile_same_device:
        ui.tooltip(_(STR.PROFILE_CHECK_TOOLTIP))
    check_profile_buttons_map = ui.checkbox(
        _(STR.INCLUDE_BTN_MAP), value=False
    ).bind_visibility_from(device, "has_buttons_map")
    with ui.row().classes("self-center"):
        btn_load_profile = ui.button(
            _(STR.LOAD), icon="file_upload", on_click=load_profile
        )
        btn_save_profile = ui.button(
            _(STR.SAVE), icon="file_download", on_click=save_profile
        )

## Hardware ID group

hardware_id_group = ui.expansion(
    _(STR.CUSTOM_HARDWARE_ID), value=False, icon="fingerprint"
)
hardware_id_group.classes(DEFAULT_GROUP_CLASSES)
hardware_id_group.tailwind.font_weight("bold")
hardware_id_group.bind_visibility_from(device, "has_custom_hw_id")
with hardware_id_group:
    read_only_notice = (
        ui.label(_(STR.DANGER_ZONE))
        .classes("self-center")
        .tailwind.font_size("lg")
        .text_color("red-600")
    )
    check_not_an_asshole = ui.checkbox(_(STR.I_AM_NOT_AN_ASSHOLE), value=False)
    check_not_an_asshole.style("font-size: 50%")
    check_not_an_asshole.on("update:model-value", on_update_hardware_id)
    display_name_input = ui.input(
        label=_(STR.CUSTOM_DISPLAY_NAME),
        validation={
            _(STR.ERROR): lambda value: (value == None)
            or (len(value) <= MAX_DISPLAY_NAME_LENGTH)
        },
    )
    display_name_input.classes("w-full")
    if is_running_in_windows():
        display_name_input.bind_enabled_from(check_not_an_asshole, "value")
    else:
        display_name_input.enabled = False
    custom_vid_input = ui.input(
        label=_(STR.CUSTOM_VID),
        placeholder=_(STR.VID_PID_FORMAT),
        validation={_(STR.ERROR): hardware_id_validate},
    )
    custom_vid_input.classes("w-full")
    custom_vid_input.bind_enabled_from(check_not_an_asshole, "value")
    custom_pid_input = ui.input(
        label=_(STR.CUSTOM_PID),
        placeholder=_(STR.VID_PID_FORMAT),
        validation={_(STR.ERROR): hardware_id_validate},
    )
    custom_pid_input.classes("w-full")
    custom_pid_input.bind_enabled_from(check_not_an_asshole, "value")
    with ui.row().classes("self-center"):
        btn_hardware_id_update = ui.button(
            _(STR.SAVE), icon="file_download", on_click=hardware_id_set
        )
        btn_hardware_id_update.bind_enabled_from(check_not_an_asshole, "value")
        btn_hardware_id_defaults = ui.button(
            _(STR.DEFAULTS), icon="factory", on_click=hardware_id_factory_defaults
        )
        btn_hardware_id_defaults.bind_enabled_from(check_not_an_asshole, "value")

##################################################################################################

auto_select_device()
app.on_connect(on_app_startup)
ui.run(
    native=True,
    reload=False,
    title="ESP32 open-source sim wheel / button box",
    window_size=(800, 600),
    uvicorn_logging_level="error",
    binding_refresh_interval=0.3,
)
