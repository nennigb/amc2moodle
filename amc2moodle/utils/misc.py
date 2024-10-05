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

import hashlib

def check_hash(file1, file2):
    """ Return the md5 sum after removing all withspace.

    Parameters
    ----------
    file1, file2 : string
        Filenames of files to check.

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