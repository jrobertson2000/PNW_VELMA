# soils_merger.py
# Author: Paul Pettus
# Date: 10-20-2017
# Description: Merge STATSGO2 and gSSURGO soil texture ASCII Maps
#
# Output is a single ASCII map that will have an assigned soil texture value
# for every cell
#
# By default, cell values will be first assigned the value of the higher
# resolution gSSURGO and if no data exists in the gSSURGO map values
# will be assigned to the output from the lower resolution STATSGO2.
#
# If no values are found in either soil input maps, nodata cells will
# be assigned a nearest neighbor value from a circling radial stepping
# algorithm. The stepping algorithm steps one cell radius per iteration until
# it finds a soil texture cell value.  The algorithm ignores border cells.
#
# Last updated: 11-16-2017

import os, sys, numpy, re, argparse, itertools


# ------------------------------------------------------------------------------------------------


# Error message class
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        parser = argparse.ArgumentParser(description='Output is a single ASCII map that will' +
                                                     ' have an assigned soil texture value for every cell')

        parser.add_argument('-SUR', action='store', dest='surFILE',
                            default='D:/GIS/Nisqually/Soil/ssurgo_aoi_texture_reclass.tif.asc',
                            help='Fully-qualified path + name of ".asc" gSSURGO soil texture file.')

        parser.add_argument('-STA', action='store', dest='staFILE',
                            default='D:/GIS/Nisqually/Soil/statsgo_aoi_texture_reclass.asc',
                            help='Fully-qualified path + name of ".asc" STATSGO2 soil texture file.')

        parser.add_argument('-OUT', action='store', dest='outFILE',
                            default='D:/GIS/Nisqually/Soil/build_old_timey_mudButt_6.asc',
                            help='Fully-qualified path + name of ".asc" output file.')

        args = parser.parse_args()

        # args parsing
        ssurgoAsc = os.path.abspath(args.surFILE)
        statsgoAsc = os.path.abspath(args.staFILE)
        buildFile = os.path.abspath(args.outFILE)

        # Check that files exists
        if not os.path.exists(ssurgoAsc):
            raise Usage('Cannot find AOI file "' + ssurgoAsc + '"')

        if not os.path.exists(statsgoAsc):
            raise Usage('Cannot find AOI file "' + statsgoAsc + '"')

        # do the work
        mergeSoils(ssurgoAsc, statsgoAsc, buildFile)

    except Usage as e:
        print(e.msg)
        return 2

    except Exception as e:
        # STUB exception handler
        # Warning: poor programming style.
        # Catches almost any exception (but not KeyboardInterrupt -- which is a Good Thing)
        raise e


# ------------------------------------------------------------------------------------------------
# Return an ascii file header
def readHeader(asciiFile):
    if not os.path.exists(asciiFile):
        raise Usage('Cannot find ASCII "' + asciiFile + '"')

    # Open file and read in header info
    readFile = open(asciiFile)

    header = readFile.readline()  # ncols
    header += readFile.readline()  # nrows
    header += readFile.readline()  # xllcorner
    header += readFile.readline()  # yllcorner
    header += readFile.readline()  # cellsize
    header += readFile.readline()  # NODATA_value
    readFile.close()

    return header


# ------------------------------------------------------------------------------------------------
# Loop by one + one cell radius of surrounding cells to find nearest neighbor cell value
def lookAround(passRow, passCol, inArray):
    inRow, inCol = inArray.shape

    # Initial search radius at one cell
    radius = 1

    found = False  # found a value

    # Loop by one + one cell radius of surrounding cells to find nearest neighbor cell value
    while found != True:

        rowList = [0]  #
        colList = [0]

        # Create search box of one cell distance
        if radius == 1:

            for i in xrange(radius):
                for j in xrange(radius):
                    rowList.append((i + 1) * -1)
                    rowList.append(i + 1)
                    colList.append((i + 1) * -1)
                    colList.append(i + 1)

            # creates a list of the relative coordinates which to search around the missing value cell
            setList = list(itertools.product(rowList, colList))

        # Else cell radius is larger than one cell
        else:

            rowList = [0]
            colList = [0]

            # Create an inner one radius cell shorter search box
            # Keeps track of already searched cells in radius
            for i in xrange((radius - 1)):
                for j in xrange((radius - 1)):
                    rowList.append((i + 1) * -1)
                    rowList.append(i + 1)
                    colList.append((i + 1) * -1)
                    colList.append(i + 1)

            minusList = list(itertools.product(rowList, colList))

            rowList = [0]
            colList = [0]

            # Create an full radius cell search box around the missing value cell
            for i in xrange(radius):
                for j in xrange(radius):
                    rowList.append((i + 1) * -1)
                    rowList.append(i + 1)
                    colList.append((i + 1) * -1)
                    colList.append(i + 1)

            fullList = list(itertools.product(rowList, colList))

            # Select only the out radius cells from full box list
            setList = list(set(fullList) - set(minusList))

        for item in setList:

            # Check that searched cells are not out of array bounds
            if ((passRow + item[0]) >= 0) and ((passRow + item[0]) < inRow) and ((passCol + item[1]) >= 0) and (
                    (passCol + item[1]) < inCol):

                # nearest neighbor cell value and return it
                value = inArray[(passRow + item[0]), (passCol + item[1])]

                if value != -9999:
                    found = True
                    return value
        # Increase radius by a cell if NA / no values are found
        radius = radius + 1


# ------------------------------------------------------------------------------------------------
# Merge SSUGO STATSGO Soils, then replace nodata values
def mergeSoils(ssurgoAsc, statsgoAsc, buildFile):
    # Load ssrgo array file
    ssgoArray = numpy.loadtxt(ssurgoAsc, skiprows=6)
    # Load statsgo array file
    statsArray = numpy.loadtxt(statsgoAsc, skiprows=6)

    row, col = ssgoArray.shape
    # Create new merge array
    mergeArray = numpy.zeros((row, col))

    print("Starting texture map merge.")

    for i in xrange(row):
        for j in xrange(col):
            # Get soil values
            ssgoValue = ssgoArray[i, j]
            statsValue = statsArray[i, j]

            # Assign higher resolution ssurgo values first
            if ssgoValue != -9999:
                mergeArray[i, j] = ssgoValue
            # Assign lower resolution statsgo next
            elif statsValue != -9999:
                mergeArray[i, j] = statsValue
            # Assign no data value if neither has a set has a value
            else:
                mergeArray[i, j] = -9999

    # Merged ssurgo statsgo, export complete ascii

    fileName, fileExtension = os.path.splitext(buildFile)

    mergeFile = fileName + "_mergedFile" + fileExtension

    header = readHeader(ssurgoAsc)

    f = open(mergeFile, "w")
    f.write(header)
    numpy.savetxt(f, mergeArray, fmt="%i")
    f.close()

    print("Created intermediate merged gSSURGO and STATSGO2 file: ", mergeFile)

    reloadArray = numpy.loadtxt(mergeFile, skiprows=6)

    noDataArray = numpy.zeros((row, col))

    print("Starting NODATA fixes.")

    # Replace nodata cells with search radius algorythm
    for i in xrange(row):
        for j in xrange(col):
            mergeValue = reloadArray[i, j]

            # if nodata, send to search algorythm
            if mergeValue == -9999:
                newValue = lookAround(i, j, reloadArray)

                noDataArray[i, j] = newValue
            # else keep merged data value
            else:
                noDataArray[i, j] = mergeValue

    # Merged ssurgo statsgo and nodata filled, export complete ascii
    header = readHeader(ssurgoAsc)

    outputFile = buildFile

    f = open(outputFile, "w")
    f.write(header)
    numpy.savetxt(f, noDataArray, fmt="%i")
    f.close()

    print("Completed texture file!")


if __name__ == "__main__":
    sys.exit(main())

# ------------------------------------------------------------------------------------------------
# Old code for internal testing only
################################################################################################
### Modify files and locations
################################################################################################
### SSURGO ASCII file
##ssurgoAsc = "D:/GIS/Nisqually/Soil/ssurgo_aoi_texture_reclass.tif.asc"
### STATSGO ASCII file
##statsgoAsc = "D:/GIS/Nisqually/Soil/statsgo_aoi_texture_reclass.asc"
### SSURGO and STATSGO merged ASCII file, intermediate
##mergeFile = "D:/GIS/Nisqually/Soil/merged_soils_5.asc"
### SSURGO and STATSGO merged ASCII file with nodata fixed, final output
##buildFile = "D:/GIS/Nisqually/Soil/build_old_timey_mudButt_5.asc"
################################################################################################
##
### Call main function to merge and replace nodata values
##mergeSoils(ssurgoAsc,statsgoAsc,buildFile)

