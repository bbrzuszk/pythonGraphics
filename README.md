# Python Graphics 

## Summary 
This library give students the abilty to create basic shapes, widgets, and animations through an easy to use graphic library.  The general documentation for this library can be found in the this repository or at http://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf.  Use the documentation to navigate the different classes and functions with those classes to produce graphics of any kind.  Check here for recent additions to the library and explaination for the implementation of those additions.  


## How To Use
Place the graphics.py file in the same directory as your current project that is using the library.  To use the classes of the library, best practice is to import it into your current project by typing from graphics import * as the first line of code in your python file. This will give you access to the graphics module in your current python file and any file the imports from that file.

## Update: Basic Collision Detection Added
Static methods for collision detection have been added to class Rectangle and class Circle.  Check the Wiki for more specific information on how to use them.

## Update: Transform Images 2/4/2019
Class Image now gives you the ability to scale and rotate through a [transform method](https://github.com/bbrzuszk/pythonGraphics/wiki/5.-Image-Objects-and-Methods) images if and only if the Pillow modulue is installed on your machine.  If not you can still use the Image class as you did before

## Update: Class RotatablePolygon 2/4/2019
Class [RotatablePolygon](https://github.com/bbrzuszk/pythonGraphics/wiki/3.8.1-Rotatable-Polygon-Object) give you the ability to a polygon object that is able to rotate a specific number of degrees about the polygons centroid.

## Update: GraphWin method getCurrentMouseLocation() added 4/4/2018
Method [getCurrentMouseLocation()](https://github.com/bbrzuszk/pythonGraphics/wiki/2-GraphWin-Object#keyboard-and-mouse-controls) will return a point for the location of the mouse cursor in the window at any given time.


## Update: Class RoundedRectangle 3/10/2018
Class RoundedRectangle give you the ability to create a rectangle object with rounded corners.  Class RoundedRectangle inherits from Rectangle. RoundedRectangle requires 2 parameters, each a point of opposite corners just as in a Rectangle.  The optional 3rd parameter would be the radius of the curve.  This value is defaulted to 25 but may be increased for larger rounded corners or decreased for smaller corners.
### Additional Update to all 2D shapes
You now have access to another method, setActiveFill(color:str)  This method will allow you to define a color to fill the shape with when the mouse cursor is hovering above it.  


## Update: Class Arc 3/7/2017
Class Arc gives you the ability to create 3 different types of arc object.  Class Arc inherits from _ _BBox_ which in turn creates a section of an oval.  Class Arc requires 4 parameters with an option for a 5th.  Arc(Point p1, Point p2, integer startingAngle, integer angleOfRotation, [ String style ])  Angle measures are in degrees. Positive rotations are counter clockwise, negative rotations are clockwise.  Optional 5th parameter can take the values of: "Sector", "Arc", or "Chord" 
