import math
import re

class Angle:
    """Angle is an abstraction that represents an amount of rotation 
    from a fixed point.  When used for navigation, angles are expressed 
    in degrees and minutes, where 1 degree = 60 minutes.
    """

    def __init__(self):
        """Creates an instance of Angle."""
        
        self.degrees = 0
        self.minutes = 0.0

    def setDegrees(self, degrees=0):
        """Sets the value of the instance to a specified number of degrees.
        
        Parameters:
            degrees: is the number of degrees (and portions of degrees).  
                It is a numeric value (integer or float).  
                Optional, defaults to zero if missing.
                
        Returns:
            The resulting angle as degrees and portions of degrees as a 
            single floating point number, modulo 360
            
        Exceptions:
            ValueError: when "degrees" violates the parameter specifications
        """

        if not isinstance(degrees, (int, float)):
            raise ValueError("Angle.setDegrees:  Invalid degrees received. Degrees must be integer or float.")
        
        if isinstance(degrees, int):
            self.degrees = int(degrees)
            self.minutes = 0
        else:
            value = float(degrees)
            self.degrees = math.floor(value)
            self.minutes = (value - self.degrees) * 60
            
        return self.getDegrees()

    def setDegreesAndMinutes(self, angleString):
        """Sets the value of the instance based on a string that 
        contains degrees and minutes.
        
        Parameters:
            angleString: is the angle of rotation from a fixed point.  It is a 
                string the represents an angle in degrees and minutes, and has 
                the general form xdy.y where x is the degree-portion of the 
                angle, y.y is the minute portion of the angle, and "d" is the 
                separator.  The degree portion is an integer value.  The minute 
                portion is either a positive integer or a positive floating 
                point value with digit to the right of the decimal point.
            
        Returns:
            The resulting angle as degrees and portions of degrees as a single 
                floating point number, modulo 360

        Exceptions:
            ValueError: when "angleString" violates the parameter specifications
        """
        
        if not isinstance(angleString, str):
            raise ValueError("Angle.setDegreesAndMinutes:  angleString is not a String.")
        elif len(angleString) == 0:
            raise ValueError("Angle.setDegreesAndMinutes:  Blank angleString received.")
        elif "d" not in angleString:
            raise ValueError("Angle.setDegreesAndMinutes:  'd' is missing in angleString.")
        elif angleString.startswith("d"):
            raise ValueError("Angle.setDegreesAndMinutes:  Degrees part is missing in angleString.")
        elif angleString.endswith("d"):
            raise ValueError("Angle.setDegreesAndMinutes:  Minutes part is missing in angleString.")
        
        parts = angleString.split("d")
        if len(parts) != 2:
            raise ValueError("Angle.setDegreesAndMinutes:  More than one 'd' supplied in angleString.")
        elif not re.match('^(\-?\d+)$', parts[0]):
            raise ValueError("Angle.setDegreesAndMinutes:  Invalid Degrees in angleString.")
        elif not re.match('^(\d+(.\d)?)$', parts[1]):
            raise ValueError("Angle.setDegreesAndMinutes:  Invalid Minutes in angleString.")
        
        self.degrees = int(parts[0])
        self.minutes = float(parts[1]) % 60
        
        return self.getDegrees()

    def add(self, angle):
        """Adds the value of the parameterized value from the instance.
        
        Parameters:
            angle: is an instance of Angle whose value is to be added to current
                    instance.    Mandatory.
                    
        Returns:
            The resulting angle as degrees and portions of degrees as a single 
                floating point number, modulo 360
                
        Exceptions:
            ValueError: when "angle" is not a valid instance of Angle
        """
        
        if not isinstance(angle, Angle):
            raise ValueError("Angle.add:  angle is not an instance of Angle.")
        
        self.degrees += self.getDegreesPart(angle)
        self.minutes += self.getMinutesPart(angle)
        
        return self.getDegrees()
        
    def subtract(self, angle):
        """Subtracts the value of the parameterized value from the current 
        instance.
        
        Parameters:
            angle: is an instance of Angle whose value is to be subtracted from 
                the current instance.    Mandatory.
                    
        Returns:
            The resulting angle as degrees and portions of degrees as a single 
                floating point number, modulo 360
                
        Exceptions:
            ValueError: when "angle" is not a valid instance of Angle
        """
        
        if not isinstance(angle, Angle):
            raise ValueError("Angle.subtract:  angle is not an instance of Angle.")
        
        self.degrees -= self.getDegreesPart(angle)
        self.minutes -= self.getMinutesPart(angle)
        
        return self.getDegrees()

    def compare(self, angle):
        """Compares parameterized value to the current instance.
        
        Parameters:
            angle: is an instance of Angle whose value is to be added to current
                instance.    Mandatory.
                
        Returns:
            An integer having the value:
            * -1 if the instance is less than the value passed as a parameter
            * 0 if the instance is equal to the value passed as a parameter
            * 1 if the instance is greater than the value passed as a parameter
            
        Exceptions:
            ValueError: when "angle" is not a valid instance of Angle
        """
        
        if not isinstance(angle, Angle):
            raise ValueError("Angle.compare:  angle is not an instance of Angle.")
        
        currentDeg = self.getDegrees()
        receiveDeg = angle.getDegrees()

        if currentDeg > receiveDeg:
            return 1
        elif currentDeg < receiveDeg:
            return -1
        else:
            return 0

    def getString(self):
        """Returns a string value of the angle.
        
        Returns:
            A string in the form xdy.y, where x is the number of degrees 
            (modulo 360, no leading zeros), "d" is a literal separator, and y.y 
            is the number of minutes (modulo 60, no leading zeros, rounded to 
            one decimal point)
        """

        self.degrees = int(self.degrees)
        return ("{0}d{1}".format(self.degrees % 360, round(self.minutes, 1)))

    def getDegrees(self):
        """Returns the angle as degrees (and portions of degrees).

        Returns:
            A floating point number representing the degrees and minutes modulo 
            360.
        """

        return (self.degrees + (round(self.minutes / 60, 1))) % 360

    def getDegreesPart(self, angle):
        """Returns the Degrees part of the angle.
        
        Parameters:
            angle: is an instance of Angle.    Mandatory.
                    
        Returns:
            The Degrees part of the angle.
                
        Exceptions:
            ValueError: when "angle" is not a valid instance of Angle
        """
        
        if not isinstance(angle, Angle):
            raise ValueError("Angle.getDegreesPart:  angle is not an instance of Angle.")
        
        strAngle = angle.getString()
        parts = strAngle.split("d")
        return int(parts[0])
        
    def getMinutesPart(self, angle):
        """Returns the Minutes part of the angle.
        
        Parameters:
            angle: is an instance of Angle.    Mandatory.
                    
        Returns:
            The Minutes part of the angle.
                
        Exceptions:
            ValueError: when "angle" is not a valid instance of Angle
        """
        
        if not isinstance(angle, Angle):
            raise ValueError("Angle.getMinutesPart:  angle is not an instance of Angle.")
        
        strAngle = angle.getString()
        parts = strAngle.split("d")
        return float(parts[1])
