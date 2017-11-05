'''
Author: Sabrina Flemming
Class: CS229 at Stanford University
Date:

This program uses the google static maps api to source satalite image data, and will save the images
in the same folder in which this script is run

See https://developers.google.com/maps/documentation/static-maps/intro for more information on how
the API works
    The program builds a URL, and issues an HTTP GET request to the link. Google's
    Static Maps API which then returns an image that most closely matches the specified
    parameters
'''
import urllib.parse             #used to build the URL
import csv                      #used to work with CSVs
from urllib.request import *    #used to issue HTTP GET
from urllib.error import *      #used to handle HTTP errors

# Global variables used by the API
#a string used by Google to monitor API usage by my account - should not change
apiKey = "AIzaSyDifZ3ix-Db_U-Yc--HdSG7DoPmdoiG2H4"

#should not change
baseURL = "https://maps.googleapis.com/maps/api/staticmap?"

# Tweakable variables to change how the image looks
imageSize = "640x640"       #max image size is 640x640
zoomLevel = 17              #scale from 1 (most zoomed out) to 21 (most zoomed in)

# Variables that deal with formatting the image PNG is reccomended as it is not lossy
scale = 2               #the amount of pixels in the image (1 is lowest, 2 is highest)
imageFormat = "PNG"
mapType = "satellite"   #see API docs for other categories if necessary

def fetchImage(coords):
    '''
    Fetches an image from the google static map API
    parameter coords can be a lat lng pair in the following
    format: "lat,lng" or a qualified street address:
    "Jim's Cafe, New York, New York, USA"
    '''
    # Build a dict of params and their values
    paramMap = dict()
    paramMap["key"] = apiKey
    paramMap["zoom"] = zoomLevel
    paramMap["center"] = coords
    paramMap["size"] = imageSize
    paramMap["scale"] = scale
    paramMap["format"] = imageFormat
    paramMap["maptype"] = mapType
    # Create URL to access image
    downloadURL = baseURL + urllib.parse.urlencode(paramMap)
    # Download image data to internal buffer
    return urllib.request.urlopen(downloadURL)

def writeImage(filename, data):
    '''
    Handles writing an image to a file
    '''
    f = open(filename, "wb")
    f.write(data.read())
    f.close()

def parseCsv(filename):
    '''
    Parses a spreadsheet of the same format as Plant Data.xlsm
    Steps taken to properly format it:
        - File > Save as Plant Data.csv
        - Open the csv and reformat all cells to "General"
        - Split column 16 ("Lat,Lng") into two separate columns
    '''
    # Config variables: Used to adapt function to different spreadsheet
    latCol = 16
    lonCol = 17
    idCol = 0
    nameCol = 1

    sourced = 0     #how many images were sourced out
    errors = 0      #how many images resulted in errors

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar= '|')     #entries are seperated by a comma

        for row in reader:
            #perform checking for row info validity
            if(row[latCol] == "ND" or row[lonCol] == "ND"):
                # If the row doesn't contain a lat or lon, continue
                errors += 1
                continue
            elif(row[16] == "Lat"):
                # Skip the first line
                continue

            # Build coords string to pass in to fetchImage
            coords = row[latCol]+","+row[lonCol]

            # Create filename of the following format: ID_Name@Lat+Lon.PNG
            fileName = row[idCol] + "_" + row[nameCol] + "@" + row[latCol] + "+" \
                + row[lonCol]+".PNG"

            #try/catch block for http errors
            try:
                # Try fetching the image and saving it
                data = fetchImage(coords)
                writeImage(fileName, data)
                print("Saved image: ", fileName)
                sourced += 1
            except HTTPError as e:
                # Used to handle HTTP errors; Just prints error description and
                # continues trying to process the rest of the data csv
                errors += 1
                print(e.read(), "continuing to attempt sourcing images")

    print("Images succesfully sourced: ", sourced)
    print("Images not successfully sourced: ", errors)

if __name__ == "__main__":
    # Used to run the script if it is not imported into another python module
    parseCsv("Plant Data.csv")
