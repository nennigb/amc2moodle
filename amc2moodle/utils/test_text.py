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

import amc2moodle.utils.text as text
import unittest

# Run by utils.test 
class TestText(unittest.TestCase):
    """ Define calculated question parser test cases for unittest.
    """
    @classmethod
    def setUpClass(cls):
        print('\n> Tests of ', cls.__name__)

    def setUp(self):
        """ Define the test cases.
        """
        # Define the [input, output] for each test cases
        self.case = {'accent': ['óëàéèïí', 'oeaeeii'],                   # check for accents
                     'non_ascii': ['œæÆß€¿Œ', 'oeaeAEss Euros?OE'],      # check for non ascii (without accent)
                     'non_alphanum': ['Label:a/b@[c]%-2', 'Label:a b c -2'],  # check for non letter
                     'label': ['Làbêl:a/b@[cœ]%', 'Label:a b coe'],      # check label
                     }

    def test_remove_accent(self):
        """ Remove accents.
        """
        out = text.remove_accent(self.case['accent'][0])
        self.assertEqual(out, self.case['accent'][1])

    def test_remove_non_ascii(self):
        """ Remove_non_ascii.
        """
        out = text.remove_non_ascii(self.case['non_ascii'][0])
        self.assertEqual(out, self.case['non_ascii'][1])

    def test_remove_non_alphanum(self):
        """ Remove non letter.
        """
        out = text.remove_non_alphanum(self.case['non_alphanum'][0])
        self.assertEqual(out, self.case['non_alphanum'][1])

    def test_clean_q_name(self):
        """ Global cleaning.
        """
        out = text.clean_q_name(self.case['label'][0])
        self.assertEqual(out, self.case['label'][1])


if __name__ == '__main__':
    # run unittest test suite
    unittest.main()
