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
import argparse
import os
import sys

import amc2moodle as amdlpkg
from amc2moodle.amc2moodle import amc2moodle_class as a2m
from amc2moodle.utils.customLogging import customLogger


def run():
    """ Read command line input and run amc2mooodle conversion.
    """
    # Initialize command line parser with argparse
    # default values
    fileIn = None
    fileOut = None
    # deal with arguments
    parser = argparse.ArgumentParser(description='''This program converts a
                                     LaTeX file containing AMC questions into
                                     an XML file suitable for moodle import.
                                     Only 'question' and 'questionmult'
                                     environnements are now available.
                                     ''')

    parser.add_argument("inputfile",
                        help="Input TeX file (mandatory)")
    parser.add_argument("-o", "--output", nargs=1,
                        help="Output XML file (default inputfile.xml)",
                        required=False)
    parser.add_argument("-k", "--keep",
                        help='''Keep temporary file
                        (useful for debuging, optional)''',
                        required=False, action="store_true")
    parser.add_argument("-c", "--catname",  # nargs=1,
                        help='''Provide root category name (default 'amc').
                        Note that \\element{label} are used as
                        subcategory tag.''',
                        required=False, default='amc')
    parser.add_argument("-p", "--prettify",
                        help="Prettify the XML file using indent tool",
                        required=False, action="store_true")
    parser.add_argument("-n", "--notemp",
                        help='''No use of system temporary directory, use
                                input directory instead.''',
                        required=False, action="store_true")
    parser.add_argument("-V", "--version",
                        help='''Show the current version of moodle2amc''',
                        action="version",
                        version=f"%(prog)s v{amdlpkg.__version__}")
    parser.add_argument("-v", "--verbose",
                        help='''Show all log messages in CLI. Use -vv for more verbosity.''',
                        required=False, action="count",default=0)
    parser.add_argument("--no-log-file",
                        help='''Deactivate the log file.''',
                        required=False, action="store_false")
    parser.add_argument("-s", "--silent",
                        help='''Hide all messages in CLI (log file is still written) (override verbosity)''',
                        required=False, action="store_true")
    parser.add_argument("-x","--exp",
                        help='''Experimental features (clean XML...)''',
                        required=False, action="store_true")
    parser.add_argument("--disable-magic",
                        help='''Disable magic comments (default : enable).''',
                        required=False, default=False, dest='magic_flag',
                        action="store_true")
    parser.add_argument("--includestyles",
                        help='''Allow LaTeXML to load raw *.sty file (default : False).''',
                        required=False, default=False, dest='include_styles',
                        action="store_true")

    # Get input args
    args = parser.parse_args()

    if args.inputfile:
        fileIn = args.inputfile
    if args.output:
        fileOut = args.output[0]

    keepFlag = args.keep
    indentFlag = args.prettify
    tempDir = not args.notemp
    catname = args.catname
    magic_flag = not(args.magic_flag)
    silentMode = args.silent
    verboseMode = args.verbose
    cleanXML=args.exp
    logFileMode = args.no_log_file
    include_styles = args.include_styles

    #load logger
    logObj = customLogger('amc2moodle')
    logObj.setupConsoleLogger(verbositylevel=verboseMode,
                              silent=silentMode,
                              txtinfo=amdlpkg.__version__)

    # check input file
    fileInOk = False
    if fileIn is not None:
        fileInOk = os.path.exists(fileIn)

    # declare log file
    if fileInOk and logFileMode:
        logFile = os.path.splitext(os.path.basename(fileIn))[0]+'_amc2moodle.log'
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

    globalReturncode = 0
    # run conversion
    if fileInOk:
        a2m.amc2moodle(fileInput=fileIn, fileOutput=fileOut,
                       keepFlag=keepFlag, catname=catname,
                       indentXML=indentFlag, usetempdir=tempDir,
                       magic_flag=magic_flag, cleanXML=cleanXML,
                       include_styles=include_styles)
    else:
        # exit with error status
        globalReturncode = 1
    #info about the log
    if fileInOk and logFileMode:
        Logger.info(f"Log file of amc2moodle's run: {logFile}")

    # exit with error status
    sys.exit(globalReturncode)


# Run autonomous
if __name__ == '__main__':
    # run with options
    run()
