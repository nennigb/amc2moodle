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
import amc2moodle as amdlpkg
import amc2moodle.moodle2amc as mdl2amc
import argparse
import os
import sys
import logging


def run():
    """ Read command line input and run mdl2amc conversion.
    """
    # Initialize command line parser with argparse
    # default values
    fileIn = None
    fileOut = None
    debug = False
    # deal with arguments
    parser = argparse.ArgumentParser(description='''This program converts a
                                     XML file containing moodle questions into
                                     an automultiplechoice LaTeX file.''')

    parser.add_argument("inputfile",
                        help="Input moodle XML file (mandatory)")
    parser.add_argument("-o", "--output",
                        help="Output XML file (default inputfile.tex)",
                        required=False)
    parser.add_argument("--fig",
                        help='''figures folder name (default Figures not yet
                        implemented)''',
                        required=False)
    parser.add_argument("--check",
                        help='''Check if LaTeX output compile (optional)''',
                        required=False, action="store_true")
    parser.add_argument("-V","--version",
                        help='''Show the current version of moodle2amc''',
                        action="version",
                        version="%(prog)s v{version}".format(version=amdlpkg.__version__))
    parser.add_argument("-v", "--verbose",
                        help='''Show all log messages in CLI. Use -vv for more verbosity.''',
                        required=False, action="count",default=0)
    parser.add_argument("--no-log-file",
                        help='''Deactivate the log file.''',
                        required=False, action="store_false")
    parser.add_argument("-s", "--silent",
                        help='''Hide all messages in CLI (log file is still written) (override verbosity)''',
                        required=False, action="store_true")
    # parser.add_argument("-c", "--catname",  # nargs=1,
    #                     help='''Provide root category name (default 'amc').
    #                     Note that \\element{label} are used as
    #                     subcategory tag.''',
    #                     required=False, default='amc')

    # Get input args
    args = parser.parse_args()

    if args.inputfile:
        fileIn = args.inputfile
    if args.output:
        fileOut = args.output
    
    silentMode = args.silent
    verboseMode = args.verbose
    logFileMode = args.no_log_file

    #load logger
    logObj = customLogger('amc2moodle')
    logObj.setupConsoleLogger(verbositylevel=verboseMode,
                              silent=silentMode,
                              txtinfo=amdlpkg.__version__)    


    # check input file
    fileInOk = os.path.exists(fileIn)

    # declare log file
    if fileInOk and logFileMode:
        logFile = os.path.splitext(os.path.basename(fileIn))[0]+'_moodle2amc.log'
        # remove existing log file
        if os.path.exists(logFile):
            os.remove(logFile)
        # create file logger
        logObj.setupFileLogger(filename=logFile,
                               verbositylevel=2,
                               txtinfo=amdlpkg.__version__)
    #catch Logger
    Logger = logObj.getLogger()

    if fileInOk:
        Logger.debug('Input file: %s - status: %s' % (fileIn, "OK"))
    else:
        Logger.critical('Input file: %s - status: %s' % (fileIn, "does not exist"))
    if fileOut:
        fileOutOk = not os.path.exists(fileOut)
        if fileOutOk:
            Logger.debug('Output file: %s - status: Ok' % fileOut)
        else:
            Logger.warning('Output file: %s - status: Already exists (will be overwritten)' % fileOut)
    else:
        fileOut = os.path.splitext(fileIn)[0] + '.tex'
        Logger.info('Output file: %s - will be created.' % fileOut)

    globalReturncode = 0
    # run conversion
    if fileInOk:
        Logger.info('============ Run conversion ============')
        # create a quiz
        quiz = mdl2amc.Quiz(fileIn)
        # convert it
        quiz.convert(fileOut, debug)
        # test latex compilation
        if args.check:
            Logger.info('============ Check output ==============')
            status = quiz.compileLatex(fileOut)
            if status.returncode != 0:
                Logger.error('> pdflatex encounters Errors...')
                globalReturncode = status.returncode
            else:
                Logger.info('> pdflatex compile without Errors... OK')
    else:
        globalReturncode = 1
    #info about the log
    if fileInOk  and logFileMode:
        Logger.info("Log file of moodle2amc's run: {}".format(logFile))
    # exit with error status
    sys.exit(globalReturncode)
    


# Run autonomous
if __name__ == '__main__':
    # run with options
    run()
