#!/usr/env python
# coding=utf-8
#
# Main program to record the user and convert the events to Sikulix commands
#
# Copyright (C) 2024 Tom Hunter
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = u'Tom Hunter'
__version__ = (0, 0, 1)

import sys
import os
import code_events
import record_events

help_text = """ Usage: python sikulix_recorder.py <name Sikulix folder>

--help  -h      show this help.
--tripple -t    Press Escape three times to exit, instead of once.

The number of mouseMove commands generated depends on two factors: the 
precision and the step size. The step size determines how many events
of the motion are skipped. 0 means no events are skipped (this means
many code lines as each motion event generates two lines of code).
1 is every other event and so on.
If the difference in slope of the two event points is greater than
precision, the second point is selected.
So if you need great precision use a step size of 0 and a precision of
0.0. This is useful for drawing. If you just move your mouse in 
straight lines to select buttons, the precision can be much lower
(which means the number the precision is set can be much higher).

--precision -p  <float>     Set precision. Default = 6
--step  -s  <int>           Set step size. Default = 15

While recording hold LEFT SHIFT and move the mouse from the upper left
corner to the bottom right corner of the area you want to save. Click
inside this area to store the x and y offset from the middle of the
image.

While recording hold LEFT CTRL and move the mouse to indicate an area
to highlight this area.

--version   -v              Shows version number and quits.
"""

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) < 2:
        print(help_text)
    else:
        # Creating a folder_name
        folder_name = sys.argv[1]
        if not folder_name.endswith(".sikuli") and not folder_name.endswith(".sikuli" + os.path.sep):
            base_name = folder_name
            folder_name += ".sikuli"
        else:
            base_name = folder_name[:-7]
        if not folder_name.endswith(os.path.sep):
             folder_name += os.path.sep 
        filename = folder_name + base_name + ".py"
        os.makedirs(folder_name, exist_ok = True)
        code_events.output_folder = folder_name

        # Setting up the recorder's code handlers
        record_events.first_time_handler = code_events.handle_first_time
        record_events.keyboard_handler = code_events.handle_keys
        record_events.motion_handler = code_events.handle_mouse_motion
        record_events.mouse_button_handler = code_events.handle_mouse_buttons

        # Handle the other command line arguments
        if "--version" in sys.argv or "-v" in sys.argv:
            print("Version: %s" % __version__)
            sys.exit(0)
        if "--tripple" in sys.argv or "-t" in sys.argv:
            record_events.simple_way_to_exit = False
            print("Repeat pressing Esc three times to stop recording.")
        else:
            print("Press Esc to stop recording.")
        if "--precision" in sys.argv or "-p" in sys.argv:
            try:
                index = sys.argv.index("--precision")
            except:
                try:
                    index = sys.argv.index("-p")
                except:
                    pass
            if len(sys.argv) < index + 2:
                print("Missing value for 'precision'. Please add a number after the switch.")
                sys.exit(1)
            try:
                code_events.precision = float(sys.argv[index + 1])
                print("Set precision to:" +  code_events.precision)
            except:
                print("Warning: unable to get value for precision. Not a float number.")
                sys.exit(1)
        if "--step" in sys.argv or "-s" in sys.argv:
            try:
                index = sys.argv.index("--step")
            except:
                try:
                    index = sys.argv.index("-s")
                except:
                    pass
            if len(sys.argv) < index + 2:
                print("Missing value for 'step'. Please add a number after the switch.")
                sys.exit(1)
            try:
                code_events.step_size = int(sys.argv[index + 1])
                print("Set step size to: " + code_events.step_size)
            except:
                print("Warning: unable to get value for step size. Not a integer.")
                sys.exit(1)
        
        

        print("Storing the recording in '%s'. Overwriting if it already exists." % folder_name)
        record_events.start_up()
        # Waiting for the previous command to exit.

        record_events.clean_up()
        code_events.clean_up()

        # Save the Sikulix code.
        f = open(filename, "w", encoding="utf-8")
        # It seems like we are recording the Enter of the start command. Remove it
        code = code_events.cmds[2:]
        if len(code) >= 2 and code[1] == "type(Key.ENTER)" or code[1] == "type(\"enter\")":
            code = code[2:]

        # Remove the ESC sequence needed to stop the recorder.
        while len(code) and code[-1] == "type(Key.ESC)" or code[-1] == "type(\"esc\")":
            code = code[:-2]
        for r in code:
            f.write(r + "\n")
        f.close()