#!/usr/env python
#
# Used to convert a myeventslist list to Sikulix commands
# Now it handles events directly so the right image is captured.
#
# Written by Tom Hunter
# Copyright May 16th, 2024
# python -m pip install pillow
# Licence GPL3


import json
from PIL import ImageGrab

shift_chars = {"US": {",":"<", ".":">", "/":"?", ";":":", "'":"\\\"", "\\":"|", "[":"{", "]":"}", "`":"~", 
                      "1":"!", "2":"@", "3":"#", "4":"$", "5":"%", "6":"^", "7":"&", "8":"*", "9":"(", 
                      "0":")", "-":"_", "=":"+"}
                }
keyboard_layout = "US"

mouse_button_codes = {1:"Button.LEFT", 2:"Button.MIDDLE", 3:"Button.RIGHT", 4:"Button.WHEEL_UP", 5:"Button.WHEEL_DOWN"}
# Needed when using xlib instead of pynput
special_chars = {"comma":",", "period":".", "slash":"/", "semicolon":";", "apostrophe":"'", "backslash":"\\",
                             "bracketleft":"[", "bracketright":"]", "grave":"`", "minus":"-", "equal":"=",}
# For xlib
# sikulixkeys = {"Return":"ENTER", "Escape":"ESC", "Tab":"TAB", "BackSpace":"BACKSPACE", 
#                "Delete": "DELETE", "F1":"F1", "F2":"F2", "F3":"F3", "F4":"F4", 
#                "F5":"F5", "F6":"F6", "F7":"F7", "F8":"F8", "F9":"F9", "F10":"F10", 
#                "F11":"F11", "F12":"F12", "F13":"F13", "F14":"F14", "F15":"F15", 
#                "Insert": "INSERT", "space": "SPACE", "Home": "HOME", "End":"END", 
#                "Left":"LEFT", "Right":"RIGHT", "Down":"DOWN", "Up":"UP", "Next":"PAGE_DOWN", 
#                "Page_Up":"PAGE_UP", "Print":"PRINTSCREEN", "Pause":"PAUSE", 
#                "Caps_Lock":"CAPS_LOCK", "Scroll_Lock":"SCROLL_LOCK", "Num_Lock":"NUM_LOCK",
#                "KP_Insert":"NUM0", "KP_End":"NUM1", "KP_Down":"NUM2", "KP_Next":"NUM3", 
#                "KP_Left":"NUM4", "KP_Begin":"NUM5", "KP_Right":"NUM6", 
#                "KP_Home":"NUM7", "KP_Up":"NUM8", "KP_Page_Up":"NUM9", "KP_Delete":"SEPARATOR", 
#                "KP_Add":"ADD", "KP_Subtract":"MINUS", "KP_Multiply":"MULTIPLY",
#                "KP_Divide":"DIVIDE", "KP_Enter": "ENTER"}
# For pynput
sikulixkey = {"enter":"ENTER", "esc":"ESC", "tab":"TAB", "backspace":"BACKSPACE", 
               "delete": "DELETE", "f1":"F1", "f2":"F2", "f3":"F3", "f4":"F4", 
               "f5":"F5", "f6":"F6", "f7":"F7", "f8":"F8", "f9":"F9", "f10":"F10", 
               "f11":"F11", "f12":"F12", "f13":"F13", "f14":"F14", "f15":"F15", 
               "insert": "INSERT", "space": "SPACE", "home": "HOME", "end":"END", 
               "left":"LEFT", "right":"RIGHT", "down":"DOWN", "up":"UP", "page_down":"PAGE_DOWN", 
               "page_up":"PAGE_UP", "print_screen":"PRINTSCREEN", "pause":"PAUSE", 
               "caps_lock":"CAPS_LOCK", "scroll_lock":"SCROLL_LOCK", "num_lock":"NUM_LOCK",
               "KP_Divide":"DIVIDE", "<65437>":"5"}

# Globals to make this work.
output_folder = "/tmp/test.sikuli/"
cmds = []
mouse_movements = []

previous_event = None
previous_char = None
motions = [] # Stores a list of motion events, that is converted to commands when something else happens (a click, a key pressed, end of program)
time_of_last_command = None
key_pressed_while_holding_ctrl_or_shift = False
mouse_moved = False
left_shift_region = False       # Just created an image by holding left SHIFT and moving the mouse.
current_cmds_length = 0         # When start holding left SHIFT or CTRL we record the length of the commands list to be able to later remove the motion commands
center_of_image = [0,0]
image_cnt = 1                   # The name of an image stored while holding LEFT SHIFT
fname = ""                      # The actual file name of an image stored while holding LEFT SHIFT
coordinates = None              # The coordinates of this image on the screen.
start_snapping = False          # After releasing the left shift the mouse will move to the click point. Then the underlaying screen might change, so we will take a snapshot with the same name each motion event until we receive a button press.
precision = 6
step_size = 15                  # the number of events that are always skipped between two mouseMove commands
modifiers = {"button 1 down": False, "button 2 down": False, "button 3 down": False, "button 4 down": False, 
            "button 5 down": False, "left control down": False, "right control down": False, "left shift down": False, 
            "right shift down": False, "left alt down": False, "right alt down": False,  
            "left windows down": False, "right windows down": False, "context menu down": False}


def handle_first_time(time):
    """ This function should be called when the first event is received before it is handled. """
    global time_of_last_command
    time_of_last_command = time

def _get_slopes(x_values, y_values):
    """ Returns a list of changes in slope. """
    idx = []
    if x_values[1] - x_values[0] == 0:
        prior_slope = "straight up or down"
    else:
        prior_slope = float(y_values[1] - y_values[0]) / (x_values[1] - x_values[0])
    for n in range(2, len(x_values)):  # Start from 3rd pair of points.
        if x_values[n] - x_values[n - 1] == 0:
            slope = "straight up or down"
        else:
            slope = float(y_values[n] - y_values[n - 1]) / (x_values[n] - x_values[n - 1])
        
        if type(slope) is str or type(prior_slope) is str:
            if slope != prior_slope:
                if not type(slope) is str:
                    if abs(slope) < precision:
                        idx.append(n)
                else:
                    if abs(prior_slope) < precision:
                        idx.append(n)
        elif abs(slope - prior_slope) > precision:
            idx.append(n)
        prior_slope = slope
    return idx

def _set_modifiers(char, value):
    """ Maintains the list that shows which modifiers are currently pressed. 
        Returns the list and if the current key is a modifier. """
    global modifiers
    key_is_modifier = True
    if char == "Control_L":
        modifiers["left control down"] = value
    elif char == "Shift_L":
        modifiers["left shift down"] = value
    elif char == "Alt_L":
        modifiers["left alt down"] = value
    elif char == "Super_L":
        modifiers["left windows down"] = value
    elif char == "Control_R":
        modifiers["right control down"] = value
    elif char == "Shift_R":
        modifiers["right shift down"] = value
    elif char == "Alt_R":
        modifiers["right alt down"] = value
    elif char == "Super_R":
        modifiers["right windows down"] = value
    elif char == "Menu":
        modifiers["context menu down"] = value
    else:
        key_is_modifier = False
    return key_is_modifier

def _handle_motions():
    """ Returns the moveMouse commands. """
    global cmds
    global time_of_last_command
    global motions
    # We need at least three point to calculate the slope of the lines.
    if len(motions) < 3:
        for motion in motions:
            x = motion[-2]
            y = motion[-1]
            time = motion[0]
            cmds.append("Settings.MoveMouseDelay = %f" %((time - time_of_last_command)/1000.0))
            cmds.append("mouseMove(Location(%d,%d))"%(x,y))
            time_of_last_command = time            
        motions = []
        return
    # Get the x,y coordinates of the events
    x_values = []
    y_values = []
    for motion in motions:
        # print(motion)
        x_values.append(motion[-2])
        y_values.append(motion[-1])
    # Find the events where the slope changes.
    slope_indices = _get_slopes(x_values, y_values)
    # Clean up the number by limiting the number of successive indices. The assumption is that there will be 
    # an event per pixel move, and we want to cover some distance before adding a new mouse move command.
    final_indices = [0]   # Always append start point
    old_si = -1000000
    for si in slope_indices:
        if si - old_si > step_size:
            final_indices.append(si)
            old_si = si
    final_indices.append(len(motions) - 1)      # Always append end point

    # Create moveMouse commands for the end of straight lines.
    for idx in final_indices:
        motion = motions[idx]
        x = motion[-2]
        y = motion[-1]
        time = motion[0]
        cmds.append("Settings.MoveMouseDelay = %f" %((time - time_of_last_command)/1000.0))
        cmds.append("mouseMove(Location(%d,%d))"%(x,y))
        time_of_last_command = time
    motions = []


def handle_mouse_buttons(time, press, buttonno, x, y):
    """ Handler for mouse button events. """
    # Store the event string
    global mouse_moved
    global time_of_last_command
    global previous_event
    global left_shift_region
    global modifiers
    global cmds
    global start_snapping
    
    sp = [time, press, buttonno, x, y]
    mouse_movements.append([time, x, y])
    
    # We have something other than motion (a mouse button event), so we need to handle the motion.
    _handle_motions()

    if press == "Release":
        if left_shift_region:
            cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
            # Create offset within the image created by pressing SHIFT while moving the mouse.
            if buttonno == 1:
                cmds.append("hover(Location(%d, %d))"%(x,y))
                dx = x - center_of_image[0]
                dy = y - center_of_image[1]
                cmds.append("click(Pattern(\"%s.png\").similar(0.9).targetOffset(%d,%d))"%(str(image_cnt - 1), dx,dy))
            elif buttonno == 3:
                cmds.append("hover(Location(%d, %d))"%(x,y))
                dx = x - center_of_image[0]
                dy = y - center_of_image[1]
                cmds.append("rightClick(Pattern(\"%s.png\").similar(0.9).targetOffset(%d,%d))"%(str(image_cnt - 1), dx,dy))
            left_shift_region = False
        else:
            if buttonno in [4,5]: # Handle mousewheel. TODO and linux?
                no_of_clicks = 1
                cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                # TODO The code below will combine several mouse wheel commands into one. (Delete the wait command in the line above) But it will loose the timing information
                # if cmds and cmds[-1].startswith("wheel(%s, "%mouse_button_codes[buttonno]):
                #     no_of_clicks = int(cmds[-1][len("wheel(%s, "%mouse_button_codes[buttonno]):-1])
                #     no_of_clicks += 1
                #     cmds = cmds[:-1]
                cmds.append("wheel(%s, %d)" % (mouse_button_codes[buttonno], no_of_clicks))
            else:
                cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                cmds.append("hover(Location(%d, %d))"%(x,y))
                cmds.append("mouseUp(%s)"%(mouse_button_codes[buttonno]))   
        modifiers["button " + str(buttonno) + "down"] = False
    elif press == "Press":
        # Only create a mouseDown if it is not a mouse wheel action. # TODO: check this for windows.
        if not buttonno in [4, 5]:
            if buttonno == 1:
                print("Turn off snapping")
                # We are done hysterically saving the background image we are clicking on (or next to)
                start_snapping = False
            modifiers["button " + str(buttonno) + "down"] = True
            if not left_shift_region:
                cmds.append("hover(Location(%d, %d))"%(x,y))
                cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                cmds.append("mouseDown(%s)"%(mouse_button_codes[buttonno]))
    if not (buttonno in [4,5] and press == "Press"):
        # Not for the press event of the mouse wheel, because then the wait time is always 0
        time_of_last_command = time 
    previous_event = sp
    mouse_moved = False   

def handle_mouse_motion(time, x, y):
    global mouse_moved
    global previous_event
    global coordinates
    global fname
    global start_snapping

    sp = [time, x, y]
    mouse_movements.append(sp) 
    if start_snapping and ((x - coordinates[0])%20 > 15 or (y - coordinates[1])%20 > 15):
        # (x - coordinates[0])%20 > 15 is not exactly fail proof, but it ensures that not every miniature movement results in saving a screenshot and thus increasing the event queue because the program can't keep up.
        screenshot = ImageGrab.grab(coordinates)
        screenshot.save(fname, format="png")     

    # We only store a list of motion events for later processing.
    motions.append(sp)
    mouse_moved = True
    previous_event = sp  

def handle_keys(time, press, char, x, y):
    global mouse_moved
    global time_of_last_command
    global previous_event
    global previous_char
    global key_pressed_while_holding_ctrl_or_shift
    global left_shift_region
    global center_of_image
    global image_cnt
    global cmds
    global current_cmds_length
    global coordinates
    global fname
    global start_snapping    
    sp = [time, press, char, x, y]
    mouse_movements.append([time, x, y])

    # We have something other than motion (a mouse button event), so we need to handle the motion.
    _handle_motions()

    if press == "Release":
        # Handle key presses
        left_shift_region = False
        key_is_modifier = _set_modifiers(char, False)
        if char == "Control_L":
            if not key_pressed_while_holding_ctrl_or_shift and previous_char[2] == "Control_L":
                if mouse_moved:
                    # A region was selected. Highlight it.
                    no_to_remove = len(cmds) - current_cmds_length
                    cmds = cmds[:-no_to_remove]
                    cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                    old_x = previous_char[-2]
                    old_y = previous_char[-1]
                    w = abs(old_x - x)
                    h = abs(old_y - y)
                    x1 = min(old_x, x)
                    y1 = min(old_y, y)
                    cmds.append("reg = Region(%d, %d, %d, %d)" %(x1, y1, w, h))
                    seconds = 2.0
                    color = "#FF0000"
                    cmds.append("reg.highlight(%d, \"%s\")" % (seconds, color))
                else:
                    cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                    # The button was pressed but never combined with another key and the mouse never moved
                    cmds.append("# mark_point(Location(%d, %d))" % (x, y))
                time_of_last_command = time
                previous_char = previous_event = sp                        
        if char == "Shift_L":
            if not key_pressed_while_holding_ctrl_or_shift and previous_char[2] == "Shift_L":
                cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                if mouse_moved:
                    # A region was selected while holding SHIFT (but no clicking). Take a snapshot.
                    no_to_remove = len(cmds) - current_cmds_length
                    cmds = cmds[:-no_to_remove]
                    cmds.append("wait(%f)"%((time - time_of_last_command)/1000.0))
                    old_x = previous_char[-2]
                    old_y = previous_char[-1]
                    try:
                        fname = output_folder + str(image_cnt) + ".png"
                        if old_x > x:
                            tmp = x
                            x = old_x
                            old_x = tmp
                        if old_y > y:
                            tmp = y
                            y = old_y
                            old_y = tmp
                        coordinates = bbox=(old_x, old_y, x, y)
                        start_snapping = True
                        screenshot = ImageGrab.grab(bbox=(old_x, old_y, x, y))
                        screenshot.save(fname, format="png")
                        left_shift_region = True
                        cmds.append("# wait(\"%s\")" % (str(image_cnt) + ".png"))   # This type of wait will throw off the timing
                        center_of_image = [int((x + old_x)/2.0), int((y - old_y)/2.0)]
                    except Exception as e: 
                        print(e)
                        print("Unable to generate: " + fname)
                    image_cnt += 1
                    # If this one is True the next click will be an offset to the image just created.
                time_of_last_command = time
                previous_char = previous_event = sp                        
        if not key_is_modifier:            
            if char in special_chars:
                char = special_chars[char]
            t = 0.0
            if previous_char == previous_event and previous_char:
                t = (time - previous_char[0]) / 1000
            cmds.append("Settings.TypeDelay = " + str(t))

            modify = ""
            if modifiers["left alt down"]:
                modify += "+Key.ALT"
            elif modifiers["right alt down"]:
                modify += "+Key.ALTGR"
            elif modifiers["left control down"] or modifiers["right control down"]:
                modify += "+Key.CTRL"
                key_pressed_while_holding_ctrl_or_shift = True
            elif modifiers["left shift down"] or modifiers["right shift down"]:
                if modifiers["left shift down"]:
                    key_pressed_while_holding_ctrl_or_shift = True
                if char in ",./;'\\[]`1234567890-=<":
                    char = shift_chars[keyboard_layout][char]
                else:
                    modify += "+Key.SHIFT"
            elif modifiers["left windows down"] or modifiers["right windows down"]:
                modify += "+Key.WIN"
            elif modifiers["context menu down"]:
                modify += "+Key.META"
            if modify:
                modify = modify[1:]

            if not char in ["Return", "Escape", "Tab", "BackSpace", "Delete", "F1", "F2", "F3", "F4", 
                            "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "Insert", 
                            "space", "Home", "End", "Left", "Right", "Down", "Up", "Next", "Page_Up", "Print", 
                            "Pause", "Caps_Lock", "Scroll_Lock", "Num_Lock", "KP_Insert", "KP_End", "KP_Down", 
                            "KP_Next", "KP_Left", "KP_Begin", "KP_Right", "KP_Home", "KP_Up", "KP_Page_Up", 
                            "KP_Delete", "KP_Add", "KP_Subtract", "KP_Multiply", "KP_Divide", "KP_Enter"]:
                if modify:
                    cmds.append("type(\"%s\", %s)" % (char, modify))
                else:
                    cmds.append("type(\"%s\")" % char)
            else:
                sikulixkey = "Key." + sikulixkeys[char]
                if modify:
                    cmds.append("type(%s, %s)" % (sikulixkey, modify))
                else:
                    cmds.append("type(%s)" % sikulixkey)
            time_of_last_command = time
            previous_char = previous_event = sp
    elif press == "Press":
        key_is_modifier = _set_modifiers(char, True)
        if (char == "Shift_L" and not modifiers["left control down"]) or (char == "Control_L" and not modifiers["left shift down"]):
            current_cmds_length = len(cmds)
            previous_char = sp
            key_pressed_while_holding_ctrl_or_shift = False
    mouse_moved = False        
                        
def clean_up():
    # We have something other than motion (a mouse button event), so we need to handle the motion.
    _handle_motions()

if __name__ == "__main__":

    # TODO: Create a for loop to handle events from a file for unit testing.
    filename = "/tmp/eventrecord.txt"
    myeventlist = [] 
    with open(filename[:-3] + "json", "r") as file:
        myeventlist = json.load(file)

    code, mouse_movements = convert(myeventlist)
    f = open("/tmp/test.sikuli/test.py", "w", encoding="utf-8")
    for r in code:
        f.write(r + "\n")
    f.close()