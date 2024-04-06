#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Showcase viewport and hotspot functionality.

Loosely based on poster_demo by @bjerrep
https://github.com/bjerrep/ssd1306/blob/master/examples/poster_demo.py

Needs psutil (+ dependencies) installed::
  $ sudo apt-get install python-dev
  $ sudo pip install psutil
"""

import psutil

from demo_opts import get_device
from luma.core.virtual import viewport, snapshot
from time import sleep
from datetime import datetime
from math import ceil

from hotspot import memory, uptime, cpu_load, clock, network, disk


def position(max):
    forwards = range(0, max)
    backwards = range(max, 0, -1)
    while True:
        for x in forwards:
            yield x
        for x in backwards:
            yield x

def runtime_seconds(start_utc):
    return (datetime.utcnow() - start_utc).total_seconds()

def pause_every(freeze_display_seconds, interval, generator):
    try:
        while True:
            x = next(generator)
            if x % interval == 0:
                start_utc = datetime.utcnow()
                while runtime_seconds(start_utc) < freeze_display_seconds:
                    yield x
            else:
                yield x
    except StopIteration:
        pass


def intersect(a, b):
    return list(set(a) & set(b))


def first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default


def main():
    if device.rotate in (0, 2):
        # Horizontal
        full_widget_width = device.width
        half_widget_width = device.width // 2
        widget_height = device.height
    else:
        # Vertical
        widget_width = device.width
        widget_height = device.height // 2

    cpuload = snapshot(full_widget_width, widget_height, cpu_load.render, interval=0.33)
    mem = snapshot(full_widget_width, widget_height, memory.render, interval=0.33)
    dsk = snapshot(full_widget_width, widget_height, disk.render, interval=1.0)
    eth = first(intersect(psutil.net_if_stats().keys(), ["eth0", "en0"]), "eth0")
    net_eth = snapshot(full_widget_width, widget_height, network.stats(eth), interval=0.5)

    full_widgets = [cpuload, mem, dsk, net_eth]
    half_widgets = []

    freeze_display_seconds = 10

    if device.rotate in (0, 2):
        viewport_width = len(full_widgets) * full_widget_width + len(half_widgets) * half_widget_width
        virtual = viewport(device, width=viewport_width, height=widget_height)

        for i, widget in enumerate(full_widgets):
            virtual.add_hotspot(widget, (i * full_widget_width, 0))

        for i, widget in enumerate(half_widgets):
            virtual.add_hotspot(widget, (len(full_widgets) * full_widget_width + i * half_widget_width, 0))

        for x in pause_every(freeze_display_seconds, device.width, position((len(full_widgets) * full_widget_width + len(half_widgets) * half_widget_width - device.width))):
            virtual.set_position((x, 0))

    # else:
    #     virtual = viewport(device, width=widget_width, height=widget_height * len(widgets))
    #     for i, widget in enumerate(widgets):
    #         virtual.add_hotspot(widget, (0, i * widget_height))

    #     for y in pause_every(freeze_display_seconds, widget_height, position(widget_height * (len(widgets) - 2))):
    #         virtual.set_position((0, y))


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
