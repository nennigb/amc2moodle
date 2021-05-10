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

Based on https://github.com/johnjosephhorton/flatex, refactored and modified to
remove magic comments for amc2moodle.

Copyright, 2015, John J. Horton (john.joseph.horton@gmail.com)
Distributed under the terms of the GNU General Public License
See http://www.gnu.org/licenses/gpl.txt for details.
"""

import os
import re
import logging

# activate logger
Logger = logging.getLogger(__name__)

class Flatex:
    """ Merge all included tex files in one and remove magic comments.
    """

    def __init__(self, base_file, output_file,
                 noline=False, magic_flag=True):
        """ Create a new Flatex instance.

        Parameters
        ----------
        base_file : string
            Input tex filename.
        output_file : string
            Output tex file name.
        noline : bool, optional
            Add blank line after include/input. The default is False.
        magic_flag : bool, optional
            Remove or not the magic comment tag.

        Returns
        -------
        None.

        """
        # store
        self.base_file = base_file
        self.output_file = output_file
        self.noline = noline
        self.magic_flag = magic_flag

        # define the tag used to prefix the 'magic comments'
        self.magictag = '%amc2moodle '

        # define state variable for log
        self._magic_comments_number = 0
        self._included_files_list = [base_file]

    @staticmethod
    def is_input(line):
        """
        Determines whether or not a read in line contains an uncommented out
        \input{} statement. Allows only spaces between start of line and
        '\input{}'.
        """
        # tex_input_re = r"""^\s*\\input{[^}]*}""" # input only
        # match 'input' or 'include'
        tex_input_re = r"""(^[^\%]*\\input{[^}]*})|(^[^\%]*\\include{[^}]*})"""
        return re.search(tex_input_re, line)

    @staticmethod
    def get_input(line):
        """ Gets the file name from a line containing an input statement.
        """
        tex_input_filename_re = r"""{[^}]*"""
        m = re.search(tex_input_filename_re, line)
        return m.group()[1:]

    def magic_filter(self, line):
        """ Remove magic tag from a line.
        """
        return line.replace(self.magictag, '')

    @staticmethod
    def combine_path(base_path, relative_ref):
        """ Return the absolute filename path of the included tex file.
        """
        # check for absolute path
        if not(os.path.isabs(relative_ref)):
            abs_path = os.path.join(base_path, relative_ref)
        else:
            abs_path = relative_ref
        # Handle if .tex is supplied directly with file name or not
        if not relative_ref.endswith('.tex'):
            abs_path += '.tex'

        return abs_path

    def expand_file(self, base_file, current_path):
        """
        Recursively-defined function that takes as input a file and returns it
        with all the inputs replaced with the contents of the referenced file.
        """
        output_lines = []
        with open(base_file, "r") as f:
            for line in f:
                # test if it contains an '\include' or '\input'
                if self.is_input(line):
                    new_base_file = self.combine_path(current_path,
                                                      self.get_input(line))
                    output_lines += self.expand_file(new_base_file, current_path)
                    self._included_files_list.append(new_base_file)
                    if self.noline:
                        pass
                    else:
                        # add a new line after each inclided file
                        output_lines.append('\n')
                # test if magic coment
                elif self.magic_flag and line.lstrip().startswith(self.magictag):
                    output_lines += self.magic_filter(line)
                    # count it
                    self._magic_comments_number += 1
                # else append line
                else:
                    output_lines.append(line)

        return output_lines

    def expand(self):
        """ This "flattens" a LaTeX document by replacing all \\input{X} lines
        with the text actually contained in X.
        """
        current_path = os.path.split(self.base_file)[0]
        with open(self.output_file, "w") as g:
            g.write(''.join(self.expand_file(self.base_file,
                                             current_path)))
        return 0

    def report(self):
        """ Print log info about the expansion.
        """
        if self._magic_comments_number > 0:
            Logger.info('  {0} magic comments found, in {1} tex files.'.format(
                self._magic_comments_number,
                len(self._included_files_list)))
