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

from amc2moodle.utils.calculatedParser import *
from io import StringIO
import unittest
from unittest.mock import patch
# import also text test
from amc2moodle.utils.test_text import *


class TestSuiteCalculatedParserToFP(unittest.TestCase):
    """ Define calculated question parser test cases for unittest.
    """

    def setUp(self):
        """ Define the test cases.
        """
        # # define the [moodle input, the expected latex output, warning msg]
        self.expr =[['nothing', 'nothing', ''],  # variable
                    ['var {x}', r'var \FPprint{\x }', ''],  # variable
                    ['var {x_y}', r'var \FPprint{\xy }', ''],  # variable with '_'
                    ['var {x1}', r'var \FPprint{\x1 }', 'Warning'],  # variable with '_'
                    ['var {x} and {y} end.', r'var \FPprint{\x } and \FPprint{\y } end.', ''],  # 2 variables
                    ['Embedded Eq. {=1+1} = 2', r'Embedded Eq. \FPprint{\FPeval{\out}{clip(1+1)}\out} = 2', ''],  # eq inside text
                    ['{=sqrt(3)}', r'\FPprint{\FPeval{\out}{clip(root(2, 3))}\out}', ''],  # sqrt -> root(2,...)
                    ['{=(1.0 + pow(2, 3)/2)}', r'\FPprint{\FPeval{\out}{clip((1.0+pow(3,2)/2))}\out}', ''],  # pow -> pow(2,...)
                    ['{=pow(2, 0.5)}', r'\FPprint{\FPeval{\out}{clip(pow(0.5,2))}\out}', ''],  # pow for roots 1.414213562373095042
                    ['{=pow(0.5+1.5, 0.5)}', r'\FPprint{\FPeval{\out}{clip(pow(0.5,0.5+1.5))}\out}', ''],  # test expr in swap 1.414213562373095042
                    ['{=-({x}-{y})}', r'\FPprint{\FPeval{\out}{clip(neg((\x -\y )))}\out}', ''],  # - unary
                    ['{=-1.2e-3}', r'\FPprint{\FPeval{\out}{clip(-0.0012)}\out}', ''],  # float
                    ['{=2*(((1-2)*(1+2))/(1+pi()))}', r'\FPprint{\FPeval{\out}{clip(2*(((1-2)*(1+2))/(1+\FPpi)))}\out}', ''],  # nested + pi()
                    ['{=max(3, 2) + 2*2}', r'\FPprint{\FPeval{\out}{clip(max(3,2)+2*2)}\out}', ''],  # function of 2 variables 7
                    ['{=log(log(2) + 2)}', r'\FPprint{\FPeval{\out}{clip(ln(ln(2)+2))}\out}', ''],  # nested log function 0.990710465347531441
                    ['{=log(log(2) + 2}', r'{=log(log(2) + 2}', ''],  # Miss formed, parser skip
                    ['{=xyz(2)}', r'\FPprint{\FPeval{\out}{clip(xyz(2))}\out}', 'Unsupported'],  # Miss formed, parser skip
                    ['{=expm1(2)}', r'\FPprint{\FPeval{\out}{clip(expm1(2))}\out}', 'Unsupported'],  # Miss formed, parser skip
                    # Embedded LaTeX equation in XML may leads to problems (because of braces)
                    # Remove standard mathjax delimiters from 'variable' parsing,
                    # In mathjax equation environnement inside delimiters is correct
                    [r'$$\begin{equation}\int x dx =3\end{equation}$$ {=sin({x}+1)}',
                     r'$$\begin{equation}\int x dx =3\end{equation}$$ \FPprint{\FPeval{\out}{clip(sin(\x +1))}\out}',''], # $$ ... $$
                    [r'\(\begin{equation}\int x dx =3\end{equation}\) {=sin({x}+1)}',
                     r'\(\begin{equation}\int x dx =3\end{equation}\) \FPprint{\FPeval{\out}{clip(sin(\x +1))}\out}',''], #\( ... \)
                    [r'\[\begin{equation}\int x dx =3\end{equation}\] {=sin({x}+1)}',
                     r'\[\begin{equation}\int x dx =3\end{equation}\] \FPprint{\FPeval{\out}{clip(sin(\x +1))}\out}',''], #\[ ... \[)]
                    [r'\[\begin{equation}\int x dx =3\end{equation}\] {x}',
                     r'\[\begin{equation}\int x dx =3\end{equation}\] \FPprint{\x }',''] #\[ ... \[)] + var
                    ]

    def test_render(self):
        """ Tests if input XML file yields reference LaTeX file and warning are
        printed.
        """
        print('\n> Tests of' , self.__class__.__name__)
        # Create the parser
        parser = CreateCalculatedParser('xml2fp')
        for e, ref, expectedwarn in self.expr:
            print("Expr = {} -> {}".format(e, ref))
            # mock out std ouput for testing
            with patch('sys.stdout', new=StringIO()) as fake_out:
                # parse answer
                out = parser.render(e)
                # check for the expected conversion
                self.assertEqual(out, ref)
                # check for expected warnings
                # As '' belong to all strings
                warn = fake_out.getvalue()
                if warn:
                    self.assertIn(expectedwarn, warn)



class TestSuiteCalculatedParserFromFP(unittest.TestCase):
    """ Define AMC/FP question parser test cases for unittest.
    """

    def setUp(self):
        """ Define the test cases.
        """
        # # define the [moodle input, the expected latex output, warning msg]
        self.expr =[['nothing', 'nothing', ''],  # nothing to parse
                    ['blabla fp{rand1} bla', r'blabla {={rand1}} bla', ''],  # variable
                    ['fp{root(2, 3)}', r'{=sqrt(3)}', ''],  # root(2,...)-> sqrt
                    ['fp{root(1+1, 3)}', r'{=pow(3,1/(1+1))}', ''],  # root(2,...)-> pow if not 2
                    ['fp{ln(pi)}', r'{=log(pi())}', ''],  # ln -> log
                    ['fp{clip(1+rand0*(10-1))}', r'{=(1+{rand0}*(10-1))}', ''], # clip is skipped (print only)
                    ['fp{neg(neg(1+2))}', r'{=-(-(1+2))}', ''], # check 'neg'
                    ['fp{(arctan(1.2)+arcsin(3))/(arccos((pi+rand2)/2))}', r'{=(atan(1.2)+asin(3))/(acos((pi()+{rand2})/2))}', ''],  # ln -> log
                    ['fp{xyz(2)}', r'{=xyz(2)}', 'Unsupported'],  # Miss formed, parser skip
                   ]

    def test_render(self):
        """ Tests if input XML file yields reference LaTeX file and warning are
        printed.
        """
        print('\n> Tests of', self.__class__.__name__)
        # Create the parser
        parser = CreateCalculatedParser('fp2xml')
        for e, ref, expectedwarn in self.expr:
            print("Expr = {} -> {}".format(e, ref))
            # mock out std ouput for testing
            with patch('sys.stdout', new=StringIO()) as fake_out:
                # parse answer
                out = parser.render(e)
                # check for the expected conversion
                self.assertEqual(out, ref)
                # check for expected warnings
                # As '' belong to all strings
                warn = fake_out.getvalue()
                if warn:
                    self.assertIn(expectedwarn, warn)


if __name__ == '__main__':
    # run unittest test suite
    print('> Running utils submodule tests...')
    unittest.main()
