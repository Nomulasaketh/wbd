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
        self.errString = ""
        self.Angle = Angle.Angle()
        self.newAngle = Angle.Angle()
        self.newAngle2 = Angle.Angle()
        self.err = 0
        if len(logFile) < 1:
            raise (ValueError("Fix.__init__:  Received Filename is invalid"))

        try:
            logger = open(logFile, "a")
            self.logger = logger
            
            dateUTC = datetime.now(tz=timezone.utc)
            dateLocal = dateUTC.astimezone().replace(microsecond=0)

            filePath = os.path.abspath(logFile)
            logger.write("LOG: " + dateLocal.isoformat(' ') + " Log file:\t" + filePath + "\n")
            
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
        filePath = os.path.abspath(sightingFile)
        self.logger.write("LOG: " + dateLocal.isoformat(' ') + " Sighting file:\t" + filePath + " \n")
        try:
            f = open(self.sightingFile, "r")
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setSightingFile:  Sighting file could not be opened"))

        return filePath

    # setAriesFile method receives parameter ariesFile as string.
    # Sets the received text file as the aries file.
    def setAriesFile(self, ariesFile):
        actualFileName = ariesFile.split(".")[0]

        if (len(actualFileName)) < 1:
            raise (ValueError("Fix.setAriesFile:  Received Filename is invalid"))

        dateUTC = datetime.now(tz=timezone.utc)
        dateLocal = dateUTC.astimezone().replace(microsecond=0)
        filePath = os.path.abspath(ariesFile)

        self.logger.write("LOG: " + dateLocal.isoformat(' ') + " Aries file:\t" + filePath + " \n")
        self.ariesFile = actualFileName + ".txt"

        try:
            f = open(self.ariesFile, "r")
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setAriesFile:  Aries file could not be opened"))
        return filePath

    # setStarFile method receives parameter starFile as string.
    # Sets the received text file name as the stars file.
    def setStarFile(self, starFile):
        actualFileName = starFile.split(".")[0]

        if (len(actualFileName)) < 1:
            raise (ValueError("Fix.setStarFile:  Received Filename is invalid"))

        dateUTC = datetime.now(tz=timezone.utc)
        dateLocal = dateUTC.astimezone().replace(microsecond=0)
        filePath = os.path.abspath(starFile)

        self.logger.write("LOG: " + dateLocal.isoformat(' ') + " Star file:\t" + filePath + " \n")
        self.starFile = actualFileName + ".txt"

        try:
            f = open(self.starFile, "r")
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setStarFile:  Stars file could not be opened"))

        return filePath

    # getSightings file works on the sighting file, starsfile and ariesfile.
    # Processes the sightings information specified in the sightingFile.
    # Reads stars file and aries file and takes matching data.
    # Calculates adjusted altitude, latitude and longitude.
    # Writes calculation in log file with current datetime in cronological order to the earliest time.
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
                    self.err += 1
                    self.errString += "Fix.getSightings:  body tag is missing"
                    continue

                try:
                    receivedDate = sighting.getElementsByTagName('date')[0].childNodes[0].data.strip()
                except Exception as e:
                    self.err += 1
                    self.errString += "Fix.getSightings:  date tag is missing"
                    continue

                try:
                    tm = sighting.getElementsByTagName('time')[0].childNodes[0].data.strip()
                except Exception as e:
                    self.err += 1
                    self.errString += "Fix.getSightings:  time tag is missing"
                
                try:
                    observation = sighting.getElementsByTagName('observation')[0].childNodes[0].data.strip()
                except Exception as e:
                    self.err += 1
                    self.errString += "Fix.getSightings:  observation tag is missing"
                    continue

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
                h, m, sec = tm.split(":")

                s = (int(m) * 60) + int(sec)
                convertedDate = datetime.strptime(receivedDate, '%Y-%m-%d').strftime('%m/%d/%y')

                starData = open(self.starFile, "r")
                bodyFlag = False

                for line in starData:

                    name = line.split("\t")[0]
                    tempDt = line.split("\t")[1]
                    if name == body and tempDt == convertedDate:
                        self.SHAstar = self.Angle.setDegreesAndMinutes(line.split("\t")[2])
                        self.latitude = (line.split("\t")[3]).strip()
                        bodyFlag = True
                starData.close()

                try:
                    if (not bodyFlag):
                        self.err += 1
                        self.errString += "Sighting file : Some data not match"
                        continue

                except:
                    self.err += 1

                ariesData = open(self.ariesFile, "r")
                for line in ariesData:
                    tempD = line.split("\t")[0]
                    tempH = line.split("\t")[1]
                    obj = line.split("\t")[2]

                    h = int(h)
                    tempH = int(tempH)
                    if tempD == convertedDate and tempH == h:
                        self.GHAaries1 = self.newAngle.setDegreesAndMinutes(obj)
                        nextObj = next(ariesData).split("\t")[2]
                        self.GHAaries2 = self.newAngle2.setDegreesAndMinutes(nextObj)

                ariesData.close()

                self.GHAaries = self.GHAaries1 + (self.GHAaries2 - self.GHAaries1) * (s / 3600)
                self.GHAobservation = self.GHAaries + self.SHAstar

                self.Angle.setDegrees(self.GHAobservation)
                self.GHAobservation = self.Angle.getString()

                listSightings.append({
                    "body": body,
                    "datetime": datetime.strptime(receivedDate + " " + tm, "%Y-%m-%d %H:%M:%S"),
                    "dt": receivedDate,
                    "tm": tm,
                    "observation": observation,
                    "height": height,
                    "temperature": temperature,
                    "pressure": pressure,
                    "horizon": horizon,
                    "altitude": angle.getString(),
                    "latitude": self.latitude,
                    "longitude": self.GHAobservation
                })

            listSightings = sorted(listSightings, key=lambda k: k['body'])
            listSightings = sorted(listSightings, key=lambda k: k['datetime'])

            for sighting in listSightings:
                dateUTC = datetime.now(tz=timezone.utc)
                dateLocal = dateUTC.astimezone().replace(microsecond=0)
                self.logger.write("LOG: " + dateLocal.isoformat(' ') + ":\t" + sighting['body'] + "\t" + sighting['dt'] + "\t" + sighting['tm'] + "\t" + sighting['altitude'] + "\t" + sighting['latitude'] + "\t" + sighting['longitude'] + "\n")


            dateUTC = datetime.now(tz=timezone.utc)
            dateLocal = dateUTC.astimezone().replace(microsecond=0)
            self.logger.write("LOG: " + dateLocal.isoformat(' ') + " Sighting errors:" + "\t" + str(self.err) + "\n")
            self.logger.close()
            return (approximateLatitude, approximateLongitude)
        except Exception as e:
            raise (ValueError("Fix.getSightings:  Error reading sighting file"))
            self.err += 1


            
if __name__ == "__main__":
    f = Fix()
    f.setSightingFile("sight.xml")
    f.setAriesFile("aries.txt")
    f.setStarFile("stars.txt")
    f.getSightings()
 

