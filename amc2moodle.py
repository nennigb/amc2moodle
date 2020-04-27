#!/usr/bin/env python
"""
    This file is part of amc2moodle, a convertion tool to recast quiz written
    with the LaTeX format used by automuliplechoice 1.0.3 into the 
    moodle XML quiz format.
    Copyright (C) 2016  Benoit Nennig, benoit.nennig@supmeca.fr 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

usage :
    ./amc2moodle.py -h to see option
        
part of amc2moodle : 
    call xslt stylesheet and complete the require xml element
    compute the grade according to the amc way
    convert non png img into png and embedded them in the output_file
    
warning : 
    the grade are not computed exactly as in amc, see amc2moodle.pdf

"""

from amc2moodle import amc2moodle_class as a2m
import argparse
import os





def run():
    """
    Read parser and run amc2mooodle
    """
    #defulat values
    fileIn = None
    fileOut = None
    keepFlag = False
    catname = None
    #deal with arguments
    parser = argparse.ArgumentParser(description="""This script converts a tex file of AMC questions into an xml file
    suitable for moodle import. Only question and questionmult
    environnement are ready!
    This GNU bash script is not fully compatible with Mac and path error may
    occured. See issues on amc2moodle github page.""")
    #
    parser.add_argument("inputfile",nargs='?',help="Input TeX file (mandatory)")
    # parser.add_argument("-i", "--input",nargs=1,dest='inputfile',help="Input TeX file (mandatory)",required=False)
    parser.add_argument("-o", "--output",nargs=1, help="Output XML file (optional)",required=False)
    parser.add_argument("-k", "--keep", help="Keep temporary file (useful for debuging) (optional)",required=False,action="store_true")
    parser.add_argument("-c", "--catname", nargs=1, help="Use \element{label} as category tag as a subcategorie root_cat_name (optional)",required=False)
    #
    args = parser.parse_args()
    # print(args)
    #
    if args.inputfile:
        fileIn = args.inputfile
    if args.output:
        fileOut = args.output[0]
    keepFlag = args.keep
    if args.catname:
        catname = args.catname[0]
    #
    if fileIn is not None:
        fileInOk = os.path.exists(fileIn)
    #
    if fileInOk:
        print('Input file: %s - status: %s'%(fileIn,"OK"))
    else:
        print('Input file: %s - status: %s'%(fileIn,"does not exist"))
    if fileOut:
        fileOutOk = not os.path.exists(fileOut)
        if fileOutOk:
            print('Output file: %s - status: Ok'%fileOut)
        else:
            print('Output file: %s - status: Already exists (will be overwritten)'%fileOut)

    # run computation
    if fileInOk:        
        a2m.amc2moodle(fileInput=fileIn,fileOutput=fileOut,keepFile=keepFlag,catname=catname)


# Run autonomous
if __name__ == '__main__':
    # run with options
    run()