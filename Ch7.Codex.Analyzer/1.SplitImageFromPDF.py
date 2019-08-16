# L.W. Cornelis van Lit (c) 2017-2018
# Function for fetching a specific page from PDF and saving as JPG
#
# NOTE: Sample PDFs not provided. Please search on e.g. archive.org for suitable samples
#
# Part of the book "AMONG DIGITIZED MANUSCRIPTS", github.com/among/digitized-manuscripts
# -------------------------------------------------------------------------------------

# Dependencies
from io import BytesIO
from PyPDF2 import PdfFileMerger

# A string defining a JPG always starts and ends with these values
startMark = b"\xff\xd8"
endMark = b"\xff\xd9"

# Predefined path where files are
pathOfFiles = ""
nameOfCollection = "COLLECTION"
startNumber = 1000
finishNumber = 2000

# -------------------------------------------------------------------------------------

def Accessing_file(filePath):
#    Check if a file exists and is accessible.
    try:
        file = open(filePath, "rb")
        file.close()
        return True
    except:
        return False

# -------------------------------------------------------------------------------------

# This function takes one PDF file and extracts one page from it, to save as JPG.
# Only to be used on PDFs in which each page is only an image.

# Check if file exists. If not, go to next.
def Save_page_PDF(nameOfPDF, pageOfPDF):
    if not Accessing_file(pathOfFiles + nameOfPDF + ".pdf"):
        return

# File exists, so prepare the virtual containers.
    virtualPDF = PdfFileMerger()
    bytePDF = BytesIO()

# Opens PDF and takes out specific page
    with open( pathOfFiles + nameOfPDF + ".pdf", "rb") as sourcePDF:
        virtualPDF.append(fileobj=sourcePDF, pages=(pageOfPDF - 1, pageOfPDF))
        virtualPDF.write(bytePDF)
    virtualPDF.close()

# Read the desired page simply in its string of values
    page = bytePDF.getvalue()
    bytePDF.close()

# Find the start and end of the string defining the JPG
    jpgStart = page.find(startMark, 0)
    jpgEnd = page.find(endMark, jpgStart)

# Reading out the entire string defining the JPG
    jpgString = page[jpgStart:jpgEnd]

# Save the JPG to the hard drive
    with open(nameOfPDF + ".jpg", "wb") as jpgFile:
        jpgFile.write(jpgString)

# -------------------------------------------------------------------------------------

#Loop the function
for i in range(startNumber,finishNumber+1):
    print("Working on Manuscript " + str(i))
    SavePagePDF(nameOfCollection+str(i),1)

# -------------------------------------------------------------------------------------
# This goes at the top
#import time
#start_time = time.time()

# This goes at the bottom
#print("Finished in %s seconds." % (time.time() - start_time))