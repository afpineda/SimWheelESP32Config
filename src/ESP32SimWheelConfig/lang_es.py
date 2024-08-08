# ****************************************************************************
# @file lang_es.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-25
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

from enum import Enum
from appstrings import install


class ES(Enum):
    _lang = "es"
    _domain = "ESP32SimWheelConfig"
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
    PROFILE_CHECK_TOOLTIP = (
        "Desmarcar para cargar los ajustes de otro volante / caja de botones"
    )
    RECALIBRATE = "Recalibrar"
    REGULAR_BUTTON = "Botón normal"
    RELOAD = "Recargar"
    SAVE = "Salvar"
    SELECT = "Seleccionar"
    SOC = "Estado de carga"
    USER_DEFINED = "Del usuario"
    USER_DEFINED_ALT = "Del usuario modo ALT"
    WAIT = "Por favor, espere..."
    READ_ONLY_NOTICE = "Bloqueo de seguridad. Sólo lectura."
    DANGER_ZONE = "Zona de peligro"
    CUSTOM_HARDWARE_ID = "ID a medida"
    I_AM_NOT_AN_ASSHOLE = "Sé lo que hago"
    CUSTOM_VID = "ID de fabricante a medida (VID)"
    CUSTOM_PID = "ID de producto a medida (PID)"
    VID_PID_FORMAT = "Entero sin signo de 16 bits"
    CUSTOM_DISPLAY_NAME = "Nombre en pantalla a medida (solo Windows)"
    REVERSE_LEFT_AXIS = "Invertir eje izquierdo"
    REVERSE_RIGHT_AXIS = "Invertir eje derecho"


install(ES)
