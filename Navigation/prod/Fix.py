from datetime import datetime, time, timedelta, timezone
from math import *
import os
from xml.dom.minidom import parse
import xml.dom.minidom

import Angle as Angle

class Fix():
    # Default constructor of Fix Class.    
    # It initializes all the attributes.    
    def __init__(self, logFile="log.txt"):    
        if len(logFile) < 1:
            raise (ValueError("Fix.__init__:  Received Filename is invalid"))
        
        try:
            logger = open(logFile, "a")
            self.logger = logger
            
            dateUTC = datetime.now(tz=timezone.utc)
            dateLocal = dateUTC.astimezone().replace(microsecond=0)
            logger.write("LOG:\t" + dateLocal.isoformat(' ') + ":\tStart of log\n")
            
        except ValueError as raisedException:
            raise (ValueError("Fix.__init__:  Log File could not be created or appended"))


    # setSightingFile method receives parameter sightingFile as string.
    # Sets the received xml file as the sighting file.
    def setSightingFile(self, sightingFile):
        actualFileName = sightingFile.split(".")[0]
        
        if(len(actualFileName)) < 1:
           raise (ValueError("Fix.setSightingFile:  Received Filename is invalid"))
       
        self.sightingFile = actualFileName + ".xml"
        
        dateUTC = datetime.now(tz=timezone.utc)
        dateLocal = dateUTC.astimezone().replace(microsecond=0)
        self.logger.write("LOG:\t" + dateLocal.isoformat(' ') + ":\tStart of sighting file " + self.sightingFile + "\n")
        
        try:
            f = open(self.sightingFile, "r")
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setSightingFile:  Sighting file could not be opened"))
        
        return self.sightingFile
    
    # getSightings file works on the sighting file.
    # processes the sightings information specified in the sightingFile. 
    def getSightings(self):
        approximateLatitude = "0d0.0"			
        approximateLongitude = "0d0.0"
        try:
            DOMTree = xml.dom.minidom.parse(self.sightingFile)  
        except Exception as e:
            raise (ValueError("Fix.getSightings:  Sighting file not found"))
        
        collection = DOMTree.documentElement
        sightings = collection.getElementsByTagName("sighting")
        listSightings = []
        
        try:
            for sighting in sightings:
                try:
                    body = sighting.getElementsByTagName('body')[0].childNodes[0].data.strip()
                except Exception as e:
                    raise (ValueError("Fix.getSightings:  body tag is missing"))
                
                try:
                    dt = sighting.getElementsByTagName('date')[0].childNodes[0].data.strip()
                except Exception as e:
                    raise (ValueError("Fix.getSightings:  date tag is missing"))
                
                try:
                    tm = sighting.getElementsByTagName('time')[0].childNodes[0].data.strip()
                except Exception as e:
                    raise (ValueError("Fix.getSightings:  time tag is missing"))
                
                try:
                    observation = sighting.getElementsByTagName('observation')[0].childNodes[0].data.strip()
                except Exception as e:
                    raise (ValueError("Fix.getSightings:  observation tag is missing"))
                    
                try:
                    height = sighting.getElementsByTagName('height')[0].childNodes[0].data.strip()
                except Exception as e:
                    height = "0"
                    
                try:
                    temperature = float(sighting.getElementsByTagName('temperature')[0].childNodes[0].data.strip())
                except Exception as e:
                    temperature = 72.0
                
                try:
                    pressure = sighting.getElementsByTagName('pressure')[0].childNodes[0].data.strip()
                except Exception as e:
                    pressure = "1010"
                    
                try:
                    horizon = sighting.getElementsByTagName('horizon')[0].childNodes[0].data.strip().lower()
                except Exception as e:
                    horizon = "natural"
                
                angle = Angle.Angle()
                angle.setDegreesAndMinutes(observation)
                
                if angle.degrees < 0 or angle.degrees > 90:
                    raise (ValueError("Fix.getSightings:  Observation-Degrees are invalid"))
                elif angle.minutes < 0 or angle.minutes > 60:
                    raise (ValueError("Fix.getSightings:  Observation-Minutes are invalid"))
                elif height == "":
                    height = 0
                elif temperature == "":
                    temperature = 72
                elif pressure == "":
                    pressure = 1010
                elif horizon == "":
                    horizon = "natural"

                dip = 0.0
                if horizon == "natural":
                    dip = (-0.97 * sqrt(float(height.strip()))) / 60.0

                celcius = (temperature - 32) * 5.0 / 9.0
                angle.setDegreesAndMinutes(observation)
                altitude = angle.degrees + (angle.minutes / 60) % 360

                part1 = -0.00452 * float(pressure)
                part2 = float(273 + celcius)
                part3 = tan(radians(altitude))
                refraction = part1 / part2 / part3

                adjustedAltitude = altitude + dip + refraction
                angle.setDegrees(adjustedAltitude)

                listSightings.append({
                    "body": body,
                    "datetime": datetime.strptime(dt + " " + tm, "%Y-%m-%d %H:%M:%S"),
                    "dt": dt,
                    "tm": tm,
                    "observation": observation,
                    "height": height,
                    "temperature": temperature,
                    "pressure": pressure,
                    "horizon": horizon,
                    "altitude": angle.getString()
                })

            listSightings = sorted(listSightings, key=lambda k: k['body'])
            listSightings = sorted(listSightings, key=lambda k: k['datetime'])
            
            for sighting in listSightings:
                dateUTC = datetime.now(tz=timezone.utc)
                dateLocal = dateUTC.astimezone().replace(microsecond=0)
                self.logger.write("LOG:\t" + dateLocal.isoformat(' ') + ":\t" + sighting['body'] + "\t" + sighting['dt'] + "\t" + sighting['tm'] + "\t" + sighting['altitude'] + "\n")

            dateUTC = datetime.now(tz=timezone.utc)
            dateLocal = dateUTC.astimezone().replace(microsecond=0)
            self.logger.write("LOG:\t" + dateLocal.isoformat(' ') + ":\tEnd of sighting file " + self.sightingFile + "\n")
            self.logger.close()
            return (approximateLatitude, approximateLongitude)
        except Exception as e:
            raise (ValueError("Fix.getSightings:  Error reading sighting file"))
        

if __name__ == "__main__":
    print("start")
    f = Fix()
    f.setSightingFile("sight.xml")
    f.getSightings()
    print("finish")
