#!/usr/bin/env python3
# ****************************************************************************
#  @author Ángel Fernández Pineda. Madrid. Spain.
#  @date 2024-01-21
#  @brief Configuration app for ESP32-based open source sim wheels
#  @copyright Creative Commons Attribution 4.0 International (CC BY 4.0)
# *****************************************************************************

print(f"ESP32SimWheelConfig --------------------------------------------")
print(f"Running as package: {__package__}")
if __package__:
    from . import esp32simwheel
else:
    import esp32simwheel

from nicegui import ui, app, run
import webview
from json import dumps, loads
from appstrings import *

##################################################################################################

# def _(STR.s: str):
#     return s

_ = gettext

class STR(AppStrings):
    _lang = "en"
    ALT_BUTTONS = "ALT buttons"
    ALT_MODE = "Alternate mode"
    ANALOG_AXES = "Analog axes"
    AVAILABLE_DEVICES = "Available devices"
    AXIS = "Axis"
    BATTERY = "Battery"
    BITE_POINT = "Bite point"
    BUTTON = "Button"
    BUTTONS_MAP = "Buttons map"
    CHECK_ID = "Check device identity"
    CLUTCH = "Clutch"
    CLUTCH_PADDLES = "Clutch paddles"
    DEFAULTS = "Defaults"
    DONE = "Done!"
    DPAD = "Directional pad"
    ERROR = "Error!"
    FIRMWARE_DEFINED = "Firmware-defined"
    INCLUDE_BTN_MAP = "Include buttons map"
    INVALID_BTN = "Invalid button number (valid numbers are in the range 0-127)"
    LOAD = "Load"
    LOCAL_PROFILE = "Local profile"
    NAV = "Navigation"
    NO_DEVICE = "No device"
    NO_DEVICES_FOUND = "No devices found"
    PROFILE_CHECK_TOOLTIP = "Uncheck to load settings from another sim wheel/button box"
    RECALIBRATE = "Recalibrate"
    REGULAR_BUTTON =  "Regular button"
    RELOAD = "Reload"
    SAVE = "Save"
    SELECT = "Select"
    SOC = "State of charge"
    USER_DEFINED = "User-defined"
    USER_DEFINED_ALT = "User-defined Alt Mode"
    WAIT = "Please, wait..."



class ES(AppStrings):
    _lang = "es"
    ALT_BUTTONS = "Botones ALT"
    ALT_MODE = "Modo alternativo"
    ANALOG_AXES = "Ejes analógicos"
    AVAILABLE_DEVICES = "Dispositivos disponibles"
    AXIS = "Eje"
    BATTERY = "Batería"
    BITE_POINT = "Punto de mordida"
    BUTTON = "Botón"
    BUTTONS_MAP = "Mapa de botones"
    CHECK_ID = "Comprobar identidad del dispositivo"
    CLUTCH = "Embrague"
    CLUTCH_PADDLES = "Paletas de embrague"
    DEFAULTS = "Por defecto"
    DONE = "¡Hecho!"
    DPAD = "Cruceta direccional"
    ERROR = "¡Error!"
    FIRMWARE_DEFINED = "Del firmware"
    INCLUDE_BTN_MAP = "Incluir mapa de botones"
    INVALID_BTN = "Número de botón inválido (los válidos están en el rango 0-127)"
    LOAD = "Cargar"
    LOCAL_PROFILE = "Perfil local"
    NAV = "Navegación"
    NO_DEVICE = "Sin dispositivo"
    NO_DEVICES_FOUND = "No se halló dispositivo alguno"
    PROFILE_CHECK_TOOLTIP = "Desmarcar para cargar los ajustes de otro volante / caja de botones"
    RECALIBRATE = "Recalibrar"
    REGULAR_BUTTON =  "Botón normal"
    RELOAD = "Recargar"
    SAVE = "Salvar"
    SELECT = "Seleccionar"
    SOC = "Estado de carga"
    USER_DEFINED = "Del usuario"
    USER_DEFINED_ALT = "Del usuario modo ALT"
    WAIT = "Por favor, espere..."

install(STR,True)
install(ES)

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
                card.classes(add="w-full")
                ui.label(sim_wheel.product_name).classes("text-overline")
                ui.label(sim_wheel.manufacturer).classes("font-thin")
                ui.label(f"{sim_wheel.deviceID:X}").classes("font-thin")
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
    print(f"Product name: {device.product_name}")
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
    rowIndex = changes.args["rowIndex"]
    columnKey = changes.args["colId"]
    value = changes.args["value"]
    if (value < 0) or (value > 127):
        ui.notify(
            _(STR.INVALID_BTN),
            type="negative",
            multi_line=True,
        )
    else:
        buttons_map_data[rowIndex][columnKey] = value
        device.set_button_map_tuple(buttons_map_data[rowIndex])
        # Ensure that the new value was accepted by the device
        try:
            map = device.get_button_map(buttons_map_data[rowIndex]["firmware"])
            if map != {}:
                buttons_map_data[rowIndex] = map
        except:
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
    except:
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
    print(f"Loading profile from {filename}")
    try:
        f = open(filename, "r", encoding="utf-8")
        try:
            json = f.read()
            content = loads(json)
            if check_profile_same_device.value:
                idCheckOk = ("deviceID" in content) and (
                    content["deviceID"] == device.deviceID
                )
            else:
                idCheckOk = True
            if not idCheckOk:
                f.close()
                return False
            if not check_profile_buttons_map.value:
                content.pop("ButtonsMap", None)
            device.deserialize(content)
        finally:
            f.close()
        return True
    except:
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
    print(f"Saving profile to {filename}")
    try:
        content = device.serialize()
        content["deviceID"] = device.deviceID
        if not check_profile_buttons_map.value:
            content.pop("ButtonsMap", None)
        json = dumps(content)
        f = open(filename, "w", encoding="utf-8")
        try:
            f.write(json)
        finally:
            f.close()
        return True
    except:
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


##################################################################################################

with ui.header():
    with ui.row():
        ui.button(icon="menu").on("click", lambda: drawer.toggle()).props(
            "flat color=white dense"
        )
        headerLabel = ui.label().classes("text-h3 align-middle tracking-wide ellipsis")
        headerLabel.bind_text_from(
            device,
            "is_alive",
            backward=lambda isReady: device.product_name if isReady else _(STR.NO_DEVICE),
        )

drawer = ui.left_drawer(value=False).props("behavior=desktop")
drawer.on("show", refresh_available_devices)
with drawer:
    with ui.row().classes("w-full"):
        ui.label(_(STR.AVAILABLE_DEVICES)).classes("text-h6")
        ui.space()
        ui.button(icon="refresh").props("flat dense").on(
            "click", refresh_available_devices, throttle=1
        )
    ui.separator()
    available_devices_ph = ui.column().classes("w-full justify-center")

alt_buttons_group = ui.expansion(_(STR.ALT_BUTTONS), value=True, icon="touch_app")
alt_buttons_group.classes("text-h6")
alt_buttons_group.tailwind.font_weight("bold")
alt_buttons_group.bind_visibility_from(device, "has_alt_buttons")
with alt_buttons_group:
    ui.toggle({True: _(STR.ALT_MODE), False: _(STR.REGULAR_BUTTON)}).bind_value(
        device, "alt_buttons_working_mode"
    )

dpad_group = ui.expansion(_(STR.DPAD), value=True, icon="gamepad")
dpad_group.classes("text-h6")
dpad_group.tailwind.font_weight("bold")
dpad_group.bind_visibility_from(device, "has_dpad")
with dpad_group:
    ui.toggle({True: _(STR.NAV), False: _(STR.REGULAR_BUTTON)}).bind_value(
        device, "dpad_working_mode"
    )

clutch_paddles_group = ui.expansion(_(STR.CLUTCH_PADDLES), value=True, icon="garage")
clutch_paddles_group.classes("text-h6")
clutch_paddles_group.tailwind.font_weight("bold")
clutch_paddles_group.bind_visibility_from(device, "has_clutch")
with clutch_paddles_group:
    ui.toggle(
        {0: _(STR.CLUTCH), 1: _(STR.AXIS), 2: _(STR.ALT_MODE), 3: _(STR.BUTTON)}
    ).bind_value(device, "clutch_working_mode")
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

battery_group = ui.expansion(_(STR.BATTERY), value=True, icon="battery_full")
battery_group.classes("text-h6")
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

buttons_map_group = ui.expansion(_(STR.BUTTONS_MAP), value=False, icon="map")
buttons_map_group.classes("text-h6")
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

profile_group = ui.expansion(_(STR.LOCAL_PROFILE), value=False, icon="inventory_2")
profile_group.classes("text-h6")
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

##################################################################################################

auto_select_device()
app.on_connect(on_app_startup)
ui.run(
    native=True,
    reload=False,
    title="ESP32 open-source sim wheel / button box",
    window_size=(550, 600),
    uvicorn_logging_level="error",
    binding_refresh_interval=0.3,
)
