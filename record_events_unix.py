#!/usr/env python
#
# Records mouse and keyboards events and converts the result
# to a Sikulix script.
#
# Written by Tom Hunter
# Copyright May 16th, 2024
# Licence GPL3

# Install python-xlib for Xlib (no longer needed, but still possible. Install python-pynput)
# This code is based on the example record_demo.py

import sys
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

local_dpy = display.Display()
record_dpy = display.Display()

ctx = None
myeventlist = []
first_time = True
simple_way_to_exit = True
escape_cnt = 0

# External handlers
first_time_handler = None
keyboard_handler = None
motion_handler = None
mouse_button_handler = None

def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            return name[3:]
    return "[%d]" % keysym

def record_callback(reply):
    global myeventlist
    global first_time
    global escape_cnt 
    if reply.category != record.FromServer:
        return
    if reply.client_swapped:
        print("* received swapped protocol data, cowardly ignored")
        return
    if not len(reply.data) or reply.data[0] < 2:
        # not an event
        return

    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)

        if first_time_handler and first_time:
            first_time_handler(event.time)
            first_time = False
        # All pen events are KeyReleases.
        if event.type in [X.KeyPress, X.KeyRelease]:
            pr = event.type == X.KeyPress and "Press" or "Release"

            keysym = local_dpy.keycode_to_keysym(event.detail, 0)
            if not keysym:
                myeventlist.append("%d\tKeyCode\t%s\t%s\t%d\t%d"%(event.time, pr, str(event.detail), event.root_x, event.root_y))
                print("KeyCode%s" % pr, event.detail)
            else:
                myeventlist.append("%d\tKey\t%s\t%s\t%d\t%d"%(event.time, pr, lookup_keysym(keysym), event.root_x, event.root_y))
                if keyboard_handler:
                    keyboard_handler(event.time, pr, lookup_keysym(keysym), event.root_x, event.root_y )

            if simple_way_to_exit:
                # Press Escape to quit
                if event.type == X.KeyPress and keysym == XK.XK_Escape:
                    local_dpy.record_disable_context(ctx)
                    local_dpy.flush()
                    return
            else:
                if event.type == X.KeyPress and keysym == XK.XK_Escape:
                    escape_cnt += 1
                elif event.type == X.KeyRelease and keysym == XK.XK_Escape:
                    pass
                else:
                    escape_cnt = 0
                if escape_cnt > 2:
                    local_dpy.record_disable_context(ctx)
                    local_dpy.flush()
                    return

        elif event.type == X.ButtonPress:
            myeventlist.append("%d\tButton\tPress\t%s\t%d\t%d"%(event.time, str(event.detail), event.root_x, event.root_y))
            if mouse_button_handler:
                mouse_button_handler(event.time, "Press", event.detail, event.root_x, event.root_y)
        elif event.type == X.ButtonRelease:
            myeventlist.append("%d\tButton\tRelease\t%s\t%d\t%d"%(event.time, str(event.detail), event.root_x, event.root_y))
            if mouse_button_handler:
                mouse_button_handler(event.time, "Release", event.detail, event.root_x, event.root_y)
        elif event.type == X.MotionNotify:
            myeventlist.append("%d\tMotion\t%d\t%d"%(event.time, event.root_x, event.root_y))
            if motion_handler:
                motion_handler(event.time, event.root_x, event.root_y)

def start_up():
    """ Initialise and start the recording of events. """
    global ctx
    # Check if the extension is present
    if not record_dpy.has_extension("RECORD"):
        print("RECORD extension not found")
        sys.exit(1)
    r = record_dpy.record_get_version(0, 0)
    print("RECORD extension version %d.%d" % (r.major_version, r.minor_version))

    # Create a recording context; we only want key and mouse events
    ctx = record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress, X.MotionNotify, X.CurrentTime, X.CursorShape),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }])

    # Enable the context; this only returns after a call to record_disable_context,
    # while calling the callback function in the meantime
    record_dpy.record_enable_context(ctx, record_callback)

def clean_up():
    # Finally free the context
    global ctx
    record_dpy.record_free_context(ctx)

if __name__ == "__main__":
    import json    

    print("Recording keys and mouse. Press Escape to stop recording.")
    filename = "/tmp/eventrecord.txt"
    print("Raw data is dumped in %s. [timestamp in ms, action, details]"%filename)

    start_up()

    # Store output.
    f = open(filename, "w", encoding="utf-8")
    for event in myeventlist:
        f.write(event + "\n")
    f.close()

    with open(filename[:-3] + "json", "w") as file:
        json.dump(myeventlist, file)

    clean_up()
