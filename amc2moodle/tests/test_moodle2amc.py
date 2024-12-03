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

from amc2moodle.utils.customLogging import customLogger
from amc2moodle.utils.misc import check_hash, decorator_set_cwd
from amc2moodle.moodle2amc import Quiz
import amc2moodle as amdlpkg
import os
import shutil
import unittest

# Load logger
logObj = customLogger("amc2moodle")
logObj.setupConsoleLogger(verbositylevel=2, silent=False, txtinfo=amdlpkg.__version__)
# Catch Logger
Logger = logObj.getLogger()

# payload data directory for running test
_PAYLOAD_TEST_DIR = os.path.join(os.path.dirname(__file__), "payload_test_moodle2amc")


# add an output directory for tests
_OUTPUT_TEST_DIR = os.path.abspath(os.path.join(os.getcwd(), "output_tests"))
# create output directory and switch working dir on it
os.makedirs(_OUTPUT_TEST_DIR, exist_ok=True)
# os.chdir(_OUTPUT_TEST_DIR)


# Silence other loggers
# for log_name, log_obj in logging.Logger.manager.loggerDict.items():
#     if "amc2moodle" not in log_name and "tests_a2m" not in log_name:
#         log_obj.disabled = True


class TestSuite(unittest.TestCase):
    """Define test cases for unittest.

    Before changing the reference xml file, please check they can be imported
    in [moodle sandbox](https://sandbox.moodledemo.net/login/index.php)
    teacher / sandbox

    """

    @decorator_set_cwd(_OUTPUT_TEST_DIR) # setting of cwd required for latex compilation
    def test_mdl_bank(self):
        """Tests if input XML file yields reference LaTeX file."""
        # define i/o file
        fileIn = os.path.abspath(
            os.path.join(_PAYLOAD_TEST_DIR, "moodle-bank-exemple.xml")
        )
        fileOut = os.path.abspath(
            os.path.join(_OUTPUT_TEST_DIR, "test_moodle-bank-exemple.tex")
        )
        fileRef = os.path.abspath(
            os.path.join(_PAYLOAD_TEST_DIR, "moodle-bank-exemple.tex")
        )

        # move sty's file to output dir
        src = os.path.abspath(os.path.join(_PAYLOAD_TEST_DIR, "automultiplechoice.sty"))
        dst = os.path.abspath(os.path.join(_OUTPUT_TEST_DIR, "automultiplechoice.sty"))
        shutil.copyfile(src, dst)

        Logger.info("============ Run test conversion ============")
        # create a quiz
        quiz = Quiz(fileIn)
        # convert it
        quiz.convert(fileOut, debug=False)

        Logger.info("=============== Check output ================")
        # check it (for convinience but too strict)
        equiv = check_hash(fileOut, fileRef)
        if equiv:
            Logger.info("> Converted XML is identical to the reference: OK")
        # test latex compilation
        status = quiz.compileLatex(fileOut)
        Logger.info("cwd {}".format(os.getcwd()))
        if status.returncode != 0:
            Logger.info("> pdflatex encounters Errors, see logs...")
        else:
            Logger.info("> pdflatex compile without Errors: OK")

        Logger.info("cwd {}".format(os.getcwd()))
        self.assertEqual(status.returncode, 0)


if __name__ == "__main__":
    # run unittest test suite
    Logger.info("> Running tests...")
    unittest.main()
