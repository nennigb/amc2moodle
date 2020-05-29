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

from amc2moodle.amc2moodle.test import check_hash
from amc2moodle.moodle2amc import Quiz
import os
import unittest
import pkgutil



class TestSuite(unittest.TestCase):
    """ Define test cases for unittest.

    Before changing the reference xml file, please check they can be imported
    in [moodle sandbox](https://sandbox.moodledemo.net/login/index.php)
    teacher / sandbox

    """

    def test_mdl_bank(self):
        """ Tests if input XML file yields reference LaTeX file.
        """
        # define i/o file
        fileIn = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "test/moodle-bank-exemple.xml"))
        fileOut = os.path.abspath('./test_moodle-bank-exemple.tex')
        fileRef = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "test/moodle-bank-exemple.tex"))

        print('============ Run test conversion ============')
        # create a quiz
        quiz = Quiz(fileIn)
        # convert it
        quiz.convert(fileOut, debug=False)

        print('=============== Check output ================')
        # check it (for convinience but too strict)
        equiv = check_hash(fileOut, fileRef)
        if equiv:
            print('> Converted XML is identical to the reference: OK')
        # test latex compilation
        status = quiz.compileLatex(fileOut)
        if status.returncode != 0:
            print('> pdflatex encounters Errors, see logs...')
        else:
            print('> pdflatex compile without Errors: OK')
        self.assertEqual(status.returncode, 0)





if __name__ == '__main__':
    # run unittest test suite
    print('> Running tests...')
    unittest.main()

