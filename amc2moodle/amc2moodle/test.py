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
from lxml import etree

# TODO complete test case for Numerical questions
# TODO Test XML Schema Definition

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


class TestSuiteNoTikz(unittest.TestCase):
    """ Define test cases for unittest based on test/QCM_wo-tikz.tex.

    This is the main part of the test. It test some key/value of the XML
    output file and that the global work finish normally.

    Before changing the reference XML file, please check they can be imported
    in [moodle sandbox](https://sandbox.moodledemo.net/login/index.php)

    teacher / sandbox

    """

    @classmethod
    def setUpClass(cls):
        """ Setup XML file from inpout tex (no tikz) for value checking.
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

        # open, parse and store the the converted file tree
        cls.tree = etree.parse(fileOut)
        #self.assertTrue(equiv, 'The converted file is different from the ref.')

    def question_fields(self, qname, target_ans_sum,
                        target_shuffleanswers='true', target_single='false'):
        """ Parse and test a question from the tree.

        Parameters
        ----------
        qname : string
            Name of the question in tex file.
        target_ans_sum : float
            Value of the target grade (deduce from the AMC scroring commands).
        target_shuffleanswers : string, optional
            Value of the 'suffleanswser' parameter. The default is 'true'.
        target_single : string, optional
            Value of the 'single' parameter. The default is 'false'.

        Returns
        -------
        ok : int
            Contains the number of test that fails, 0 means all test passed.

        """
        # If all matches are good, return 0, else return the number of fails.
        ok = -1
        TOL = 1e-5
        # loop over the test
        for q in self.tree.iterfind('question'):
            if q.attrib['type'] == 'multichoice':
                if q.find('name/text').text == qname:
                    # if there is a match, ok is now 0
                    ok += 1
                    # performed all tests
                    # Test shuffleanswers, should be 'false', ie keep order
                    sa = q.find('shuffleanswers').text
                    if sa != target_shuffleanswers:
                        ok += 1
                    # Test if single answer
                    single = q.find('single').text
                    if single != target_single:
                        ok += 1
                    # Test local scoring, eg local scoring m=-0.25, sum = 75
                    ans = q.findall('answer')
                    if ans:
                        s = 0.
                        frac_list = []
                        for a in ans:
                            frac = float(a.attrib['fraction'])
                            frac_list.append(frac)
                            s += frac
                        print('In {}, fraction are {}\n'.format(qname, frac_list))
                        if abs(s - target_ans_sum) > TOL:
                            ok += 1
                    else:
                        ok += 1
        return ok

    def test_name_Qmult_Aucune(self):
        """ Check specific element for question 'Qmult:Aucune'.
        """
        # question name
        qname = 'Qmult:Aucune'

        # Test shuffleanswers, should be 'false', ie keep order
        # Test local scoring, ie local scoring \bareme{e=-0.5,b=1,m=-1.,p=-0.5}
        # Test question multiple ie target_single='false'
        ok = self.question_fields(qname=qname,
                                  target_ans_sum=0,
                                  target_shuffleanswers='false',
                                  target_single='false')

        # the test is ok if ok==0
        self.assertEqual(ok, 0)

    def test_name_pref(self):
        """ Check specific element for question 'pref'.
        """
        # question name
        qname = 'pref'

        # Test shuffleanswers, should be 'true', ie shuffle (default)
        # Test local scoring, ie local scoring m=-0.25, sum = 75
        # Test question multiple ie target_single='false'
        ok = self.question_fields(qname=qname,
                                  target_ans_sum=75,
                                  target_shuffleanswers='true',
                                  target_single='false')
        # the test is ok if ok==0
        self.assertEqual(ok, 0)

    def test_name_QmultTabVerbMacro(self):
        """ Check specific element for question 'Qmult:TabVerbMacro'.
        """
        # question name
        qname = 'Qmult:TabVerbMacro'

        # Test shuffleanswers, should be 'true', ie shuffle (default)
        # Test local scoring, ie global scoring m=-0.25, sum = 75
        # Test question multiple ie target_single='false'
        ok = self.question_fields(qname=qname,
                                  target_ans_sum=75,
                                  target_shuffleanswers='true',
                                  target_single='false')
        # the test is ok if ok==0
        self.assertEqual(ok, 0)

    def test_itemizeEnumerate(self):
        """ Check specific element for question 'itemize-enumerate'.
        """

        # question name
        qname = 'itemize-enumerate'

        # Test shuffleanswers, should be 'true', ie shuffle (default)
        # Test local scoring, ie local scoring m=0,p=0, sum = 100
        # Test question single ie target_single='true'
        ok = self.question_fields(qname=qname,
                                  target_ans_sum=100,
                                  target_shuffleanswers='true',
                                  target_single='true')
        # the test is ok if ok==0
        self.assertEqual(ok, 0)


class TestSuiteOther(unittest.TestCase):
    """ Define test cases for unittest. Just check the process finish normally.

    Before changing the reference xml file, please check they can be imported
    in [moodle sandbox](https://sandbox.moodledemo.net/login/index.php)

    teacher / sandbox

    """

    def test_numerical(self):
        """ Tests if numerical questions yields reference xml file.
        """
        # define i/o file
        fileIn = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "test/numerical.tex"))
        fileOut = os.path.abspath('./test_numerical.xml')
        fileRef = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "test/numerical.xml"))
        # convert to xml
        a2m.amc2moodle(fileInput=fileIn,
                       fileOutput=fileOut,
                       keepFlag=False,
                       catname='test_num',
                       deb=0)
        # check it
        equiv = check_hash(fileOut, fileRef)
        if equiv:
            print(' > Converted XML is identical to the ref.')
        # self.assertTrue(equiv, 'The converted file is different from the ref.')

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
