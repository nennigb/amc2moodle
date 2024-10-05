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

import unicodedata
import re


def remove_accent(s):
    """Remove all accent or special chars from an input utf-8 string.

    It first convert unicode string into the 'canonical form' NFKD that translates each
    accentuated character into its decomposed form.
    Based on Python cookbook 2.9
    """
    nfkd_form = unicodedata.normalize('NFKD', s)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def remove_non_ascii(s):
    """Remove all non ascii symbol from an utf8 string.
    """
    # define few european non ascii char
    remap = {ord('œ'): 'oe',
             ord('Œ'): 'OE',
             ord('æ'): 'ae',
             ord('Æ'): 'AE',
             ord('€'): ' Euros',
             ord('ß'): 'ss',
             ord('¿'): '?'}
    # and replace them, other will be ignored
    out = s.translate(remap)

    return out


def remove_non_alphanum(s):
    """ Remove all non alphanum char to conform to AMC.
    """
    # keep only alphanum, spaces, ':' and '-'
    out = re.sub(r'[^0-9a-zA-Z:\-]+', ' ', s)
    return out


def clean_q_name(s):
    r""" Cleanup a string to conformed to AMC labels.

    # AMC doc
    Il faut utiliser un identifiant différent pour chaque question.
    Un identifiant peut être constitué de chiffres, lettres et caractères
    simples (ne pas utiliser le caractère souligné _, les accolades,
    crochets, par exemple !). Il ne faut pas utiliser d’identifiants se
    terminant par un nombre entier entre crochets (comme marine-marchande[2]
    ou 123[27] ), car cette forme d’identifiants est réservée à la saisie de
    longs codes (par exemple grâce à \AMCcodeGrid - voir Section 5.4.14).
    """

    out = remove_accent(s)
    out = remove_non_ascii(out)
    out = remove_non_alphanum(out)

    return out.strip()
