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
"""

from amc2moodle.amc2moodle import convert
import subprocess
import sys
import os
from importlib import util  # python 3.x
import shutil
import tempfile
from distutils.dir_util import copy_tree


def checkTools(show=True):
    """ Check if the required Tools are available.
    """
    # Wand Python module
    wand_loader = util.find_spec('wand') 
    wandOk = wand_loader is not None
    if not wandOk:
        print ("Please install Wand's Python module")
    # lxml Python Module
    lxml_loader = util.find_spec('lxml') 
    lxmlOk = lxml_loader is not None
    if not lxmlOk:
        print ("Please install lxml's Python module")
    # LaTeXML
    latexMLwhich = subprocess.run(['which', 'latexml'],
                                  stdout=subprocess.DEVNULL)
    latexmlOk = latexMLwhich.returncode == 0
    if not latexmlOk:
        print ("Please install LaTeXML software (see https://dlmf.nist.gov/LaTeXML/)")

    return wandOk and lxmlOk and latexmlOk


def getFilename(fileIn):
    """ Get the filename without path.
    """
    return os.path.basename(fileIn)


def getPathFile(fileIn):
    """ Get the path of a file without.
    """
    dirname = os.path.dirname(fileIn)
    if not dirname:
        dirname = '.'
    return dirname


class amc2moodle:
    """ Main class to invoke LaTeX to moodle XML conversion.
    """
    def __init__(self, fileInput, fileOutput=None, keepFlag=False,
                 catname='amc', indentXML=False, usetempdir=True, deb=0):
        """ Initialize the object.

        Parameters
        ----------
        fileInput : string
            Input LaTeX file containg amc questions. 
        fileOutput : string, optional
            Output XML moodle file. The default is `inputfile.xml`.
        keepFlag : bool, optional
            If `True` keep temporary file. The default is False.
        catname : TYPE, optional
            DSet moodle category. The default is 'amc'.
        indentXML : bool, optional
            Run XML indentatation program. The default is False.
        usetempdir : bool, optional
            Store all intermediate file in temp directory. The default is True.
        deb : int, optional
            Store all intermediate file for debugging.

        Returns
        -------
        None.

        """
        print('========================')
        print('========================')
        print('=== Start amc2moodle ===')
        print('========================')
        print('========================')
        # Set temp XML filename for internal use
        self.tempxmlfiledef = 'tex2xml.xml'
        self.tempxmlfile = 'tex2xml.xml'
        self.indentXML = indentXML

        # check required tools
        if not checkTools(show=True):
            sys.exit(1)
        # if fileInput is None:  # already chcecked (script + input func)
        #     print('ERROR : Input TeX file is missing.')
        #     sys.exit(1)
        else:
            # encapsulate data
            self.keepFlag = keepFlag
            self.catname = catname
            self.input = fileInput
            self.deb = deb

            if fileOutput:
                self.output = fileOutput
            else:
                # default is input.xml
                tmp = os.path.splitext(self.input)
                self.output = tmp[0] + '.xml'

            if usetempdir:
                # temp
                self.tempdir = tempfile.TemporaryDirectory()
            else:
                # input file directory
                self.tempdir = tempfile.TemporaryDirectory(dir=getPathFile(self.input),
                                                           prefix='amc2moodle')
            # set temporary file
            self.tempxmlfile = os.path.join(self.tempdir.name,
                                            self.tempxmlfiledef)
            # Show summury of all loaded parameters
            self.showData()

        #run the building of the xml file for Moodle
        self.runBuilding()

    def cleanUpTemp(self):
        """ Clean-up temp directory created by tempfile.TemporaryDirectory().
        """
        self.tempdir.cleanup()
        print(' > Clean-up tempfile.')

    def showData(self):
        """ Show loaded parameters.
        """
        print('====== Parameters ======')
        print(' > path input TeX: %s' % getPathFile(self.input))
        print(' > input TeX file: %s' % getFilename(self.input))
        print(' > temporary directory: %s' % getPathFile(self.tempdir.name))
        print(' > path output TeX: %s' % getPathFile(self.output))
        print(' > output XML file: %s' % getFilename(self.output))
        print(' > temp XML file: %s' % self.tempxmlfile)
        print(' > keep temp files: %s' % self.keepFlag)
        print(' > categorie name: %s' % self.catname)

    def endMessage(self):
        """ Show end message explaining moodle inmport procedure.
        """
        print("""File converted. Check below for errors...

            For import into moodle :
            --------------------------------
            - Go to the course admistration\\question bank\\import
            - Choose 'moodle XML format'
            - In the option chose : 'choose the closest grade if not listed'
              in the 'General option' since Moodle used tabulated grades
              like 1/2, 1/3 etc...
        """)

    def runLaTeXML(self):
        """ Run LaTeXML on the input TeX file.
        """
        # run LaTeXML
        print(' > Running LaTeXML conversion')
        runStatus = subprocess.run([
            'latexml',
            '--noparse',
            '--nocomments',
            '--path=%s' % os.path.dirname(__file__),
            '--dest=%s' % self.tempxmlfile,
            self.input])
        return runStatus.returncode == 0

    def runXMLindent(self):
        """ Run XML indentation with subprocess.
        """
        # check for xmlindent
        xmlindentwhich = subprocess.run(['which', 'xmlindent'])
        xmlindentOk = xmlindentwhich.returncode == 0
        # check for xmllint (Macos)
        xmllintwhich = subprocess.run(['which', 'xmllint'])
        xmllintOk = xmllintwhich.returncode == 0

        # linux
        if xmlindentOk:
            print(' > Indenting XML output...')
            subprocess.run(['xmlindent', self.output, '-o', self.output],
                           stdout=subprocess.DEVNULL)
        # MacOS
        if xmllintOk and not xmlindentOk:
            print(' > Indenting XML output...')
            subprocess.run(['xmllint', self.output,'--format','--output', self.output],
                           stdout=subprocess.DEVNULL)

    def runBuilding(self):
        """ Build the xml file for Moodle quizz.
        """
        print('====== Build XML =======')
        print(' > Running LaTeXML pre-processing...')
        if self.runLaTeXML():
            # run script
            print(' > Running Python conversion...')
            convert.to_moodle(
                filein=getFilename(self.tempxmlfile),
                pathin=getPathFile(self.input),
                workingdir=self.tempdir.name,
                fileout=getFilename(self.output),
                pathout=getPathFile(self.output),
                catname=self.catname,
                deb=self.deb)
            # remove temporary file
            if self.keepFlag:
                # copy all temporary files
                tempdirSave = tempfile.mkdtemp(prefix='tmp_amc2moodle_',
                                               dir=getPathFile(self.output))
                #
                print(' > Save all temp files in: %s' % tempdirSave)
                copy_tree(self.tempdir.name, tempdirSave)

            # run XMLindent
            if self.indentXML:
                self.runXMLindent()

            # clean up temp dir
            self.cleanUpTemp()

            # show end message
            self.endMessage()

        else:
            print('ERROR during LaTeXML processing.')
            sys.exit(1)
