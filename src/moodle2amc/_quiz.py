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

from lxml import etree
from xml.sax.saxutils import unescape
import subprocess
import os
from ._questions import *
from amc2moodle.utils.text import clean_q_name
import logging
from concurrent.futures import ThreadPoolExecutor


# output latex File
LATEX_FILEOUT = 'out.tex'
# xslt file
XSLT_TEXRENDERER = os.path.join(os.path.dirname(__file__), 'struc2tex.xslt')

# activate logger
Logger = logging.getLogger(__name__)

def writePipeOnOutput(process,streamIn,output):
    """ Write the stream from a pipe through an output
    during process executed by subprocess.Popen
    """
    while process.poll() is None:
        msg = streamIn.readline().strip()
        if msg !="":
            output(msg)
    # write the rest from the buffer
    msg = streamIn.read().strip()
    if msg !="":
        output(msg)

class Quiz:
    """ Define the quiz class.
    """

    def __init__(self, mdl_xml_file):
        """ Init the quiz from `mdl_xml_file` which can be :
              - a file name/path
              - a file object
              - a file-like object
        """
        parser = etree.XMLParser(encoding='utf-8', strip_cdata=False)
        self.mdl = etree.parse(mdl_xml_file, parser=parser)

    # @classmethod
    # def fromstring(cls, mdl_xml_str):

    def __repr__(self):
            """ Change string representation.
            """
            rep = "Instance of {}.".format(self.__class__.__name__)
            return rep

    def __str__(self):
        """ Change string representation to print the tree.
        """
        rep = self.__repr__()
        s = etree.tostring(self.mdl, pretty_print=True,
                           encoding='utf8').decode('utf8')
        return '\n'.join((rep, s))

    def convert(self, texfile=LATEX_FILEOUT, debug=False):
        """ Convert moodle quiz to LaTeX amc format.

        Parameters
        ----------
        texfile : string, optional
            Ouput latex path/filename. The default is LATEX_FILEOUT.
        debug : bool, optional
            Display additional outputs. The default is False.

        Returns
        -------
        None.

        """
        # convert : convert(to str) converttofile
        amc, cat_dict = self._reshape()
        if debug:
            Logger.debug(etree.tostring(amc, pretty_print=True,
                                 encoding='utf8').decode('utf-8'))
        tex = self.texRendering(amc)
        # remove document root
        tex_str = unescape(etree.tostring(tex, encoding='utf8')
                           .decode('utf-8')
                           .replace('<document>\n', '')
                           .replace('<document>', '')
                           .replace('</document>', '')
                           .replace('\n}', '}'))

        # Write document to file
        with open(texfile, 'w') as f:
            f.write(tex_str)

        # print ouput message
        self.output_msg()


    # TODO create a class quiz to encapsulate that
    def _latex_header(self):
        """ Define LaTeX header and newcommand.
        """
        # TODO : select fp only if QuestionNumerical instance ?
        header_text = r"""
        \documentclass[a4paper]{article}
        % -------------------------::== package ==::---------------------------
        \usepackage[utf8]{inputenc}
        \usepackage[T1]{fontenc}
        \usepackage{alltt}
        \usepackage{multicol}
        \usepackage{amsmath,amssymb}
        \usepackage{color}
        \usepackage{graphicx}
        % Mandatory for conversion
        \usepackage[francais,bloc,completemulti]{automultiplechoice}
        \usepackage{tikz}
        \usepackage{hyperref}
        \usepackage{ulem} % strike text
        % fp is needed by AMC for numerical question with float. Need to be commented for amc2moodle usage (fp is not yet supported)
        \usepackage{fp} 

        % -----------------------::== newcommand ==::--------------------------
        \newcommand{\feedback}[1]{}
        \begin{document}
        """.replace('        ','')
        header = etree.Element('header')
        header.text = header_text
        return header

    def _latex_footer(sel, cat_dict):
        """ Define LaTeX footer to populate a amc test from the question bank.
        """
        # store copy operation for all category
        group_list=[]
        exemplaire_text =r"""
        % ============================================================================
        \exemplaire{1}{    	% nombre de sujet différent

        % Replace with your Header
        \vspace*{.5cm}
        \begin{minipage}{.4\linewidth}
            \centering\large\bf Test
        \end{minipage}
        \champnom{\fbox{
            \begin{minipage}{.5\linewidth}
                Nom et prénom :

                \vspace*{.5cm}\dotfill
                \vspace*{1mm}
            \end{minipage}
        }}

        \begin{center}
          \Large{\textsc{An AMC quiz generated from moodle XML questions export}}\\
          \normalsize
        \end{center}

        % mélange et catégorie (groupe dans ACM)
        \cleargroup{allquestions}
        """.replace('        ','')
        enddocument = "\n\\end{document}"
        copy_group = "\\copygroup{%s}{allquestions}\n"

        # iterate over category
        for cat, number in cat_dict.items():
            if number > 0:
                group_list.append(copy_group % cat)

        melange = "% Shuffling is commented for testing\n" + \
                  "%\\melangegroupe{allquestions}\n" + \
                  "\\restituegroupe{allquestions}"

        footer_text = exemplaire_text + ''.join(group_list) + melange + '\n}' \
            + enddocument

        footer = etree.Element('footer')
        footer.text = footer_text
        return footer


    def _reshape(self):
        """ Reshape  moodle XML file into a stucture close to AMC Latex format.

        Parameters
        ----------
        root : etre.Element.tree
            An XML file parse by lxml.etre.

        Returns
        -------
        None.

        """

        root = self.mdl
        # initial default value for the category name
        catname = 'moodle'
        # store existing category in dict, Key=catname, value is the number of
        # question in this category
        cat_dict = dict()

        # create new etree that will contains new xml suitable for amc.
        # the roots node is document as for a tex file
        amc = etree.Element('document')

        # add header
        header = self._latex_header()
        amc.append(header)

        # start from quizz
        for question in root.findall('question'):
            # get type of Question
            qtype = question.attrib['type']
            # check if question is a category
            if question.attrib['type'] == 'category':
                mdl_catname = question.find('category/text').text
                # create a simpler catname for amc
                catname = '-'.join(mdl_catname.split('/')[1:])
                # sanitize catname (remove %)
                catname = catname.replace('%', 'perc. ')
                # Remove accent and non ascii chars for amc compatibility
                catname = clean_q_name(catname)
                # store name and say no question in it for now
                cat_dict.update({catname: 0})
            else:
                # Standard question
                # qname can be in CDATA or not. '.text' works for both.
                qname = question.find('name/text').text
                # Remove accent and non ascii chars for amc compatibility  (just for logging here)
                # for tex conversion, it is done in Question __init__
                qname = clean_q_name(qname)
                if qtype in SUPPORTED_QUESTION_TYPE:
                        Logger.debug("> Reshape question '{}' of type '{}'.".format(qname, qtype))
                        # if no encounter category name before this question,
                        # add the defaut catname in the cat_dict
                        if not(cat_dict):
                            cat_dict.update({catname: 0})
                        # there is one more question in the catname categogy
                        cat_dict[catname] += 1
                        amc_q = CreateQuestion(qtype, question).transform(catname)
                        amc.append(amc_q)
                else:
                    Logger.error("> Question '{}' of type '{}' is not supported. Skipping.".format(qname, qtype))

        Logger.info('> done.')

        # add footer
        footer = self._latex_footer(cat_dict)
        amc.append(footer)

        return amc, cat_dict

    @staticmethod
    def texRendering(amc):
        """ Apply xslt tranformation for final step of tex conversion.

        Parameters
        ----------
        amc : etre.Element
            XML structure object describing the .

        Returns
        -------
        tex : XSLT results object
            Contain an intermediate state of the conversion process.
        """
        # create XSLT transformation fonction
        xslt_texrenderer = XSLT_TEXRENDERER
        texrenderer = etree.XSLT(etree.parse(xslt_texrenderer))
        tex = texrenderer(amc)

        return tex

    @staticmethod
    def compileLatex(latexFile):
        """ Compile output with pdflatex.

        Parameters
        ----------
        latexFile : string
            full name of a latex file.
        """
        command = "pdflatex -interaction=nonstopmode -halt-on-error -file-line-error {}".format(latexFile)
        #TODO: caution with 'universal_newlines=' (new syntax from Python 3.7: text=)
        Logger.debug('Run command {}'.format(command))
        with subprocess.Popen(command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True) as latexProcess:
            #while latexProcess.poll() is None:
            #    Logger.debug(latexProcess.stdout.read())
            #writePipeOnOutput(latexProcess,latexProcess.stderr,Logger.debug)

            # write stdout and stderr in parallel to the right logging outputs
            # caution pdflatex uses only STDOUT...
            # all outputs will be written in debug log
            with ThreadPoolExecutor(2) as pool:
                rstdout = pool.submit(writePipeOnOutput,
                        latexProcess,
                        latexProcess.stdout,
                        Logger.debug)
                rstderr = pool.submit(writePipeOnOutput,
                        latexProcess,
                        latexProcess.stderr,
                        Logger.debug)
                rstdout.result()
                rstderr.result()
        
        # status = subprocess.run(command.split(),
        #                         stdout=subprocess.DEVNULL)
        return latexProcess

    @staticmethod
    def output_msg():
        """ Print ouput message.
        """
        # Summary of logged events in convert.py only
        log_msg = "> Found {} Warnings and {} Errors during conversion (see above)."
        # Needto sum from _questions.py and _quiz.py
        quest_log = logging.getLogger('amc2moodle.moodle2amc._questions')        
        warn_number = quest_log.counter['warning'] + Logger.counter['warning']
        err_number = (quest_log.counter['error'] + Logger.counter['error']
                      + quest_log.counter['critical'] + Logger.counter['critical'])
        Logger.info(log_msg.format(warn_number, err_number))

        msg = """ The conversion is complete. Try to compile the tex file...
                In case of trouble, you may need to check for :
                - unicode character like euro € currency symbol  
                - latex special character like '{', '_', '&', ... 
                - possible problems with embedded 'equation' environnement inside matjax delimiters:
                  ex :  $$\\begin{equation}... Remove '$$' in output TeX file
                - strange html tags
                - check the scoring
                - ..."""
        for item in msg.split('\n'):
            Logger.info(item)

