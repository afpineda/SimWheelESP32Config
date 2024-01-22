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

##################################################################################################

device = esp32simwheel.SimWheel()

##################################################################################################

buttons_map_data = []

__buttons_map_columns = [
    {
        "headerName": "Firmware-defined",
        "field": "firmware",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
    {
        "headerName": "User-defined",
        "field": "user",
        "editable": True,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
    {
        "headerName": "User-defined Alt Mode",
        "field": "userAltMode",
        "editable": True,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
    },
]


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
                ui.button("Select", icon="task_alt").classes("self-center").on(
                    "click", lambda path=sim_wheel.path: select_device(path)
                )
        sim_wheel.close()
    if count == 0:
        with available_devices_ph:
            ui.label("No devices found").classes(
                replace="text-negative", add="text-weight-bold"
            )


async def refresh_available_devices():
    notification = ui.notification(timeout=None)
    notification.message = "Please, wait..."
    notification.spinner = True
    await run.io_bound(_refresh_available_devices)
    # _refresh_available_devices()
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
            "Invalid button number (valid numbers are in the range 0-127)",
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
    notification = ui.notification(timeout=None)
    notification.message = "Please, wait..."
    notification.spinner = True
    await run.io_bound(_reload_buttons_map)
    buttons_map_grid.update()
    buttons_group_enable(True)
    notification.dismiss()


async def save_now():
    buttons_group_enable(False)
    device.save_now()
    ui.notify("Saved!")
    buttons_group_enable(True)


async def buttons_map_factory_defaults():
    device.reset_buttons_map()
    await reload_buttons_map()
    await save_now()


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
            backward=lambda isReady: device.product_name if isReady else "No device",
        )

drawer = ui.left_drawer(value=False).props("behavior=desktop")
drawer.on("show", refresh_available_devices)
with drawer:
    with ui.row().classes("w-full"):
        ui.label("Available devices").classes("text-h6")
        ui.space()
        ui.button(icon="refresh").props("flat dense").on(
            "click", refresh_available_devices, throttle=1
        )
    ui.separator()
    available_devices_ph = ui.column().classes("w-full justify-center")

alt_buttons_group = ui.expansion("ALT buttons", value=True, icon="touch_app")
alt_buttons_group.classes("text-h6")
alt_buttons_group.tailwind.font_weight("bold")
alt_buttons_group.bind_visibility_from(device, "has_alt_buttons")
with alt_buttons_group:
    ui.toggle({True: "ALT mode", False: "Regular button"}).bind_value(
        device, "alt_buttons_working_mode"
    )

dpad_group = ui.expansion("Directional pad", value=True, icon="gamepad")
dpad_group.classes("text-h6")
dpad_group.tailwind.font_weight("bold")
dpad_group.bind_visibility_from(device, "has_dpad")
with dpad_group:
    ui.toggle({True: "Navigation", False: "Regular button"}).bind_value(
        device, "dpad_working_mode"
    )

clutch_paddles_group = ui.expansion("Clutch paddles", value=True, icon="garage")
clutch_paddles_group.classes("text-h6")
clutch_paddles_group.tailwind.font_weight("bold")
clutch_paddles_group.bind_visibility_from(device, "has_clutch")
with clutch_paddles_group:
    ui.toggle({0: "Clutch", 1: "Axis", 2: "Alternate mode", 3: "Button"}).bind_value(
        device, "clutch_working_mode"
    )
    ui.label("Bite point").classes("self-center").tailwind.font_size("sm")
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
    ui.label("Analog axes").classes("self-center").bind_visibility_from(
        device, "has_analog_clutch_paddles"
    ).tailwind.font_size("sm")
    ui.button(
        "Recalibrate",
        icon="autorenew",
        on_click=lambda: device.recalibrate_analog_axes(),
    ).bind_visibility_from(device, "has_analog_clutch_paddles").classes("self-center")

battery_group = ui.expansion("Battery", value=True, icon="battery_full")
battery_group.classes("text-h6")
battery_group.tailwind.font_weight("bold")
battery_group.bind_visibility_from(device, "has_battery")
with battery_group:
    ui.label("State of charge").classes("self-center").tailwind.font_size("sm")
    ui.linear_progress(show_value=False).bind_value_from(
        device, "battery_soc", backward=lambda v: v / 100
    )
    ui.button(
        "Recalibrate",
        icon="autorenew",
        on_click=lambda: device.recalibrate_battery(),
    ).bind_visibility_from(device, "battery_calibration_available").classes(
        "self-center"
    )

buttons_map_group = ui.expansion("Buttons map", value=False, icon="map")
buttons_map_group.classes("text-h6")
buttons_map_group.tailwind.font_weight("bold")
buttons_map_group.bind_visibility_from(device, "has_buttons_map")
with buttons_map_group:
    with ui.row().classes("self-center"):
        btn_map_reload = ui.button(
            "Reload", icon="sync", on_click=reload_buttons_map
        )
        btn_map_save = ui.button("Save", icon="save", on_click=save_now)
        btn_map_defaults = ui.button(
            "Defaults", icon="factory", on_click=buttons_map_factory_defaults
        )

    buttons_map_grid = ui.aggrid(
        {
            "columnDefs": __buttons_map_columns,
            "rowData": buttons_map_data,
            "rowSelection": "single",
            "stopEditingWhenCellsLoseFocus": True,
        }
    ).on("cellValueChanged", buttons_map_value_change)

# ui.page_title("ESP32 open-source sim wheel / button box")

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
