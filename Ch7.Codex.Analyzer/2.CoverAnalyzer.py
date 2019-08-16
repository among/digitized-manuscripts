# ----------------------------------------------------------------
# # L.W. Cornelis van Lit (c) 2017-2018
# Finding the angle of the flap of an Islamic manuscript and visually present the result
#
# Part of the book "AMONG DIGITIZED MANUSCRIPTS", github.com/among/digitized-manuscripts
# ----------------------------------------------------------------

#Initial requirements.
import cv2
import numpy as np
import os

#User variables
imageStartingNumber = 1
imageStartingDirection = True
#Either write BW for Black and White processed image to be displayed, or Color for original to be shown.
imageAppearance = "Color"
maximumEdgePoints = 4
kernelbig = np.ones((10, 10), np.uint8)


# ----------------------------------------------------------------

# This function checks if the file exists and if the file is not corrupt.
# number is manuscript number as given in the filename.
# Direction is for browsing when encountering a faulty image.
# True means browsing up, False means browsing down.
# Corruption is checked by making sure file size exceeds 100kb.
def Check_image_readable(imageNumber, direction):
    if direction:
        imageNumber = imageNumber + 1
    else:
        imageNumber = imageNumber - 1
    fileName = 'COLLECTION/COLLECTION{0}.jpg'.format(imageNumber)
    if os.path.isfile(fileName):
        fileSize = os.path.getsize(fileName) >> 10
        if fileSize > 100:
            Analyze_image(imageNumber)
        else:
            Check_image_readable(imageNumber,direction)
    else:
        Check_image_readable(imageNumber,direction)

# ----------------------------------------------------------------

#This function analyses the image.
def Analyze_image(imageNumber):
    img = cv2.imread('COLLECTION/COLLECTION{0}.jpg'.format(imageNumber))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(img, (0, 0), fx=0.8, fy=0.8)
    smaller = cv2.resize(small, (0, 0), fx=0.9, fy=0.9)
    originalImage = smaller
    height, width, _ = originalImage.shape

    ret, thresh1 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    scaled = cv2.resize(thresh1, (0, 0), fx=0.8, fy=0.8)
    openimg = cv2.morphologyEx(scaled, cv2.MORPH_OPEN, kernelbig)
    ret, thresh2 = cv2.threshold(openimg, 1, 255, cv2.THRESH_BINARY)
    scaledagain = cv2.resize(thresh2, (0, 0), fx=0.9, fy=0.9)

    _, contours, _ = cv2.findContours(scaledagain, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(originalImage, contours, -1, (0, 255, 0), 1)
    mainContour = max(contours, key=len)

    hull = cv2.convexHull(mainContour, returnPoints=False)

    hullContourX = []
    hullContourY = []
    for indexHull in hull:
        hullContourX.append(mainContour[indexHull[0]][0][0])
        hullContourY.append(mainContour[indexHull[0]][0][1])

#Hand over output to function that displays image
    Display_image(imageNumber, originalImage, scaledagain, hullContourX, hullContourY)

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
                        np.put(decideMiddlePoints, np.where(reducedXArray < imageWidth / 2), 0)
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

            # tipY needs to be estimated as an average
            tipY = 0
            for tipCoordinate in reducedXMinimumList:
                tipY = tipY + tipOfFlapYArray[tipCoordinate]
            tipY = int(tipY / len(reducedXMinimumList))

        # Is the tip on the right?
        elif np.average(tipOfFlapXArray) > imageWidth / 2:
            reducedXMinimumArray = np.where(tipOfFlapXArray == tipOfFlapXArray.max())
            reducedXMinimumList = reducedXMinimumArray[0].tolist()
            tipX = int(tipOfFlapXArray.max())
            # tipY needs to be estimated as an average
            tipY = 0
            for tipCoordinate in reducedXMinimumList:
                tipY = tipY + tipOfFlapYArray[tipCoordinate]
            tipY = int(tipY / len(reducedXMinimumList))

        # Just to be sure in case some unexpected result comes in, we can deflect it as unable to find angle
        else:
# It is a bit hacky but we need to specify all seven return values as None. If we decide later to add more return values, more 'None' values need to be added here
            return (None, None, None, None, None, None, None)

    # If there are no middle points, no flap can be found.
    else:
        return (None, None, None, None, None, None, None)

    # Check if hull is formed correctly
    if (abs(restOfHullXArray - tipX) < 4).any():
        return (None, tipX, tipY, None, None, None, None)

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

        def Get_upper_point_number():
            return((np.where(upperRestOfHullXArray == upperRestOfHullXArray.min())[0]).tolist())

        def Get_lower_point_number():
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

        def Get_upper_point_number():
            return((np.where(upperRestOfHullXArray == upperRestOfHullXArray.max())[0]).tolist())
        def Get_lower_point_number():
            return((np.where(lowerRestOfHullXArray == lowerRestOfHullXArray.max())[0]).tolist())

    # Establishing upper edge points
    upperEdgePoint = []
    upperEdgeX = []
    upperEdgeY = []
    for pointNumber in range(0, maximumEdgePoints):
        if pointNumber < len(upperRestOfHullXArray):
            upperEdgePoint.append( Get_upper_point_number() )
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
            lowerEdgePoint.append( Get_lower_point_number() )
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
            print("A cannot be zero!")
            return (None, None, None, None, None, None, None)

    lowerAngles = []

    for pointNumber in range(0, len(lowerEdgeX)):
        A = abs(tipLowerX - lowerEdgeX[pointNumber])
        B = abs(tipLowerY - lowerEdgeY[pointNumber])
        C = A**2 + B**2
        try:
            lowerAngles.append(np.rad2deg(np.arccos((A ** 2 + C - B ** 2) / (2 * A * np.sqrt(C)))))
        except:
            print("A cannot be zero!")
            return (None, None, None, None, None, None, None)

    # Entire angle, rounded to zero decimals (would give false sense of accuracy otherwise) is:
    if not upperAngles or not lowerAngles:
        print("Error calculating angle!")
        return (None, None, None, None, None, None, None)
    else:
        finalAngle = int(np.rint( np.average(np.asarray(lowerAngles)) + np.average(np.asarray(upperAngles)) ))
        return(finalAngle, tipX, tipY, lowerEdgeX[-1], lowerEdgeY[-1], upperEdgeX[-1], upperEdgeY[-1])

# ----------------------------------------------------------------

def Display_image(imageNumber, original, analyzed, hullContourX, hullContourY):
# Convert the analyzed result from BW to Color so that we can draw in color over it
    analyzedConverted = cv2.cvtColor(analyzed,cv2.COLOR_GRAY2BGR)
    imageHeight, imageWidth, _ = analyzedConverted.shape

# Do you want to see the original or the processed image?
    global imageAppearance
    if imageAppearance == "BW":
        imageForDisplay = analyzedConverted
    elif imageAppearance == "Color":
        imageForDisplay = original
    else:
        print("Variable imageAppearance must be set to BW or Color!")
        exit()

    #Drawing all points of the outer, reduced hull
    for correctYvalue in range(0,len(hullContourX)):
            xPos = hullContourX[correctYvalue]
            yPos = hullContourY[correctYvalue]
            cv2.circle(imageForDisplay, (xPos, yPos), 3, (255, 0, 0), -1)

    #Calling Angle finding function
    message, tipX, tipY, lowerEdgeX, lowerEdgeY, upperEdgeX, upperEdgeY = Find_angle(hullContourX,hullContourY,imageWidth,imageHeight)
    if message == None:
        message = "No Flap Detectable!"
    else:
        message = "Angle of flap is {0} degrees.".format(message)
        cv2.circle(imageForDisplay, (tipX, tipY), 9, (0, 50, 250), -1)
        cv2.circle(imageForDisplay, (lowerEdgeX, lowerEdgeY), 6, (0, 250, 250), -1)
        cv2.circle(imageForDisplay, (upperEdgeX, upperEdgeY), 6, (0, 250, 250), -1)

# Putting text and showing image
    cv2.putText(imageForDisplay,str(message),(int(imageWidth/2 - 139), int(imageHeight/2 + 1)),cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)
    cv2.putText(imageForDisplay,str(message),(int(imageWidth/2 - 140), int(imageHeight/2)),cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)
    cv2.putText(imageForDisplay,str(message),(int(imageWidth/2 - 141), int(imageHeight/2 -1)),cv2.FONT_HERSHEY_DUPLEX, 1, (120, 0, 220), 1)
    cv2.imshow("{0}".format(imageNumber), imageForDisplay)
    cv2.moveWindow("{0}".format(imageNumber),0,0)

# Awaiting keyboard input.
# The key 'q' will show the manuscript with call number one less than current.
# The key 'w' will show MS with call nr. one more.
# Any other key exits the program.
    key = cv2.waitKey(0) & 0xFF

    if key == ord("q"):
        cv2.destroyAllWindows()
        Check_image_readable(imageNumber, False)
    elif key == ord("w"):
        cv2.destroyAllWindows()
        Check_image_readable(imageNumber, True)
    elif key == ord("e"):
        if imageAppearance == "Color":
            imageAppearance = "BW"
            Display_image(imageNumber, original, analyzed, hullContourX, hullContourY)
        else:
            imageAppearance = "Color"
            Display_image(imageNumber, original, analyzed, hullContourX, hullContourY)
    else:
        cv2.destroyAllWindows()

# ----------------------------------------------------------------

# Execute the code by starting the first function.
Check_image_readable(imageStartingNumber-1, imageStartingDirection)