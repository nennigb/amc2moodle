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

from amc2moodle import grading
import subprocess
import sys
import argparse
import os
import importlib  #python 3.x
import shutil

def checkTools(show=True):
    """
    Check if the required Tools are available
    """
    # Wand Python module
    wand_loader = importlib.util.find_spec('wand') 
    wandOk = wand_loader is not None
    if not wandOk:
        print ("Please install Wand's Python module")
    # lxml Python Module
    lxml_loader = importlib.util.find_spec('lxml') 
    lxmlOk = lxml_loader is not None
    if not lxmlOk:
        print ("Please install lxml's Python module")
    # LaTeXML
    latexMLwhich = subprocess.run(['which','latexml'],stdout=subprocess.DEVNULL)
    latexmlOk = latexMLwhich.returncode == 0
    if not latexmlOk:
        print ("Please install LaTeXML software (see https://dlmf.nist.gov/LaTeXML/)")
    # xmlindent
    xmlindentwhich = subprocess.run(['which','xmlindent'],stdout=subprocess.DEVNULL)
    xmlindentOk = xmlindentwhich.returncode == 0
    # if not xmlindentOk:
    #     print ("Please install (optional) XML indent software (see http://xmlindent.sourceforge.net/)")
    #
    return wandOk and lxmlOk and latexmlOk

def getFilename(fileIn):
    """
    get the filename without path
    """
    return os.path.basename(fileIn)

def getPathFile(fileIn):
    """
    get the path of a file without
    """
    dirname = os.path.dirname(fileIn)
    if not dirname:
        dirname='.'
    return dirname 
    
    

class amc2moodle:
    def __init__(self,fileInput=None,fileOutput=None,keepFile=None,catname=None):
        """
        initialized object
        """
        print('========================')
        print('========================')
        print('=== Start amc2moodle ===')
        print('========================')
        print('========================')
        # default value
        self.output = None
        self.tempxmlfiledef = 'tex2xml.xml'
        self.tempxmlfile = 'tex2xml.xml'
        self.keepFlag = False
        self.catname = None
        # check required tools
        if not checkTools(show=True):
            sys.exit()
        if fileInput is None:
            print('Input TeX file is missing')
            sys.exit()
        else:            
            #load data
            self.input = fileInput
            if fileOutput is not None:
                self.output = fileOutput
            else:
                tmp = os.path.splitext(self.input)
                self.output = tmp[0]+'.xml'
            if keepFile is not None:
                self.keepFlag = keepFile
            if catname is not None:
                self.catname = catname
            #temporary file
            self.tempxmlfile = os.path.join(getPathFile(self.input),self.tempxmlfiledef)
            self.showData()
        #run the building of the xml file for Moodle
        self.runBuilding()

    def showData(self):
        """
        show loaded parameters
        """
        print('====== Parameters ======')
        print(' > path input TeX: %s'%getPathFile(self.input))
        print(' > input TeX file: %s'%getFilename(self.input))
        print(' > path output TeX: %s'%getPathFile(self.output))
        print(' > output XML file: %s'%getFilename(self.output))
        print(' > temp XML file: %s'%self.tempxmlfile)
        print(' > keep temp files: %s'%self.keepFlag)
        print(' > categorie name: %s'%self.catname)

    def endMessage(self):
        print("""File converted. Check below for errors...

            This GNU bash script is not fully compatible with Mac and path error may
            occured. See issues on amc2moodle github page.

            For import into moodle :
            --------------------------------
            - Go to the course admistration\question bank\import
            - Choose 'moodle XML format'
            - In the option chose : 'choose the closest grade if not listed'
            in the 'General option'
            (Moodle used tabulated grades like 1/2, 1/3 etc...)
        .""")

    def runLaTeXML(self):
        """
        Run LaTeXML on the input TeX file
        """
        #run LaTeXML
        print(' > Running LaTeXML conversion')
        subprocess.run([
            'latexml',
            '--noparse',
            '--nocomments',
            '--path=%s'%getPathFile(self.output),
            '--dest=%s'%self.tempxmlfile,
            self.input])

    def runXMLindent(self):
        """
        Build the xml file for Moodle quizz
        """
        # check for xmlindent
        xmlindentwhich = subprocess.run(['which','xmlindent'])
        xmlindentOk = xmlindentwhich.returncode == 0
        #
        if xmlindentOk:
            subprocess.run([
                'xmlindent',
                self.output,
                '-o',
                self.output])

    def runBuilding(self):
        """
        Build the xml file for Moodle quizz
        """
        print('====== Build XML =======')
        self.runLaTeXML()
        #run script
        print(' > Running Python conversion')
        grading.grading(
            inputfile=getFilename(self.tempxmlfile),
            inputdir=getPathFile(self.input),
            outputfile=getFilename(self.output),
            outputdir=getPathFile(self.input),
            keepFlag=self.keepFlag,
            incatname=self.catname
        )
        #remove temporary file
        if not self.keepFlag:
            print(' > Remove temp file: %s'%self.tempxmlfile)
            os.remove(self.tempxmlfile)
        #run XMLindent
        self.runXMLindent()
        #copy file from working dir to outputdir
        if getPathFile(self.input) != '.':
            shutil.copyfile(os.path.join(getPathFile(self.input),getFilename(self.output)),self.output)
        #
        self.endMessage()

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
    print(args)
    #
    if args.inputfile:
        fileIn = args.inputfile
    if args.output:
        fileOut = args.output[0]
    keepFlag = args.keep
    if args.catname:
        catname = args.catname
    #
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
        amc2moodle(fileInput=fileIn,fileOutput=fileOut,keepFile=keepFlag,catname=catname)


# Run autonomous
if __name__ == '__main__':
    # run with options
    run()