# L.W. Cornelis van Lit (c) 2017-2018
# Finding the angle of the flap of an Islamic manuscript and iterating over a large collection
#
# Part of the book "AMONG DIGITIZED MANUSCRIPTS", github.com/among/digitized-manuscripts
# -------------------------------------------------------------------------------------

# Dependencies
import cv2
import numpy as np
import io
from PyPDF2 import PdfFileMerger
import csv
import os
import time

#For analytical purpose only, a timer is set
start_time = time.time()

# A dictionary is created to catch the results
results = {}

# A string defining a JPG always starts and ends with these values
startmark = b"\xff\xd8"
endmark = b"\xff\xd9"

#User variables
maximumEdgePoints = 4
kernelbig = np.ones((10, 10), np.uint8)

# -------------------------------------------------------------------------------------

def Initiate_angle_finding(pathOfFiles, nameOfPDF, pageOfPDF):

# Check if file exists and is sound. Change ".pdf" to .jpg" to use jpgs instead of pdfs and uncomment lines 67 and 68.
    if not Accessing_file(pathOfFiles + nameOfPDF + ".pdf", 'rb'):
        results[nameOfPDF]="File inaccessible."

# Check if image on specific page can be extracted.
    else:
        extractedImage = Extract_image_from_PDF(pathOfFiles, nameOfPDF, pageOfPDF)
        if not type(extractedImage) == np.ndarray:
            results[nameOfPDF] = "Image inaccessible."

# Perform analysis on image.
        else:
            hullContourX, hullContourY, imageWidth, imageHeight = Analyze_image(extractedImage)
            if not hullContourX:
                results[nameOfPDF] = "Cannot analyze image."
            else:
                angleInfo = Find_angle(hullContourX, hullContourY, imageWidth, imageHeight)
                results[nameOfPDF] = angleInfo

# -------------------------------------------------------------------------------------

# Check if a file exists and is accessible.
def Accessing_file(filepath, mode):
    try:
        f = open(filepath, mode)
        f.close()
    except:
        #File unreadable.
        return False
    #File readable.
    return True

# -------------------------------------------------------------------------------------
# This function takes one PDF file and extracts one page from it, to save as JPG.
# Only to be used on PDFs in which each page is only an image.

def Extract_image_from_PDF(pathOfFiles, nameOfPDF, pageOfPDF):

#Uncomment these two lines of code if files are already images:
#    img = cv2.imread(pathOfFiles + nameOfPDF + ".jpg")
#    return img

# File exists, so prepare the virtual containers.
    merger = PdfFileMerger()
    virtualpdf = io.BytesIO()

# Opens PDF and takes out specific page
    with open( pathOfFiles + nameOfPDF + ".pdf", "rb") as sourcePDF:
        try:
            merger.append(fileobj=sourcePDF, pages=(pageOfPDF - 1, pageOfPDF))
            merger.write(virtualpdf)
        except:
            return
    merger.close()

# Read the desired page simply in its string of values
    pdf = virtualpdf.getvalue()
    virtualpdf.close()

# Find the start and end of the string defining the JPG
    jpgstart = pdf.find(startmark, 0)
    jpgend = pdf.find(endmark, jpgstart)

# Reading out the entire string defining the JPG
    jpgstring = pdf[jpgstart:jpgend]

# Preparing the string to be read by OpenCV
    jpgstring2 = np.fromstring(jpgstring, np.uint8)

# Turn into OpenCV-readable image
    image = cv2.imdecode(jpgstring2, 1)

# Give back OpenCV-readable image
    return image

# ----------------------------------------------------------------

#This function analyses the image.
def Analyze_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    # Twice scaling is part of accessing the angle
    scaled = cv2.resize(thresh1, (0, 0), fx=0.8, fy=0.8)
    openimg = cv2.morphologyEx(scaled, cv2.MORPH_OPEN, kernelbig)
    ret, thresh2 = cv2.threshold(openimg, 1, 255, cv2.THRESH_BINARY)
    scaledagain = cv2.resize(thresh2, (0, 0), fx=0.5, fy=0.5)

    imageHeight, imageWidth = scaledagain.shape

    _, contours, _ = cv2.findContours(scaledagain, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    try:
        mainContour = max(contours, key=len)
    except:
        return (None,None,None,None)

    hull = cv2.convexHull(mainContour, returnPoints=False)

    hullContourX = []
    hullContourY = []
    for correctYvalue in hull:
        hullContourX.append(mainContour[correctYvalue[0]][0][0])
        hullContourY.append(mainContour[correctYvalue[0]][0][1])

    mainContourX = []
    mainContourY = []

    mainContourTotalX = 0
    mainContourTotalY = 0
    for correctYvalue in range(0,len(mainContour)):
        mainContourX.append(mainContour[correctYvalue][0][0])
        mainContourY.append(mainContour[correctYvalue][0][1])
        mainContourTotalX = mainContourTotalX + mainContour[correctYvalue][0][0]
        mainContourTotalY = mainContourTotalY + mainContour[correctYvalue][0][1]

    return hullContourX, hullContourY, imageWidth, imageHeight

# ----------------------------------------------------------------

def Find_angle(hullContourX, hullContourY, imageWidth, imageHeight):
    # Using NumPy requires arrays
    reducedXArray = np.array(hullContourX)
    reducedYArray = np.array(hullContourY)

    # Using NumPy to get index numbers of all Y values within 15% of middle
    reducedYLength = len(hullContourY)
    varianceY = imageHeight * 0.15
    minimumY = imageHeight / 2 - varianceY
    maximumY = imageHeight / 2 + varianceY
    decideMiddlePoints = np.zeros(reducedYLength, dtype=np.int)

    for correctYvalue in range(0, reducedYLength):
        if minimumY <= hullContourY[correctYvalue] <= maximumY:
            np.put(decideMiddlePoints, correctYvalue, 1)
            xVal = hullContourX[correctYvalue]

            # Ruling out spurious points on non-flap side by checking if nearby points in terms of x-value are near edge in terms of y-value (i.e. in a corner)
            # Also ruling out flaps with distortions, i.e. deleting all middle points on the left/right side of the image where there is a point which meets above requirement.
            for otherXvalues in range(0, reducedYLength):
                if (xVal - 5 <= hullContourX[otherXvalues] <= xVal + 5) and (hullContourY[otherXvalues] < imageHeight * 0.2 or hullContourY[otherXvalues] > imageHeight * 0.8):
                    if hullContourX[otherXvalues] <= imageWidth/2:
                        np.put(decideMiddlePoints,np.where( reducedXArray < imageWidth / 2), 0)
                    else:
                        np.put(decideMiddlePoints, np.where(reducedXArray > imageWidth / 2), 0)
                    break

    # Only proceed if a flap can be found.
    # Get X,Y value of tip-point, making sure there are some points that could be the tip

    if not np.count_nonzero(decideMiddlePoints) == 0:
        # Get X,Y value of only tip-points
        tipOfFlapYArray = reducedYArray[decideMiddlePoints != 0]
        tipOfFlapXArray = reducedXArray[decideMiddlePoints != 0]
        restOfHullXArray = reducedXArray[decideMiddlePoints == 0]
        restOfHullYArray = reducedYArray[decideMiddlePoints == 0]

        # tipX needs to be decided, left or right
        # Is the tip on the left?
        if np.average(tipOfFlapXArray) < imageWidth / 2:
            # Get X,Y value of furthest tip-point
            reducedXMinimumArray = np.where(tipOfFlapXArray == tipOfFlapXArray.min())
            reducedXMinimumList = reducedXMinimumArray[0].tolist()
            tipX = int(tipOfFlapXArray.min())

        # Is the tip on the right?
        elif np.average(tipOfFlapXArray) > imageWidth / 2:
            reducedXMinimumArray = np.where(tipOfFlapXArray == tipOfFlapXArray.max())
            reducedXMinimumList = reducedXMinimumArray[0].tolist()
            tipX = int(tipOfFlapXArray.max())

        else:
            return ("Middle points undetermined.")
    else:
        if len(hullContourX) > 4:
            return ("Cannot find flap.")
        else:
            return ("No flap.")

    # Check if hull is formed correctly
    if (abs(restOfHullXArray - tipX) < 4).any():
        return ("Some point of hull too close to X value of tip. Hull incorrectly identified.")

    # Now find points along the edge and calculate angle

    tipUpperX = tipX
    tipUpperY = np.min(tipOfFlapYArray[reducedXMinimumList])
    tipLowerX = tipX
    tipLowerY = np.max(tipOfFlapYArray[reducedXMinimumList])

    #For left flap we need to look at minimal X values, for right flap maximal X values.
    if tipX < imageWidth / 2:

        # Get all XY that are in the upper quadrant
        upperRestOfHullXArray = restOfHullXArray[restOfHullYArray < imageHeight / 2]
        upperRestOfHullYArray = restOfHullYArray[restOfHullYArray < imageHeight / 2]

        upperRestOfHullYArray = upperRestOfHullYArray[upperRestOfHullXArray < imageWidth * 0.2]
        upperRestOfHullXArray = upperRestOfHullXArray[upperRestOfHullXArray < imageWidth * 0.2]

        # Get all XY that are in the lower quadrant
        lowerRestOfHullXArray = restOfHullXArray[restOfHullYArray > imageHeight / 2]
        lowerRestOfHullYArray = restOfHullYArray[restOfHullYArray > imageHeight / 2]

        lowerRestOfHullYArray = lowerRestOfHullYArray[lowerRestOfHullXArray < imageWidth * 0.2]
        lowerRestOfHullXArray = lowerRestOfHullXArray[lowerRestOfHullXArray < imageWidth * 0.2]

        def GetUpperPointNumber():
            return((np.where(upperRestOfHullXArray == upperRestOfHullXArray.min())[0]).tolist())

        def GetLowerPointNumber():
            return((np.where(lowerRestOfHullXArray == lowerRestOfHullXArray.min())[0]).tolist())
    else:
        # Get all XY that are in the upper quadrant
        upperRestOfHullXArray = restOfHullXArray[restOfHullYArray < imageHeight / 2]
        upperRestOfHullYArray = restOfHullYArray[restOfHullYArray < imageHeight / 2]

        upperRestOfHullYArray = upperRestOfHullYArray[upperRestOfHullXArray > imageWidth * 0.8]
        upperRestOfHullXArray = upperRestOfHullXArray[upperRestOfHullXArray > imageWidth * 0.8]

        # Get all XY that are in the lower quadrant
        lowerRestOfHullXArray = restOfHullXArray[restOfHullYArray > imageHeight / 2]
        lowerRestOfHullYArray = restOfHullYArray[restOfHullYArray > imageHeight / 2]

        lowerRestOfHullYArray = lowerRestOfHullYArray[lowerRestOfHullXArray > imageWidth * 0.8]
        lowerRestOfHullXArray = lowerRestOfHullXArray[lowerRestOfHullXArray > imageWidth * 0.8]

        def GetUpperPointNumber():
            return((np.where(upperRestOfHullXArray == upperRestOfHullXArray.max())[0]).tolist())
        def GetLowerPointNumber():
            return((np.where(lowerRestOfHullXArray == lowerRestOfHullXArray.max())[0]).tolist())

    # Establishing upper edge points
    upperEdgePoint = []
    upperEdgeX = []
    upperEdgeY = []
    for pointNumber in range(0, maximumEdgePoints):
        if pointNumber < len(upperRestOfHullXArray):
            upperEdgePoint.append( GetUpperPointNumber() )
            upperEdgeX.append( upperRestOfHullXArray[upperEdgePoint[pointNumber][0]] )
            upperEdgeY.append(upperRestOfHullYArray[upperEdgePoint[pointNumber][0]])
            upperRestOfHullXArray = np.delete(upperRestOfHullXArray, upperEdgePoint[pointNumber])
            upperRestOfHullYArray = np.delete(upperRestOfHullYArray, upperEdgePoint[pointNumber])

    # Establishing lower edge points
    lowerEdgePoint = []
    lowerEdgeX = []
    lowerEdgeY = []
    for pointNumber in range(0, maximumEdgePoints):
        if pointNumber < len(lowerRestOfHullXArray):
            lowerEdgePoint.append( GetLowerPointNumber() )
            lowerEdgeX.append(lowerRestOfHullXArray[lowerEdgePoint[pointNumber][0]])
            lowerEdgeY.append(lowerRestOfHullYArray[lowerEdgePoint[pointNumber][0]])
            lowerRestOfHullXArray = np.delete(lowerRestOfHullXArray, lowerEdgePoint[pointNumber])
            lowerRestOfHullYArray = np.delete(lowerRestOfHullYArray, lowerEdgePoint[pointNumber])

    # !!! Note that upper/lowerRestOfHull are now empty !!!

    # Calculate degree of angle based on lower edge points
    # First apply Theorem of Pythogaras to find all lengths, with A = horizontal, B = vertical, C = diagonal

    upperAngles = []
    for pointNumber in range(0,len(upperEdgeX)):
        # First apply Theorem of Pythogaras to find all lengths, with A = horizontal, B = vertical, C = diagonal
        A = abs(tipUpperX - upperEdgeX[pointNumber])
        B = abs(tipUpperY - upperEdgeY[pointNumber])
        C = A**2 + B**2
        # Then use Law of Cosine to find angle. Answer is returned in Radians so it needs to be transposed to Degrees for human readability.
        try:
            upperAngles.append( np.rad2deg(np.arccos((A**2 + C - B**2) / (2 * A * np.sqrt(C)))) )
        except:
            return ("Upper points incorrectly identified.")

    lowerAngles = []
    for pointNumber in range(0, len(lowerEdgeX)):
        A = abs(tipLowerX - lowerEdgeX[pointNumber])
        #A is 0 which is causing the problem. Not allowed to divide by 0.
        B = abs(tipLowerY - lowerEdgeY[pointNumber])
        C = A**2 + B**2
        try:
            lowerAngles.append(np.rad2deg(np.arccos((A ** 2 + C - B ** 2) / (2 * A * np.sqrt(C)))))
        except:
            return ("Upper points incorrectly identified.")

    # Entire angle, rounded to zero decimals (would give false sense of accuracy otherwise) is:
    if not upperAngles or not lowerAngles:
        return ("Cannot make out angle.")
    else:
        finalAngle = int(np.rint( np.average(np.asarray(lowerAngles)) + np.average(np.asarray(upperAngles)) ))
        return(finalAngle)

# -------------------------------------------------------------------------------------

#for file in os.listdir(directory):
#    filename = os.fsdecode(file)
#    if filename.endswith(".pdf"):
#        if not filename.endswith("_text.pdf"):
#            filename = filename[:-4]
#            print("Working on manuscript " + filename)
#            Initiate_angle_finding(directoryPath,filename,1)

#We can also loop the function over the number in which the filename ends by using these lines of code:
collectionName = "COLLECTION"
startNumber = 4
finishNumber = 500
for i in range(startNumber,finishNumber+1):
    if not i == 96 and not i == 392:
        print("Working on manuscript " + collectionName + " " + str(i))
        Initiate_angle_finding("/Volumes/Manuscripts_1/COLLECTION/",collectionName+str(i), 1)

# Save results as CSV
with open(collectionName+".csv", "w") as output:
    writeToCSV = csv.writer(output)
    writeToCSV.writerows(results.items())

print("Finished in %s seconds." % (time.time() - start_time))