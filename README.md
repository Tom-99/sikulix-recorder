# sikulix-recorder
A commandline recorder for Sikulix

## Purpose

Sikulix ([http://sikulix.com/](http://sikulix.com/)) automates anything you see on the screen of your desktop computer running Windows, Mac or some Linux/Unix. It uses image recognition powered by OpenCV to identify GUI components. This is handy in cases when there is no easy access to a GUI's internals or the source code of the application or web page you want to act on.

But you have to code what you want in Sikulix. The coding is easy, but still... I decided to throw some code together to see if I could make a simple recorder that monitors your mouse and keyboard and converts it to code that can be played back by Sikulix. This recorder is still very basic and not very well tested, but I decided to share it in the hope it would be useful to someone. This would justify the time investment I put into this experiment. So let me know if you use it :)

## Installing
This is a command line Python program. So you will need Python ([www.python.org](www.python.org)) and some Python modules.

The modules are:
1. pynput
2. pillow

These can be installed with `python -m pip install <insert name of module here>`

This program should work on Windows, Linux, and possibly MacOS (I don't have access to a Mac, but the pynput module should work if you run it as super user)

## Usage
Open a command line, go to the folder of sikulix-recorder and run:
`python sikulix_recorder.py <name>`

A folder named name.sikulix will be created to store the Sikulix script and any captured images. Play back the script with Sikulix to automatically repeat all keys  pressed and mouse button/movements that were recorded.

To capture an image, move the mouse to the top left corner, and press and hold the left shift button. Then move the mouse to the bottom right corner of the image and release shift. Now left click on the spot you want Silulix to click on (or beside) the image.

To see all available options, enter:
`python sikulix_recorder.py --help`








