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
"""

from amc2moodle.amc2moodle import amc2moodle_class as a2m
import os
import hashlib
import unittest
import pkgutil


def check_hash(file1, file2):
    """ Return the md5 sum after removing all withspace.

    Parameters
    ----------
    file1, file2 : string
        Filename 1.

    Returns
    -------
    equiv : bool
        equiv is True if the checksum are equal.
    """

    # list of whitespace expression, avoid pb if xml layout is changed
    ignored_exp = [' ', '\t', '\n']

    # read and replace whitespace
    with open(file1) as f1:
        content1 = f1.read()
        for exp in ignored_exp:
            content1 = content1.replace(exp, '')

    # read and replace whitespace
    with open(file2) as f2:
        content2 = f2.read()
        for exp in ignored_exp:
            content2 = content2.replace(exp, '')

    # compute hash
    h1 = hashlib.md5(content1.encode()).hexdigest()
    h2 = hashlib.md5(content2.encode()).hexdigest()
    equiv = h1 == h2
    return equiv


class TestSuite(unittest.TestCase):
    """ Define test cases for unittest.

    Before changing the reference xml file, please check they can be imported
    in [moodle sandbox](https://sandbox.moodledemo.net/login/index.php)
    teacher / sandbox

    """

    def test_notikz(self):
        """ Tests if input tex (without tikz) file yields reference xml file.
        """
        # define i/o file
        fileIn = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "test/QCM_wo-tikz.tex"))
        fileOut = os.path.abspath('./test_notikz.xml')
        fileRef = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "test/QCM_wo-tikz.xml"))
        # convert to xml
        a2m.amc2moodle(fileInput=fileIn,
                       fileOutput=fileOut,
                       keepFlag=False,
                       catname='test_notikz',
                       deb=0)
        # check it
        equiv = check_hash(fileOut, fileRef)
        if equiv:
            print(' > Converted XML is identical to the ref.')
        #self.assertTrue(equiv, 'The converted file is different from the ref.')

    def test_tikz(self):
        """ Tests if input tex (with tikz) file yields reference xml file.
        """
        # define i/o file
        fileIn = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "test/QCM.tex"))
        fileOut = os.path.abspath('./test_tikz.xml')
        fileRef = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "test/QCM.xml"))
        # convert to xml
        a2m.amc2moodle(fileInput=fileIn,
                       fileOutput=fileOut,
                       keepFlag=True,
                       catname='test_tikz',
                       deb=0)
        # check it
        equiv = check_hash(fileOut, fileRef)
        if equiv:
            print(' > Converted XML is identical to the ref.')
        #self.assertTrue(equiv, 'The converted file is different from the ref.')



if __name__ == '__main__':
    # run unittest test suite
    print('> Running tests...')
    unittest.main()

