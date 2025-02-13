#!/usr/bin/env python3
# ****************************************************************************
# @file __pixels_test__.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2025-02-13
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

if __package__:
    from . import esp32simwheel
else:
    import esp32simwheel

import time
import sys

###############################################################################


def pixel_control_enumerate():
    for device in esp32simwheel.enumerate(configurable_only=False):
        if device.has_pixel_control:
            yield device


def set_pixel(device, group, index):
    for i in range(device.pixel_count(group)):
        device.pixel_set(group, i, 0, 0, 0)
    device.pixel_set(group, index, 255, 255, 255)


def next_index(device):
    for group in esp32simwheel.PixelGroup:
        device.pixel_index[group] = device.pixel_index[group] + 1
        if device.pixel_index[group] >= device.pixel_count(group):
            device.pixel_index[group] = 0
        # print(f"GRP: {group} IDX: {device.pixel_index[group]}")


###############################################################################

if len(sys.argv) > 1:
    fps = int(sys.argv[1])
    if fps < 0:
        fps = 50
else:
    fps = 50

print("------------------")
print("Pixel control test")
print(f"FPS limit: {fps}")
print("------------------")

if fps==0:
    frame_limit_time = 0.0
else:
    frame_limit_time = 1 / fps

devices = list(pixel_control_enumerate())
for sim_wheel in devices:
    print(f"Found : '{sim_wheel.manufacturer}' / '{sim_wheel.product_name}'")
    sim_wheel.pixel_index = [0, 0, 0]
    sim_wheel.pixel_reset()

print("-------")
print("Running")
print("-------")

while True:
    for device in devices:
        for group in esp32simwheel.PixelGroup:
            set_pixel(device, group, device.pixel_index[group])
            # print(f"GRP: {group} IDX: {device.pixel_index[group]}")
        next_index(device)
        device.pixel_show()
    if frame_limit_time>0.0:
        time.sleep(frame_limit_time)
