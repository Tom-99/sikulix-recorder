#!/usr/env python
#
# Records mouse and keyboards events and converts the result
# to a Sikulix script.
#
# Written by Tom Hunter
# Copyright May 16th, 2024

# Licence GPL3
# Install pynput for global events
# python -m pip install pynput 

from pynput import keyboard, mouse
import time

myeventlist = []
continue_listening = True
first_time = True
simple_way_to_exit = True
escape_cnt = 0
keyboard_listener = None
x = 0
y = 0

# External handlers
first_time_handler = None
keyboard_handler = None
motion_handler = None
mouse_button_handler = None

# callback for key presses, the listener will pass us a key object that
# indicates what key is being pressed
def on_key_press(key):
    # print("Key pressed: ", key, hasattr(key, "char")goedemorgen)
    # so this is a bit of a quirk with pynput,
    # if an alpha-numeric key is pressed the key object will have an attribute
    # char which contains a string with the character, but it will only have
    # this attribute with alpha-numeric, so if a special key is pressed
    # this attribute will not be in the object.
    # so, we end up having to check if the attribute exists with the hasattr
    # function in python, and then check the character
    # here is that in action:
    global myeventlist
    global first_time
    global keyboard_listener

    t = int(time.time() * 1000)  # in milisecs
    if first_time_handler and first_time:
        first_time_handler(t)
        first_time = False
    
    if key in [keyboard.Key.enter, keyboard.Key.esc, keyboard.Key.tab, keyboard.Key.backspace, keyboard.Key.delete, keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.f3, keyboard.Key.f4, keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8, keyboard.Key.f9, keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12, keyboard.Key.f13, keyboard.Key.f14, keyboard.Key.f15, keyboard.Key.insert, keyboard.Key.space, keyboard.Key.home, keyboard.Key.end, keyboard.Key.left, keyboard.Key.right, keyboard.Key.down, keyboard.Key.up, keyboard.Key.page_down, keyboard.Key.page_up, keyboard.Key.print_screen, keyboard.Key.pause, keyboard.Key.caps_lock, keyboard.Key.scroll_lock, keyboard.Key.num_lock]:
        key = str(key)[4:]
    elif key == keyboard.Key.ctrl:
        key = "Control_L"
    elif key == keyboard.Key.shift:
        key = "Shift_L"
    elif key == keyboard.Key.alt: 
        key = "Alt_L"
    elif key == keyboard.Key.cmd: 
        key = "Super_L"
    elif key == keyboard.Key.ctrl_r: 
        key = "Control_R"
    elif key == keyboard.Key.shift_r: 
        key = "Shift_R"
    elif key == keyboard.Key.alt_r: 
        key = "Alt_R"
    elif key == keyboard.Key.cmd_r: 
        key = "Super_R"
    elif key == keyboard.Key.menu: 
        key = "Menu"          
    else:
        # Scan code to name of key.
        key = str(keyboard_listener.canonical(key)).strip("'")
    # if isinstance(key, keyboard.Key):
    #     print('Key:', key.name, key.value.vk, key.value)
    #     name = key.name
    # elif isinstance(key, keyboard.KeyCode):
    #     print('KeyCode:', key.char, key.vk)
    #     name = key.char51230.
    # if hasattr(key, "char"):
    #     myeventlist.append("%d\tKey\t%s\t%s\t%d\t%d"%(t, "Press", key.char, x, y))
    #     if keyboard_handler:
    #         keyboard_handler(t, "Press", key.char, x, y)
    # else:H
    myeventlist.append("%d\tKey\t%s\t%s\t%d\t%d"%(t, "Press", str(key), x, y))
    if keyboard_handler:
        keyboard_handler(t, "Press", str(key), x, y)

# same as the key press callback, but for releasing keys
def on_key_release(key):
    global myeventlist
    global first_time
    global escape_cnt   
    global continue_listening
    global simple_way_to_exit
    if key in [keyboard.Key.enter, keyboard.Key.esc, keyboard.Key.tab, keyboard.Key.backspace, keyboard.Key.delete, keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.f3, keyboard.Key.f4, keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8, keyboard.Key.f9, keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12, keyboard.Key.f13, keyboard.Key.f14, keyboard.Key.f15, keyboard.Key.insert, keyboard.Key.space, keyboard.Key.home, keyboard.Key.end, keyboard.Key.left, keyboard.Key.right, keyboard.Key.down, keyboard.Key.up, keyboard.Key.page_down, keyboard.Key.page_up, keyboard.Key.print_screen, keyboard.Key.pause, keyboard.Key.caps_lock, keyboard.Key.scroll_lock, keyboard.Key.num_lock]:
        key = str(key)[4:]
    elif key == keyboard.Key.ctrl:
        key = "Control_L"
    elif key == keyboard.Key.shift:
        key = "Shift_L"
    elif key == keyboard.Key.alt: 
        key = "Alt_L"
    elif key == keyboard.Key.cmd: 
        key = "Super_L"
    elif key == keyboard.Key.ctrl_r: 
        key = "Control_R"
    elif key == keyboard.Key.shift_r: 
        key = "Shift_R"
    elif key == keyboard.Key.alt_r: 
        key = "Alt_R"
    elif key == keyboard.Key.cmd_r: 
        key = "Super_R"
    elif key == keyboard.Key.menu: 
        key = "Menu"      
    else:
        # Scan code to name of key.
        key = str(keyboard_listener.canonical(key)).strip("'")

    t = int(time.time() * 1000)  # in milisecs
    # if hasattr(key, "char"):
    #     myeventlist.append("%d\tKey\t%s\t%s\t%d\t%d"%(t, "Release", key.char, x, y))
    #     if keyboard_handler:
    #         keyboard_handler(t, "Release", key.char, x, y)
    # else:
    myeventlist.append("%d\tKey\t%s\t%s\t%d\t%d"%(t, "Release", str(key), x, y))
    if keyboard_handler:
        keyboard_handler(t, "Release", str(key), x, y)

    if simple_way_to_exit:
        # Press Escape to quit
        if key == "esc":
            print("Exiting.")
            continue_listening = False
            return False
    else:
        if key == "esc":
            escape_cnt += 1
        else:
            escape_cnt = 0
        if escape_cnt > 2:
            print("Exiting.")
            continue_listening = False
            return False

# the mouse click callback will give you the button pressed and its status, the
# callback will be triggered once when the button is pushed and again when released
# the is_pressed will tell you which state it's in
# there are several types of buttons it can recognize, but for the most part
# you'll just need the main 3: left, right and middle
def on_mouse_click(mouse_position_x, mouse_position_y, button, is_pressed):
    global myeventlist
    global first_time
    global x
    global y
    x, y = mouse_position_x, mouse_position_y
    buttons = {"Button.left":1, "Button.middle":2, "Button.right":3, "Button.x1":8, "Button.x2":9} # TODO check on Linux.
    b = str(button).split(":")[0]
    if not b in buttons.keys():
        print("Button '%s' not (yet) implemented." % button)
        return

    t = int(time.time() * 1000)  # in milisecs
    if first_time_handler and first_time:
        first_time_handler(t)
        first_time = False

    buttonno = buttons[b]
    if is_pressed:
        myeventlist.append("%d\tButton\tPress\t%s\t%d\t%d"%(t, str(buttonno), mouse_position_x, mouse_position_y))
        if mouse_button_handler:
            mouse_button_handler(t, "Press", buttonno, mouse_position_x, mouse_position_y)
    else:
        myeventlist.append("%d\tButton\tRelease\t%s\t%d\t%d"%(t, str(buttonno), mouse_position_x, mouse_position_y))
        if mouse_button_handler:
            mouse_button_handler(t, "Release", buttonno, mouse_position_x, mouse_position_y)

def on_mouse_move(mouse_position_x, mouse_position_y):
    global myeventlist
    global first_time
    global x
    global y
    x, y = mouse_position_x, mouse_position_y  

    t = int(time.time() * 1000)  # in milisecs
    if first_time_handler and first_time:
        first_time_handler(t)
        first_time = False

    # Watch out the mouse_positions can be negative. It seems that the mouse cursor will overshoot a bit.
    myeventlist.append("%d\tMotion\t%d\t%d"%(t, mouse_position_x, mouse_position_y))
    if motion_handler:
        motion_handler(t, mouse_position_x, mouse_position_y)

# So the mouse scroll callback will give you 2 sets of scroll changes, one for the x
# axis and one for the y. Most of the time the one you care about is the y axis change
def on_mouse_scroll(mouse_position_x, mouse_position_y, scroll_x_change, scroll_y_change):
    """ Handler for scroll events of the mouse. """
    global myeventlist
    global first_time
    global x
    global y
    x, y = mouse_position_x, mouse_position_y    

    t = int(time.time() * 1000)  # in milisecs
    if first_time_handler and first_time:
        first_time_handler(t)
        first_time = False

    # if scroll_x_change < 0:
    #     print("user is scrolling to the left")
    # elif scroll_x_change > 0:
    #     print("user is scrolling to the right")
    # if scroll_y_change > 0:
    #     print("user is scrolling up the page")
    # elif scroll_y_change < 0:
    #     print("user is scrolling down the page")
    # print("scroll change deltas: ", scroll_x_change, scroll_y_change)
    
    # Linux handles scroll events as clicks of mouse button 4 (UP) and 5 (DOWN).
    # TODO consider handling left and right scrolling.
    if scroll_y_change == 1:
        buttonno=4
    elif scroll_y_change == -1:
        buttonno = 5
    else:
        # Not (yet) handled.
        return
    myeventlist.append("%d\tButton\tPress\t%s\t%d\t%d"%(t, str(buttonno), mouse_position_x, mouse_position_y))
    if mouse_button_handler:
        mouse_button_handler(t, "Press", buttonno, mouse_position_x, mouse_position_y)
    myeventlist.append("%d\tButton\tRelease\t%s\t%d\t%d"%(t, str(buttonno), mouse_position_x, mouse_position_y))
    if mouse_button_handler:
        mouse_button_handler(t, "Release", buttonno, mouse_position_x, mouse_position_y)


def start_up():
    """ Initialise and start the recording of events. """
    # create a listener and setup our call backs
    global keyboard_listener
    global continue_listening
    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_move=on_mouse_move, on_scroll=on_mouse_scroll, on_click=on_mouse_click)

    # start the listener
    keyboard_listener.start()
    mouse_listener.start()
    while continue_listening:
        time.sleep(1)
    keyboard_listener.stop()
    mouse_listener.stop()
    mouse_listener.join()    
    keyboard_listener.join()   


def clean_up():
    # We need this because the main program calls it on Linux when using Xlib
    pass


if __name__ == "__main__":
    import json    

    print("Recording keys and mouse. Press Escape to stop recording.")
    filename = "eventrecord.txt"
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
