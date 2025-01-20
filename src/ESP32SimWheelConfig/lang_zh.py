# ****************************************************************************
# @file lang_zh.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-04-03
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

from enum import Enum
from appstrings import install


class ZH(Enum):
    _lang = "zh"
    _domain = "ESP32SimWheelConfig"
    ALT_BUTTONS = "ALT 按钮"
    ALT_MODE = "备用模式"
    ANALOG_AXES = "模拟轴"
    AVAILABLE_DEVICES = "可用设备"
    AXIS = "轴"
    BATTERY = "电池"
    BITE_POINT = "咬合点"
    BUTTON = "按钮"
    BUTTONS_MAP = "按钮地图"
    CHECK_ID = "检查设备身份"
    CLUTCH = "离合器"
    CLUTCH_PADDLES = "离合器拨片"
    DEFAULTS = "默认值"
    DONE = "完成"
    DPAD = "定向垫"
    ERROR = "错误"
    FIRMWARE_DEFINED = "固件定义"
    INCLUDE_BTN_MAP = "包括按钮地图"
    INVALID_BTN = "按钮编号无效（有效编号范围为 0-127)"
    LOAD = "载荷"
    LOCAL_PROFILE = "当地概况"
    NAV = "导航"
    NO_DEVICE = "无设备"
    NO_DEVICES_FOUND = "未找到设备"
    PROFILE_CHECK_TOOLTIP = "取消选中可从另一个模拟滚轮或按钮盒加载设置"
    RECALIBRATE = "重新校准"
    REGULAR_BUTTON = "常规按钮"
    RELOAD = "重新加载"
    SAVE = "节省"
    SELECT = "选择"
    SOC = "充电状态"
    USER_DEFINED = "用户自定义"
    USER_DEFINED_ALT = "用户自定义 Alt 模式"
    WAIT = "请稍候..."
    READ_ONLY_NOTICE = "安全锁。设备是只读的。"
    DANGER_ZONE = "危险区域"
    CUSTOM_HARDWARE_ID = "自定义硬件 ID"
    I_AM_NOT_AN_ASSHOLE = "我知道我在做什么"
    CUSTOM_VID = "自定义供应商 ID （VID）"
    CUSTOM_PID = "自定义产品 ID （PID）"
    VID_PID_FORMAT = "16 位无符号整数"
    CUSTOM_DISPLAY_NAME = "自定义显示名称（仅限 Windows）"
    REVERSE_LEFT_AXIS = "反转左轴"
    REVERSE_RIGHT_AXIS = "反转右轴"
    LAUNCH_CTRL_LEFT_MASTER = "發射控制（左主凸輪）"
    LAUNCH_CTRL_RIGHT_MASTER = "發射控制（右主凸輪）"


install(ZH)
