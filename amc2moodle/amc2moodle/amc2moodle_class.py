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

from ..amc2moodle import convert
from ..utils.flatex import Flatex
import subprocess
import sys
import os
from importlib import util  # python 3.x
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
    # tag for magic comments
    magictag = '%amc2moodle '

    def __init__(self, fileInput, fileOutput=None, keepFlag=False,
                 catname='amc', indentXML=False, usetempdir=True,
                 magic_flag=True, deb=0):
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
        magic_flag : bool, optional
            Enable magic comment.The default is True.
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
            self.inputtex = fileInput
            self.deb = deb
            self.magic_flag = magic_flag

            if fileOutput:
                self.output = fileOutput
            else:
                # default is input.xml
                tmp = os.path.splitext(self.inputtex)
                self.output = tmp[0] + '.xml'

            if usetempdir:
                # temp
                self.tempdir = tempfile.TemporaryDirectory()
            else:
                # input file directory
                self.tempdir = tempfile.TemporaryDirectory(dir=getPathFile(self.inputtex),
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
        print(' > Clean-up tempfile.')
        self.tempdir.cleanup()
        # remove magictex temp file
        if not self.keepFlag:
            os.unlink(self.magictex)

    def showData(self):
        """ Show loaded parameters.
        """
        disable = {True:'enable', False:'disable'}
        print('====== Parameters ======')
        print(' > path input TeX: %s' % getPathFile(self.inputtex))
        print(' > input TeX file: %s' % getFilename(self.inputtex))
        print(' > temporary directory: %s' % getPathFile(self.tempdir.name))
        print(' > path output TeX: %s' % getPathFile(self.output))
        print(' > output XML file: %s' % getFilename(self.output))
        print(' > temp XML file: %s' % self.tempxmlfile)
        print(' > keep temp files: %s' % self.keepFlag)
        print(' > categorie name: %s' % self.catname)
        print(' > magic comments: %s' % disable[self.magic_flag])

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

    def removeMagicComment(self):
        """ Remove magic comments prefix to enable amc2moodle dedicated LaTeX
        commands.
        """

        pathin = getPathFile(self.inputtex)
        prefix = os.path.splitext(getFilename(self.inputtex))[0] + '_'

        # Create magitex as persistent temp file in input.tex dir
        with tempfile.NamedTemporaryFile(mode='w',
                                         prefix=prefix,
                                         suffix='_magic.tex',
                                         dir=pathin,
                                         delete=False) as m:
            # Store tempfile name for alter use
            self.magictex = m.name

        # Merge all included tex files in one and remove magic comments.
        texpand = Flatex(self.inputtex, self.magictex,
                         magic_flag=self.magic_flag,
                         noline=False)
        texpand.expand()
        texpand.report()


    def runLaTeXML(self):
        """ Run LaTeXML on the input TeX file.
        """
        # run LaTeXML on magictex file
        print(' > Running LaTeXML conversion')
        runStatus = subprocess.run([
            'latexml',
            '--noparse',
            '--nocomments',
            '--path=%s' % os.path.dirname(__file__),
            '--dest=%s' % self.tempxmlfile,
            self.magictex])
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
        # remove magic comment, return magictex
        if self.magic_flag:
            print(' > Search for magic comments...')
        self.removeMagicComment()


        print(' > Running LaTeXML pre-processing...')
        # process magictex as tex input
        if self.runLaTeXML():
            # run script
            print(' > Running Python conversion...')
            convert.to_moodle(
                filein=getFilename(self.tempxmlfile),
                pathin=getPathFile(self.inputtex),
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
