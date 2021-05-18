# graphics.py
"""Simple object oriented graphics library
The library is designed to make it very easy for novice programmers to
experiment with computer graphics in an object oriented fashion. It is
written by John Zelle for use with the book "Python Programming: An
Introduction to Computer Science" (Franklin, Beedle & Associates).
LICENSE: This is open-source software released under the terms of the
GPL (http://www.gnu.org/licenses/gpl.html).
PLATFORMS: The package is a wrapper around Tkinter and should run on
any platform where Tkinter is available.
INSTALLATION: Put this file somewhere where Python can see it.
OVERVIEW: There are two kinds of objects in the library. The GraphWin
class implements a window where drawing can be done and various
GraphicsObjects are provided that can be drawn into a GraphWin. As a
simple example, here is a complete program to draw a circle of radius
10 centered in a 100x100 window:
--------------------------------------------------------------------
from graphics import *
def main():
    win = GraphWin("My Circle", 100, 100)
    c = Circle(Point(50,50), 10)
    c.draw(win)
    win.getMouse() # Pause to view result
    win.close()    # Close window when done
main()
--------------------------------------------------------------------
GraphWin objects support coordinate transformation through the
setCoords method and mouse and keyboard interaction methods.
The library provides the following graphical objects:
    Point
    Line
    Circle
    Oval
    Rectangle
    Polygon
    Text
    Entry (for text-based input)
    Image
Various attributes of graphical objects can be set such as
outline-color, fill-color and line-width. Graphical objects also
support moving and hiding for animation effects.
The library also provides a very simple class for pixel-based image
manipulation, Pixmap. A pixmap can be loaded from a file and displayed
using an Image object. Both getPixel and setPixel methods are provided
for manipulating the image.
DOCUMENTATION: For complete documentation, see Chapter 4 of "Python
Programming: An Introduction to Computer Science" by John Zelle,
published by Franklin, Beedle & Associates.  Also see
http://mcsp.wartburg.edu/zelle/python for a quick reference"""

__version__ = "5.0"

# Version 5 8/26/2016
#     * update at bottom to fix MacOS issue causing askopenfile() to hang
#     * update takes an optional parameter specifying update rate
#     * Entry objects get focus when drawn
#     * __repr_ for all objects
#     * fixed offset problem in window, made canvas borderless

# Version 4.3 4/25/2014
#     * Fixed Image getPixel to work with Python 3.4, TK 8.6 (tuple type handling)
#     * Added interactive keyboard input (getKey and checkKey) to GraphWin
#     * Modified setCoords to cause redraw of current objects, thus
#       changing the view. This supports scrolling around via setCoords.
#
# Version 4.2 5/26/2011
#     * Modified Image to allow multiple undraws like other GraphicsObjects
# Version 4.1 12/29/2009
#     * Merged Pixmap and Image class. Old Pixmap removed, use Image.
# Version 4.0.1 10/08/2009
#     * Modified the autoflush on GraphWin to default to True
#     * Autoflush check on close, setBackground
#     * Fixed getMouse to flush pending clicks at entry
# Version 4.0 08/2009
#     * Reverted to non-threaded version. The advantages (robustness,
#         efficiency, ability to use with other Tk code, etc.) outweigh
#         the disadvantage that interactive use with IDLE is slightly more
#         cumbersome.
#     * Modified to run in either Python 2.x or 3.x (same file).
#     * Added Image.getPixmap()
#     * Added update() -- stand alone function to cause any pending
#           graphics changes to display.
#
# Version 3.4 10/16/07
#     Fixed GraphicsError to avoid "exploded" error messages.
# Version 3.3 8/8/06
#     Added checkMouse method to GraphWin
# Version 3.2.3
#     Fixed error in Polygon init spotted by Andrew Harrington
#     Fixed improper threading in Image constructor
# Version 3.2.2 5/30/05
#     Cleaned up handling of exceptions in Tk thread. The graphics package
#     now raises an exception if attempt is made to communicate with
#     a dead Tk thread.
# Version 3.2.1 5/22/05
#     Added shutdown function for tk thread to eliminate race-condition
#        error "chatter" when main thread terminates
#     Renamed various private globals with _
# Version 3.2 5/4/05
#     Added Pixmap object for simple image manipulation.
# Version 3.1 4/13/05
#     Improved the Tk thread communication so that most Tk calls
#        do not have to wait for synchonization with the Tk thread.
#        (see _tkCall and _tkExec)
# Version 3.0 12/30/04
#     Implemented Tk event loop in separate thread. Should now work
#        interactively with IDLE. Undocumented autoflush feature is
#        no longer necessary. Its default is now False (off). It may
#        be removed in a future version.
#     Better handling of errors regarding operations on windows that
#       have been closed.
#     Addition of an isClosed method to GraphWindow class.

# Version 2.2 8/26/04
#     Fixed cloning bug reported by Joseph Oldham.
#     Now implements deep copy of config info.
# Version 2.1 1/15/04
#     Added autoflush option to GraphWin. When True (default) updates on
#        the window are done after each action. This makes some graphics
#        intensive programs sluggish. Turning off autoflush causes updates
#        to happen during idle periods or when flush is called.
# Version 2.0
#     Updated Documentation
#     Made Polygon accept a list of Points in constructor
#     Made all drawing functions call TK update for easier animations
#          and to make the overall package work better with
#          Python 2.3 and IDLE 1.0 under Windows (still some issues).
#     Removed vestigial turtle graphics.
#     Added ability to configure font for Entry objects (analogous to Text)
#     Added setTextColor for Text as an alias of setFill
#     Changed to class-style exceptions
#     Fixed cloning of Text objects

# Version 1.6
#     Fixed Entry so StringVar uses _root as master, solves weird
#            interaction with shell in Idle
#     Fixed bug in setCoords. X and Y coordinates can increase in
#           "non-intuitive" direction.
#     Tweaked wm_protocol so window is not resizable and kill box closes.

# Version 1.5
#     Fixed bug in Entry. Can now define entry before creating a
#     GraphWin. All GraphWins are now toplevel windows and share
#     a fixed root (called _root).

# Version 1.4
#     Fixed Garbage collection of Tkinter images bug.
#     Added ability to set text atttributes.
#     Added Entry boxes.

import time, os, sys, math

try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
except:
    import Tkinter as tk

# DJC: Added 01.30.19.14.03
# Attempts to load Pillow library and saves boolean for testing in Image class."""
try:
    import importlib

    importlib.__import__("PIL")
    from PIL import Image as PILIMage, ImageTk as PILImageTK

    importedPillow = True
except ImportError:
    importedPillow = False


# DJC: end

##########################################################################
# Module Exceptions

class GraphicsError(Exception):
    """Generic error class for graphics module exceptions."""
    pass


OBJ_ALREADY_DRAWN = "Object currently drawn"
UNSUPPORTED_METHOD = "Object doesn't support operation"
BAD_OPTION = "Illegal option value"

##########################################################################
# global variables and funtions

_root = tk.Tk()
_root.withdraw()

_update_lasttime = time.time()


def update(rate=None):
    global _update_lasttime
    if rate:
        now = time.time()
        pauseLength = 1 / rate - (now - _update_lasttime)
        if pauseLength > 0:
            time.sleep(pauseLength)
            _update_lasttime = now + pauseLength
        else:
            _update_lasttime = now

    _root.update()


############################################################################
# Graphics classes start here

class GraphWin(tk.Canvas):
    """A GraphWin is a toplevel window for displaying graphics."""

    def __init__(self, title="Graphics Window",
                 width=200, height=200, autoflush=True):
        assert type(title) == type(""), "Title must be a string"
        master = tk.Toplevel(_root)
        master.protocol("WM_DELETE_WINDOW", self.close)
        tk.Canvas.__init__(self, master, width=width, height=height,
                           highlightthickness=0, bd=0)
        self.master.title(title)
        self.pack()
        master.resizable(0, 0)
        self.foreground = "black"
        self.items = []
        self.mousePressed = False  # DJC: Added 03.09.21.14.49
        self.mouseRtPressed = False  # DJC: Added 03.09.21.14.49
        self.mouseX = None
        self.mouseY = None
        self.mouseXright = None  # SN: Added 04.05.20.22.17
        self.mouseYright = None  # SN: Added 04.05.20.22.17
        self.keys = set()  # DJC: Added 03.05.18.11.33
        self.currentMouseX = 0  # DJC: Added 04.04.18.12.03
        self.currentMouseY = 0  # DJC: Added 04.04.18.12.03
        self.bind("<Button-1>", self._onClick)
        self.bind("<ButtonRelease-1>", self._releaseClick)  # DJC: Added 03.09.21.14.49
        self.bind("<Button-3>", self._onRtClick)  # SN: Added 04.05.20.22.17
        self.bind("<ButtonRelease-3>", self._releaseRtClick)  # DJC: Added 03.09.21.14.49
        #        self.bind_all("<Key>", self._onKey)
        self.bind_all('<KeyPress>', self.keyPressHandler)  # DJC: Added 03.05.18.11.33
        self.bind_all('<KeyRelease>', self.keyReleaseHandler)  # DJC: Added 03.05.18.11.33
        self.bind_all('<Motion>', self._motion)  # DJC: Added 04.04.18.12.03
        self.height = int(height)
        self.width = int(width)
        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None
        self.closed = False
        master.lift()
        self.lastKey = ""
        if autoflush: _root.update()

    def __repr__(self):
        if self.isClosed():
            return "<Closed GraphWin>"
        else:
            return "GraphWin('{}', {}, {})".format(self.master.title(),
                                                   self.getWidth(),
                                                   self.getHeight())

    def __str__(self):
        return repr(self)

    def __checkOpen(self):
        if self.closed:
            raise GraphicsError("window is closed")

    def _onKey(self, evnt):
        self.lastKey = evnt.keysym

    def setBackground(self, color):
        """Set background color of the window"""
        self.__checkOpen()
        self.config(bg=color)
        self.__autoflush()

    def setCoords(self, x1, y1, x2, y2):
        """Set coordinates of window to run from (x1,y1) in the
        lower-left corner to (x2,y2) in the upper-right corner."""
        self.trans = Transform(self.width, self.height, x1, y1, x2, y2)
        self.redraw()

    def close(self):
        """Close the window"""

        if self.closed: return
        self.closed = True
        self.master.destroy()
        self.__autoflush()

    def isClosed(self):
        return self.closed

    def isOpen(self):
        return not self.closed

    def __autoflush(self):
        if self.autoflush:
            _root.update()

    def plot(self, x, y, color="black"):
        """Set pixel (x,y) to the given color"""
        self.__checkOpen()
        xs, ys = self.toScreen(x, y)
        self.create_line(xs, ys, xs + 1, ys, fill=color)
        self.__autoflush()

    def plotPixel(self, x, y, color="black"):
        """Set pixel raw (independent of window coordinates) pixel
        (x,y) to color"""
        self.__checkOpen()
        self.create_line(x, y, x + 1, y, fill=color)
        self.__autoflush()

    def flush(self):
        """Update drawing to the window"""
        self.__checkOpen()
        self.update_idletasks()

    def getMouse(self):
        """Wait for mouse click and return Point object representing
        the click"""
        self.update()  # flush any prior clicks
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            if self.isClosed(): raise GraphicsError("getMouse in closed window")
            time.sleep(.1)  # give up thread
        x, y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return Point(x, y)

    def getMouseRight(self):  # SN: Added 04.05.20.22.17
        """Wait for a RIGHT mouse click and return Point object representing
        the click"""
        self.update()  # flush any prior clicks
        self.mouseXright = None
        self.mouseYright = None
        while self.mouseXright == None or self.mouseYright == None:
            self.update()
            if self.isClosed(): raise GraphicsError("getMouse in closed window")
            time.sleep(.1)  # give up thread
        x, y = self.toWorld(self.mouseXright, self.mouseYright)
        self.mouseXright = None
        self.mouseYright = None
        return Point(x, y)

    def checkMouse(self):
        """Return last mouse click or None if mouse has
        not been clicked since last call"""
        if self.isClosed():
            raise GraphicsError("checkMouse in closed window")
        self.update()
        if self.mouseX != None and self.mouseY != None:
            x, y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return Point(x, y)
        else:
            return None

    def checkMouseRight(self):  # SN: Added 04.05.20.22.17
        """Return last mouse click or None if mouse has
        not been clicked since last call"""
        if self.isClosed():
            raise GraphicsError("checkMouse in closed window")
        self.update()
        if self.mouseXright != None and self.mouseYright != None:
            x, y = self.toWorld(self.mouseXright, self.mouseYright)
            self.mouseXright = None
            self.mouseYright = None
            return Point(x, y)
        else:
            return None

    def getKey(self):
        """Wait for user to press a key and return it as a string."""
        self.lastKey = ""
        while self.lastKey == "":
            self.update()
            if self.isClosed(): raise GraphicsError("getKey in closed window")
            time.sleep(.1)  # give up thread

        key = self.lastKey
        self.lastKey = ""
        return key

    def checkKey(self):
        """Return last key pressed or None if no key pressed since last call"""
        if self.isClosed():
            raise GraphicsError("checkKey in closed window")
        self.update()
        # key = self.lastKey
        # self.lastKey = ""
        # return key
        return self.lastKey

    def getHeight(self):
        """Return the height of the window"""
        return self.height

    def getWidth(self):
        """Return the width of the window"""
        return self.width

    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x, y)
        else:
            return x, y

    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.world(x, y)
        else:
            return x, y

    def setMouseHandler(self, func):
        self._mouseCallback = func

    def _onClick(self, e):
        self.mousePressed = True  # DJC: Added 03.09.21.14.49
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def _onRtClick(self, e):  # SN: Added 04.05.20.22.17
        self.mouseRtPressed = True  # DJC: Added 03.09.21.14.49
        self.mouseXright = e.x
        self.mouseYright = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def _releaseClick(self, e):  # DJC: Added 03.09.21.14.49
        self.mousePressed = False

    def _releaseRtClick(self, e):  # DJC: Added 03.09.21.14.49
        self.mouseRtPressed = False

    def addItem(self, item):
        self.items.append(item)

    def delItem(self, item):
        self.items.remove(item)

    def redraw(self):
        for item in self.items[:]:
            item.undraw()
            item.draw(self)
        self.update()

    # DJC: 03.05.18.11.37
    def keyPressHandler(self, e):
        self.keys.add(e.keysym)
        self._onKey(e)  # BB 3/2018 fixes getKey and checkKey bug

    def keyReleaseHandler(self, e):
        self.keys.remove(e.keysym)
        self.lastKey = ""

    def checkKeys(self):
        # DJC 06.01.18.07.17
        # Eliminated because you want control of window.update() in main loop
        # self.update() # BB 3/2018 Added to Fix neccessary update in loop
        return self.keys

    # DJC: end

    # DJC: Added 04.04.18.12.03
    def _motion(self, event):
        self.currentMouseX, self.currentMouseY = event.x, event.y

    def getCurrentMouseLocation(self):
        return Point(self.currentMouseX, self.currentMouseY)
    # DJC: end    
    
    # NIS: Added 05.17.21.23.44
    def setWindowIcon(self, path):
        try:
            icon = tk.PhotoImage(file=path)
            self.master.iconphoto(False, icon)
        except Exception as e:
            print(e)
    # NIS: end


class Transform:
    """Internal class for 2-D coordinate transformations"""

    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        # w, h are width and height of window
        # (xlow,ylow) coordinates of lower-left [raw (0,h-1)]
        # (xhigh,yhigh) coordinates of upper-right [raw (w-1,0)]
        xspan = (xhigh - xlow)
        yspan = (yhigh - ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan / float(w - 1)
        self.yscale = yspan / float(h - 1)

    def screen(self, x, y):
        # Returns x,y in screen (actually window) coordinates
        xs = (x - self.xbase) / self.xscale
        ys = (self.ybase - y) / self.yscale
        return int(xs + 0.5), int(ys + 0.5)

    def world(self, xs, ys):
        # Returns xs,ys in world coordinates
        x = xs * self.xscale + self.xbase
        y = self.ybase - ys * self.yscale
        return x, y


# Default values for various item configuration options. Only a subset of
#   keys may be present in the configuration dictionary for a given item
DEFAULT_CONFIG = {"fill": "",
                  "activefill": "",  # BB added ActiveFill 3/9/2018
                  "outline": "black",
                  "width": "1",
                  "arrow": "none",
                  "text": "",
                  "justify": "center",
                  "font": ("helvetica", 12, "normal"),
                  "smooth": "0"}  # Niss added 1.05.2017


class GraphicsObject:
    """Generic base class for all of the drawable objects"""

    # A subclass of GraphicsObject should override _draw and
    #   and _move methods.

    def __init__(self, options):
        # options is a list of strings indicating which options are
        # legal for this object.

        # When an object is drawn, canvas is set to the GraphWin(canvas)
        #    object where it is drawn and id is the TK identifier of the
        #    drawn shape.
        self.canvas = None
        self.id = None

        # config is the dictionary of configuration options for the widget.
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config

    def setFill(self, color):
        """Set interior color to color"""
        self._reconfig("fill", color)

    def setOutline(self, color):
        """Set outline color to color"""
        self._reconfig("outline", color)

    def setWidth(self, width):
        """Set line weight to width"""
        self._reconfig("width", width)

    def setActiveFill(self, color):  # Added By BB 3/8
        self._reconfig("activefill", color)

    def setSmooth(self, bool):  # Niss: added 1.05.2017
        """Set smooth boolean to bool"""
        self._reconfig("smooth", bool)

    def redraw(self):  # Niss: added 1.05.2017
        """Redraws the object (i.e. hide it and then makes visible again) aReturns silently if the
        object is not currently drawn."""
        if not self.canvas: return
        if not self.canvas.isClosed():
            self.canvas.delete(self.id)
        self.id = self._draw(self.canvas, self.config)

    def draw(self, graphwin):

        """Draw the object in graphwin, which should be a GraphWin
        object.  A GraphicsObject may only be drawn into one
        window. Raises an error if attempt made to draw an object that
        is already visible."""

        if self.canvas and not self.canvas.isClosed(): raise GraphicsError(OBJ_ALREADY_DRAWN)
        if graphwin.isClosed(): raise GraphicsError("Can't draw to closed window")
        self.canvas = graphwin
        self.id = self._draw(graphwin, self.config)
        graphwin.addItem(self)
        if graphwin.autoflush:
            _root.update()
        return self

    def undraw(self):

        """Undraw the object (i.e. hide it). Returns silently if the
        object is not currently drawn."""

        if not self.canvas: return
        if not self.canvas.isClosed():
            self.canvas.delete(self.id)
            self.canvas.delItem(self)
            if self.canvas.autoflush:
                _root.update()
        self.canvas = None
        self.id = None

    def move(self, dx, dy):

        """move object dx units in x direction and dy units in y
        direction"""

        self._move(dx, dy)
        canvas = self.canvas
        if canvas and not canvas.isClosed():
            trans = canvas.trans
            if trans:
                x = dx / trans.xscale
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            self.canvas.move(self.id, x, y)
            if canvas.autoflush:
                _root.update()

    def _reconfig(self, option, setting):
        # Internal method for changing configuration of the object
        # Raises an error if the option does not exist in the config
        #    dictionary for this object
        if option not in self.config:
            raise GraphicsError(UNSUPPORTED_METHOD)
        options = self.config
        options[option] = setting
        if self.canvas and not self.canvas.isClosed():
            self.canvas.itemconfig(self.id, options)
            if self.canvas.autoflush:
                _root.update()

    def _draw(self, canvas, options):
        """draws appropriate figure on canvas with options provided
        Returns Tk id of item drawn"""
        pass  # must override in subclass

    def _move(self, dx, dy):
        """updates internal state of object to move it dx,dy units"""
        pass  # must override in subclass


class Point(GraphicsObject):
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    def _draw(self, canvas, options):
        x, y = canvas.toScreen(self.x, self.y)
        return canvas.create_rectangle(x, y, x + 1, y + 1, options)

    def _move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy

    def clone(self):
        other = Point(self.x, self.y)
        other.config = self.config.copy()
        return other

    def getX(self): return self.x

    def getY(self): return self.y


class _BBox(GraphicsObject):
    # Internal base class for objects represented by bounding box
    # (opposite corners) Line segment is a degenerate case.

    def __init__(self, p1, p2, options=["outline", "width", "fill", "activefill"]):  # BB added activefill
        GraphicsObject.__init__(self, options)
        self.p1 = p1.clone()
        self.p2 = p2.clone()

    def _move(self, dx, dy):
        self.p1.x = self.p1.x + dx
        self.p1.y = self.p1.y + dy
        self.p2.x = self.p2.x + dx
        self.p2.y = self.p2.y + dy

    def getP1(self): return self.p1.clone()

    def getP2(self): return self.p2.clone()

    def getCenter(self):
        p1 = self.p1
        p2 = self.p2
        return Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)


class Rectangle(_BBox):
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Rectangle({}, {})".format(str(self.p1), str(self.p2))

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_rectangle(x1, y1, x2, y2, options)

    def clone(self):
        other = Rectangle(self.p1, self.p2)
        other.config = self.config.copy()
        return other
    
    @staticmethod   # DJC: Added 04.20.21.14.51
    def testCollision_RectVsRect(rect1, rect2):
        """Returns True if the two Rectangles are colliding, False if not."""
        return rect1.p1.x <= rect2.p2.x and rect1.p2.x >= rect2.p1.x and \
               rect1.p1.y <= rect2.p2.y and rect1.p2.y >= rect2.p1.y

    @staticmethod   # DJC: Added 04.20.21.14.51
    def testCollision_RectVsPoint(rect, point):
        """Returns True if the Point is colliding with the Rectangle, False if not."""
        return point.x >= rect.p1.x and point.x <= rect.p2.x and \
               point.y >= rect.p1.y and point.y <= rect.p2.y

    def testCollision_RectangleVsCircle(rectangle, circle):
        """Returns True if the circle is colliding with the rectangle. False if not."""
        xClamp = max(rectangle.p1.x, min(rectangle.p2.x, circle.getCenter().x))
        yClamp = max(rectangle.p1.y, min(rectangle.p2.y, circle.getCenter().y))
        if math.sqrt((xClamp - circle.getCenter().x)**2 + (yClamp - circle.getCenter().y)**2) <= circle.radius:
            return True
        else:
            return False


class RoundedRectangle(Rectangle):  # BB added 3/9/2018
    """Creates a rectangle with rounded corners of a given radius"""

    def __init__(self, p1, p2, radius=25):
        super(RoundedRectangle, self).__init__(p1, p2)
        x1 = p1.x
        x2 = p2.x
        y1 = p1.y
        y2 = p2.y
        self.radius = radius
        # self.points is a list of points that contain rounded corners
        self.points = [x1 + radius, y1,
                       x1 + radius, y1,  # segment between x1+radius, y1 and x2-radius , y1 is not rounded
                       x2 - radius, y1,
                       x2 - radius, y1,
                       x2, y1,  # defines the corner that we create a curve out too between adjacent points
                       x2, y1 + radius,
                       x2, y1 + radius,
                       x2, y2 - radius,
                       x2, y2 - radius,
                       x2, y2,
                       x2 - radius, y2,
                       x2 - radius, y2,
                       x1 + radius, y2,
                       x1 + radius, y2,
                       x1, y2,
                       x1, y2 - radius,
                       x1, y2 - radius,
                       x1, y1 + radius,
                       x1, y1 + radius,
                       x1, y1]

    def __repr__(self):
        return "Rounded Rectangle({}, {}, {})".format(str(self.p1), str(self.p2), str(self.radius))

    def clone(self):
        other = RoundedRectangle(self.p1, self.p2, self.radius)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        return canvas.create_polygon(self.points, options, smooth=True)


class Oval(_BBox):
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Oval({}, {})".format(str(self.p1), str(self.p2))

    def clone(self):
        other = Oval(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_oval(x1, y1, x2, y2, options)


class Arc(_BBox):
    """Creates an arc, sector, or chord given opposite corners of a bounding box
    a starting angle, and a rotation in degrees"""

    def __init__(self, p1, p2, startAngle, rotation, style="SECTOR"):
        _BBox.__init__(self, p1, p2)
        self.startAngle = startAngle
        self.rotation = rotation
        self.styleAsString = style.upper()
        if (self.styleAsString == "SECTOR"):
            self.style = tk.PIESLICE
        elif (self.styleAsString == "CHORD"):
            self.style = tk.CHORD
        else:
            self.style = tk.ARC

    def __repr__(self):
        return "Arc({},{},{},{})".format(str(self.p1), str(self.p2), str(self.startAngle), str(self.rotation))

    def clone(self):
        other = Arc(self.p1, self.p2, self.startAngle, self.rotation, self.styleAsString)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_arc(x1, y1, x2, y2, options, style=self.style, start=self.startAngle, extent=self.rotation)


class Circle(Oval):
    def __init__(self, center, radius):
        p1 = Point(center.x - radius, center.y - radius)
        p2 = Point(center.x + radius, center.y + radius)
        Oval.__init__(self, p1, p2)
        self.radius = radius

    def __repr__(self):
        return "Circle({}, {})".format(str(self.getCenter()), str(self.radius))

    def clone(self):
        other = Circle(self.getCenter(), self.radius)
        other.config = self.config.copy()
        return other

    def getRadius(self):
        return self.radius
    
    def setCenter(self, point): # DJC: Added 04.21.21.18.51
        self._move(point.x - self.getCenter().x, point.y - self.getCenter().y)
        
    @staticmethod   # DJC: Added 04.20.21.14.51
    def testCollision_CircleVsCircle(circle1, circle2):
        """Returns True if the two Circles are colliding, False if not."""
        c1 = circle1.getCenter()
        c2 = circle2.getCenter()
        distanceSquared = (c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2
        return distanceSquared <= (circle1.radius + circle2.radius) ** 2

    @staticmethod   # DJC: Added 04.20.21.14.51
    def testCollision_CircleVsPoint(circle, point):
        """Returns True if the Point is colliding with the Circle, False if not."""
        distanceSquared = (point.x - circle.getCenter().x) ** 2 + (point.y - circle.getCenter().y) ** 2
        return distanceSquared <= circle.radius ** 2

    def testCollision_CircleVsRectangle(circle, rectangle):
        """Returns True if the circle is colliding with the rectangle. False if not."""
        xClamp = max(rectangle.p1.x, min(rectangle.p2.x, circle.getCenter().x))
        yClamp = max(rectangle.p1.y, min(rectangle.p2.y, circle.getCenter().y))
        if math.sqrt((xClamp - circle.getCenter().x)**2 + (yClamp - circle.getCenter().y)**2) <= circle.radius:
            return True
        else:
            return False


class Line(_BBox):
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2, ["arrow", "fill", "width"])
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill

    def __repr__(self):
        return "Line({}, {})".format(str(self.p1), str(self.p2))

    def clone(self):
        other = Line(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_line(x1, y1, x2, y2, options)

    def setArrow(self, option):
        if not option in ["first", "last", "both", "none"]:
            raise GraphicsError(BAD_OPTION)
        self._reconfig("arrow", option)


class Polygon(GraphicsObject):
    def __init__(self, *points):
        # if points passed as a list, extract it
        if len(points) == 1 and type(points[0]) == type([]):
            points = points[0]
        self.points = list(map(Point.clone, points))
        GraphicsObject.__init__(self,
                                ["outline", "width", "fill", "activefill", "smooth"])  # BB added activefill 3/9/2018
        # Niss added "smooth" 04_05_2017

    def __repr__(self):
        return "Polygon" + str(tuple(p for p in self.points))

    def clone(self):
        other = Polygon(*self.points)
        other.config = self.config.copy()
        return other

    def getPoints(self):
        return list(map(Point.clone, self.points))

    def _move(self, dx, dy):
        for p in self.points:
            p.move(dx, dy)

    def _draw(self, canvas, options):
        args = [canvas]
        for p in self.points:
            x, y = canvas.toScreen(p.x, p.y)
            args.append(x)
            args.append(y)
        args.append(options)
        return GraphWin.create_polygon(*args)


class RotatablePolygon(Polygon):  # Niss: added 1.05.2017
    """Creates an Polygon that can be rotated."""

    def __init__(self, *points):
        # if points passed as a list, extract it
        if len(points) == 1 and type(points[0] == type([])):
            points = points[0]
        points = list(map(Point.clone, points))
        Polygon.__init__(self, points)
        self.theta = 0
        self.orig_points = points  # must recalc each rot w/ original pts or rounding
        # creates degredation of poly shape
        self.center = None
        self.find_centroid()

    def rotate(self, degrees=0, about=None):
        """rotates a Polygon object // DEGREES = how far CCW the object is rotated //
        ABOUT = the center of rotation"""
        if about == None:
            about = self.center
        self.theta = (self.theta + degrees) % 360
        if degrees != 0:
            radians = (self.theta * math.pi) / 180
            for i in range(len(self.orig_points)):
                orig_x_diff = self.orig_points[i].getX() - about.getX()
                orig_y_diff = self.orig_points[i].getY() - about.getY()
                newx = orig_x_diff * math.cos(radians) + orig_y_diff * math.sin(radians)
                newy = orig_y_diff * math.cos(radians) - orig_x_diff * math.sin(radians)
                dx = newx - self.points[i].getX()
                dy = newy - self.points[i].getY()
                self.points[i].move(dx + about.getX(), dy + about.getY())
            self.redraw()
            self.find_centroid()

    def find_centroid(self):
        """calculates the centroid of a polygon"""
        x_sum = 0
        y_sum = 0
        for p in self.points:
            x_sum += p.getX()
            y_sum += p.getY()
        self.center = Point(round(x_sum / len(self.points)), round(y_sum / len(self.points)))
        return self.center

    def _move(self, dx, dy):
        """Overrides Polygon _move() to to add recalculation of centroid point for rotation purposes"""
        Polygon._move(self, dx, dy)
        for p in self.orig_points:
            p.move(dx, dy)
        self.find_centroid()


class RotatableOval(RotatablePolygon):  # Niss: added 1.05.2017
    """Creates an Oval that is actually a smoothed Polygon so it doesn't have an axis
    aligned bounding box.  This allows it to be rotated."""

    def __init__(self, center, x_radius, y_radius):
        self.x_radius = x_radius
        self.y_radius = y_radius
        coords = []
        for i in range(36):
            x = round(center.getX() + self.x_radius * math.cos(i * math.pi / 18))
            y = round(center.getY() + self.y_radius * math.sin(i * math.pi / 18))
            coords.append(Point(x, y))
        RotatablePolygon.__init__(self, coords)
        GraphicsObject.__init__(self, ["outline", "width", "fill", "smooth"])
        self.center = center
        self.about = self.center


class Text(GraphicsObject):
    def __init__(self, p, text):
        GraphicsObject.__init__(self, ["justify", "fill", "text", "font"])
        self.setText(text)
        self.anchor = p.clone()
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill

    def __repr__(self):
        return "Text({}, '{}')".format(self.anchor, self.getText())

    def _draw(self, canvas, options):
        p = self.anchor
        x, y = canvas.toScreen(p.x, p.y)
        return canvas.create_text(x, y, options)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def clone(self):
        other = Text(self.anchor, self.config['text'])
        other.config = self.config.copy()
        return other

    def setText(self, text):
        self._reconfig("text", text)

    def getText(self):
        return self.config["text"]

    def getAnchor(self):
        return self.anchor.clone()

    def setFace(self, face):
        if face in ['helvetica', 'arial', 'courier', 'times roman']:
            f, s, b = self.config['font']
            self._reconfig("font", (face, s, b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            f, s, b = self.config['font']
            self._reconfig("font", (f, size, b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            f, s, b = self.config['font']
            self._reconfig("font", (f, s, style))
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.setFill(color)


class Entry(GraphicsObject):
    def __init__(self, p, width):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        # print self.anchor
        self.width = width
        self.text = tk.StringVar(_root)
        self.text.set("")
        self.fill = "gray"
        self.color = "black"
        self.font = DEFAULT_CONFIG['font']
        self.entry = None

    def __repr__(self):
        return "Entry({}, {})".format(self.anchor, self.width)

    def _draw(self, canvas, options):
        p = self.anchor
        x, y = canvas.toScreen(p.x, p.y)
        frm = tk.Frame(canvas.master)
        self.entry = tk.Entry(frm,
                              width=self.width,
                              textvariable=self.text,
                              bg=self.fill,
                              fg=self.color,
                              font=self.font)
        self.entry.pack()
        # self.setFill(self.fill)
        self.entry.focus_set()
        return canvas.create_window(x, y, window=frm)

    def getText(self):
        return self.text.get()

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        other = Entry(self.anchor, self.width)
        other.config = self.config.copy()
        other.text = tk.StringVar()
        other.text.set(self.text.get())
        other.fill = self.fill
        return other

    def setText(self, t):
        self.text.set(t)

    def setFill(self, color):
        self.fill = color
        if self.entry:
            self.entry.config(bg=color)

    def _setFontComponent(self, which, value):
        font = list(self.font)
        font[which] = value
        self.font = tuple(font)
        if self.entry:
            self.entry.config(font=self.font)

    def setFace(self, face):
        if face in ['helvetica', 'arial', 'courier', 'times roman']:
            self._setFontComponent(0, face)
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            self._setFontComponent(1, size)
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            self._setFontComponent(2, style)
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.color = color
        if self.entry:
            self.entry.config(fg=color)


class Image(GraphicsObject):
    idCount = 0
    imageCache = {}  # tk photoimages go here to avoid GC while drawn

    def __init__(self, p, *pixmap):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        self.imageId = Image.idCount
        self.pilImage = None  # DJC: 01.30.19.14.44 Original PIL Image
        Image.idCount = Image.idCount + 1
        if len(pixmap) == 1:  # file name provided
            # DJC: 01.30.19.14.45 Added PIL Support
            if importedPillow:
                self.pilImage = PILIMage.open(pixmap[0])  # Save original to reference & prevent image degradation
                self.img = PILImageTK.PhotoImage(self.pilImage, master=_root)
            else:
                self.img = tk.PhotoImage(file=pixmap[0], master=_root)
            # DJC: End
        else:  # width and height provided
            width, height = pixmap
            self.img = tk.PhotoImage(master=_root, width=width, height=height)

    def __repr__(self):
        return "Image({}, {}, {})".format(self.anchor, self.getWidth(), self.getHeight())

    def _draw(self, canvas, options):
        p = self.anchor
        x, y = canvas.toScreen(p.x, p.y)
        self.imageCache[self.imageId] = self.img  # save a reference
        return canvas.create_image(x, y, image=self.img)

    def _move(self, dx, dy):
        self.anchor.move(dx, dy)

    def undraw(self):
        try:
            del self.imageCache[self.imageId]  # allow gc of tk photoimage
        except KeyError:
            pass
        GraphicsObject.undraw(self)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        other = Image(Point(0, 0), 0, 0)
        other.img = self.img.copy()
        other.anchor = self.anchor.clone()
        other.config = self.config.copy()
        return other

    def getWidth(self):
        """Returns the width of the image in pixels"""
        return self.img.width()

    def getHeight(self):
        """Returns the height of the image in pixels"""
        return self.img.height()

    def getPixel(self, x, y):
        """Returns a list [r,g,b] with the RGB color values for pixel (x,y)
        r,g,b are in range(256)
        """

        value = self.img.get(x, y)
        if type(value) == type(0):
            return [value, value, value]
        elif type(value) == type((0, 0, 0)):
            return list(value)
        else:
            return list(map(int, value.split()))

    def setPixel(self, x, y, color):
        """Sets pixel (x,y) to the given color
        """
        self.img.put("{" + color + "}", (x, y))

    def save(self, filename):
        """Saves the pixmap image to filename.
        The format for the save image is determined from the filname extension.
        """

        path, name = os.path.split(filename)
        ext = name.split(".")[-1]
        self.img.write(filename, format=ext)

    # DJC: Added 01.30.19.19.49
    def transform(self, scale=1, angle=0):
        """Resizes and/or Rotates the 'original' image according to the scale/angle passed."""
        if importedPillow:
            tempImg = self.pilImage.copy()
            newWidth = int(tempImg.width * scale)
            newHeight = int(tempImg.height * scale)
            tempImg = tempImg.resize((newWidth, newHeight), resample=PILIMage.BILINEAR)
            tempImg = tempImg.rotate(angle, resample=PILIMage.BILINEAR, expand=True)
            self.img = PILImageTK.PhotoImage(tempImg, master=_root)
        else:
            raise Exception("You need to install the Pillow module to resize/rotate images."
                            "\n           For instructions, see: https://pillow.readthedocs.io/en/3.3.x/installation.html")
    # DJC: End
    
    @staticmethod   # DJC: Added 04.20.21.14.51
    def testCollision_ImageVsImage(image1, image2):
        """Returns True if the two Images are colliding, False if not."""
        return image1.anchor.x - image1.getWidth()/2 <= image2.anchor.x + image2.getWidth()/2 and \
               image1.anchor.x + image1.getWidth()/2 >= image2.anchor.x - image2.getWidth()/2 and \
               image1.anchor.y - image1.getHeight()/2 <= image2.anchor.y + image2.getHeight()/2 and \
               image1.anchor.y + image1.getHeight()/2 >= image2.anchor.y - image2.getHeight()/2

    @staticmethod   # DJC: Added 04.20.21.14.51
    def testCollision_ImageVsPoint(image, point):
        """Returns True if the Point is colliding with the Image, False if not."""
        return point.x >= image.anchor.x - image.getWidth()/2 and \
               point.x <= image.anchor.x + image.getWidth()/2 and \
               point.y >= image.anchor.y - image.getHeight()/2 and \
               point.y <= image.anchor.y + image.getHeight()/2


def color_rgb(r, g, b):
    """r,g,b are intensities of red, green, and blue in range(256)
    Returns color specifier string for the resulting color"""
    return "#%02x%02x%02x" % (r, g, b)


def test():
    win = GraphWin()
    win.setCoords(0, 0, 10, 10)
    t = Text(Point(5, 5), "Centered Text")
    t.draw(win)
    p = Polygon(Point(1, 1), Point(5, 3), Point(2, 7))
    p.draw(win)
    e = Entry(Point(5, 6), 10)
    e.draw(win)
    win.getMouse()
    p.setFill("red")
    p.setOutline("blue")
    p.setWidth(2)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(e.getText())
    e.setFill("green")
    e.setText("Spam!")
    e.move(2, 0)
    win.getMouse()
    p.move(2, 3)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(s)
    win.getMouse()
    p.undraw()
    e.undraw()
    t.setStyle("bold")
    win.getMouse()
    t.setStyle("normal")
    win.getMouse()
    t.setStyle("italic")
    win.getMouse()
    t.setStyle("bold italic")
    win.getMouse()
    t.setSize(14)
    win.getMouse()
    t.setFace("arial")
    t.setSize(20)
    win.getMouse()
    win.close()


# MacOS fix 2
# tk.Toplevel(_root).destroy()

# MacOS fix 1
update()

if __name__ == "__main__":
    test()
