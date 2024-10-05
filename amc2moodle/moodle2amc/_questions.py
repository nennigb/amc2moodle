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

__all__ = ['Question', 'QuestionMultichoice',
           'QuestionEssay', 'QuestionDescription',
           'QuestionNumerical', 'QuestionCalculatedMulti',
           'SUPPORTED_QUESTION_TYPE', 'CreateQuestion']

from lxml import etree
from xml.sax.saxutils import unescape
import base64
import os
from abc import ABC, abstractmethod
from wand.image import Image
# decode filemame unsed in moodle
import urllib
import math
import sys
from ..utils.calculatedParser import *
from amc2moodle.utils.text import clean_q_name
import markdown
import logging

# list of supported moodle question type for
SUPPORTED_QUESTION_TYPE = {'multichoice', 'essay', 'description',
                           'numerical', 'calculatedmulti'}

# possible to use several grading strategy
GRADING_STRATEGY = 'std'  # good/wrong no specific grading

# define path for images files
FIGURES_PATH = "./Figures"
# File type supported by latex (pdflatex), possible to add eps with eps2pdf
# but eps is unusal in web app.
LATEX_EXT = {'.pdf', '.png', '.jpg', '.jpeg'}
# prefered format for non supported img file
LATEX_IMG_OUT = '.png'
# output latex File
LATEX_FILEOUT = 'out.tex'

# labels for choices in AMCOpen
CORRECT_LABEL = 'OK'
WRONG_LABEL = 'F'

# Default parameters for numerical Questions
DECIMAL = 0      # minimal number of decimal
SIGN = False     # use sign in AMC
DIGIT = 1        # minimal number of digit
SCOREEXACT = 1   # default grade in AMC is 2, 1 in moodle
EPS = 10*sys.float_info.epsilon  # float precision to avoid log singularity

# Add set for True or false string
TRUE = {'true', '1'}
FALSE = {'false', '0'}
# Default parameters for calculated Questions
CALCULATED_DEFAULT_PARSER = 'xml2fp'

# activate logger
Logger = logging.getLogger(__name__)
class Question(ABC):
    """ Define an absract class for all supported questions.
    """
    _xslt_html2tex = os.path.join(os.path.dirname(__file__),
                                  'html2tex.xslt')
    _transform = etree.XSLT(etree.parse(_xslt_html2tex))
    figpath = FIGURES_PATH

    # possible numerics, open
    def __init__(self, q):
        """ Init class from an etree Element.
        """
        self.q = q
        # Remove accent and non ascii chars for amc compatibility
        self.name = clean_q_name(q.find('name/text').text)
        self.qtype = None
        self.fileCreated = []
        self.gStrategy = GRADING_STRATEGY
        # save number of svg file per question
        self.svg_id = 0

    def __repr__(self):
        """ Change string representation.
        """
        rep = ("Instance of {} containing the question '{}'."
               .format(self.__class__.__name__, self.name))
        return rep

    def __str__(self):
        """ Change string representation to print the tree.
        """
        rep = self.__repr__()
        s = unescape(etree.tostring(self.q, pretty_print=True,
                                    encoding='utf8').decode('utf8'))
        return '\n'.join((rep, s))

    @classmethod
    def fromstring(cls, qstring):
        """ Create an instance of QuestionX from a XML string.
        """
        q = etree.fromstring(qstring)
        return cls(q)

    def format2tex(self, cdata_content, text_format):
        """ Convert `cdata_content` with `text_format` format into tex.

        'html', 'plain_text', 'moodle_auto_format' are treated in the same way
        since plain text is recommanded to put raw html.
        'markdown' require a specific preprocessing.

        """

        if text_format in ('html', 'plain_text', 'moodle_auto_format'):
            text = self.html2tex(cdata_content)
        elif text_format == 'markdown':
            # First convert markdown into html and
            cdata_content = (cdata_content.replace('<text><![CDATA[', '')
                                          .replace(']]></text>', ''))
            cdata_content = markdown.markdown(cdata_content,
                                              extensions=['extra'])
            text = self.html2tex(unescape('<text>' + cdata_content + '</text>'))
        else:
            Logger.warning("> Unsupported format '{}'. Try with html filter.".format(text_format))
            text = self.html2tex(cdata_content)
        return text

    def html2tex(self, cdata_content):
        """ Convert CDATA field into latex text.

        Parameter
        ---------
        cdata_content : string
            CDATA protected content that will be parsed.

        Return
        ------
        tree_content : etree.Element
            the text content in html store as a etree.

        Remarks
        -------
        <br> are removed (not exml content).
        """
        # remove manually CDATA from the string
        # FIXME use .text and etree.CDATA(new_text)
        cdata_content = (cdata_content.replace('<text><![CDATA[', '<text>')
                         .replace('%', '\%')
                         .replace(']]></text>', '</text>')
                         .replace('<br>', ''))

        parser = etree.HTMLParser(recover=True)
        tree_content = etree.fromstring(cdata_content, parser)
        # tree_content = etree.fromstring(unescape(cdata_content), parser)
        self._img_check(tree_content)

        # transform with XSLT into XSLT (tree) for all other element
        xslt_content = self._transform(tree_content)
        # convert to XML (more suitable for search)
        tree_text = etree.XML(etree.tostring(xslt_content,
                              encoding='utf8').decode('utf-8'))
        return tree_text

    def _img_check(self, tree_content):
        """ Change path and check/convert to latex supported image type.

        there is 2 steps : i) extract svg, ii) convert file non supported by
        LaTeX

        Parameters
        ----------
        tree_content : etree
            etree arising from cdata parsing.
        """
        # Step 1.
        # Remove embedded svg file (tikz) and convert to img
        for svg in tree_content.findall('.//picture/svg'):
            width = svg.attrib['width']
            filename_svg = os.path.join(self.figpath,
                                        self.name + str(self.svg_id) + '.svg')
            with open(filename_svg, 'w') as f:
                f.write(etree.tostring(svg, encoding='utf8', pretty_print=True)
                        .decode('utf-8'))
            img_svg = etree.Element('img', attrib={'src': filename_svg,
                                                   'width': width})
            svg.getparent().append(img_svg)
            svg.getparent().remove(svg)
            # increment svg_id
            self.svg_id += 1

            # <picture> is then parsed in html2tex

        # Step 2.
        # check that img file are supported by LaTeX
        for img in tree_content.findall('.//img'):
            src = img.attrib['src']
            # remove percent-encoding with urlib
            src = urllib.parse.unquote(src)
            path, filename = os.path.split(src)
            basename, ext = os.path.splitext(filename)
            # need to be converted
            if ext not in LATEX_EXT:
                im = Image(filename=os.path.join(self.figpath, filename))
                fileout = os.path.join(self.figpath, basename + LATEX_IMG_OUT)
                im.save(filename=fileout)
                im.close()
                src = fileout
            else:
                src = os.path.join(self.figpath, filename)
            # store new path/file
            img.attrib['src'] = src

    def fileExport(self):
        """ Extract embedded data to 'real' file for LaTeX processing.
        """
        # extract all file in the quetsion recurssively
        for file in self.q.findall('.//file'):
            filename = file.attrib['name']
            data = base64.decodebytes(file.text.encode())
            # create directory if needed
            if not os.path.exists(self.figpath):
                os.makedirs(self.figpath)
            # save file
            with open(os.path.join(self.figpath, filename), 'bw') as f:
                f.write(data)
                self.fileCreated.append(filename)

    def question(self):
        """ Get question text.
        """
        # check for question format (markdown, html, text)
        text_format = self.q.find('questiontext').attrib['format'].lower()
        cdata_content = etree.tostring(self.q.find('questiontext/text'),
                                       encoding='utf8').decode('utf-8')
        text = self.format2tex(cdata_content, text_format)
        return text

    @abstractmethod
    def gettype(self):
        """ Determine the amc question type.
        """
        pass

    @abstractmethod
    def answers(self):
        """ Create and parse answers.
        """
        pass

    def transform(self, catname):
        """ Main routine, applied the xml transformation.
        """
        # initialize
        amcq = etree.Element('question', attrib={'amctype': self.gettype(),
                                                 'category': catname,
                                                 'qname': self.name})
        self.fileExport()
        qtext = self.question()
        amcq.append(qtext)
        choices = self.answers()
        # append if there is choices (eg description)
        if choices != None:
            amcq.append(choices)

        return amcq


class QuestionMultichoice(Question):
    """ Multiple choice question (question or questionmult)
    """

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        super().__init__(q)
        self.q = q
        self.qtype = 'multiplechoice'

    def gettype(self):
        """ Determine the amc question type.
        """
        # test if question or questionmult
        single = self.q.find('single').text
        if single.lower() == 'true':
            amcqtype = 'question'
        elif single.lower() == 'false':
            amcqtype = 'questionmult'
        else:
            Logger.error("> Unknwon question type in '{}'".format(self.name))

        return amcqtype

    def answers(self):
        """ Create and parse answers.
        """
        amc_choices = etree.Element('choices')
        # loop over all answers
        for i, ans in enumerate(self.q.findall('.//answer')):
            # Get format for parsing (CDATA) is needed
            text_format = ans.attrib['format'].lower()
            # TODO how to integrate the scoring aspect
            if self.gStrategy == 'std':
                # the fraction (scoring) field is not allways at the same place
                try:
                    fraction = ans.find('fraction').text
                except:
                    try:
                        fraction = ans.attrib['fraction']
                    except:
                        raise ValueError('fraction not found.')
                if float(fraction) > 0:
                    tag = 'correctchoice'
                else:
                    tag = 'wrongchoice'
            amc_ans = etree.Element(tag, attrib={'order': str(i)})
            # parse answer text
            cdata_content = etree.tostring(ans.find('text'), encoding='utf8').decode('utf-8')
            text = self.format2tex(cdata_content, text_format)
            amc_ans.append(text)
            # store in a list
            amc_choices.append(amc_ans)

        return amc_choices



class QuestionEssay(Question):
    """ Essai choice question (AMCopen)
    """

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        super().__init__(q)
        self.q = q
        self.qtype = 'essai'

    def gettype(self):
        """ Determine the amc question type.
        """
        amcqtype = 'question'

        return amcqtype

    def answers(self):
        """ Create and parse answers.
        """
        nlines = self.q.find('responsefieldlines').text
        amc_open = etree.Element('open', attrib={'nlines': str(nlines)})
        # loop over all answers

        if self.gStrategy == 'std':
            # Create 2 possible answers 0, or 100%
            # perhaps create an options for more details, but perhaps more
            # simple to fix that directly in amc
            amc_good = etree.Element('correctchoice', attrib={'label': CORRECT_LABEL})
            etree.SubElement(amc_good, "text").text = CORRECT_LABEL

            amc_wrong = etree.Element('wrongchoice', attrib={'label': WRONG_LABEL})
            etree.SubElement(amc_wrong, "text").text = WRONG_LABEL
            # answers are embedded into open element, for parsing the box
            amc_open.append(amc_good)
            amc_open.append(amc_wrong)
        else:
            raise NotImplementedError()

        # print(etree.tostring(amc_open).decode())
        return amc_open

class QuestionNumerical(Question):
    """ Multiple choice question (question or questionmult).

    Whereas Moodle, AMC does not support multiple answer for numerical
    questions, excepted to
        - yield different grade if the rounding is too loose
    The following behaviors are ignored:
        - catch classical wrong answer for feedback
        - support for multiple solution to a problem eg. modulo 2pi
    The unit handling is not supported.
    """

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        super().__init__(q)
        self.q = q
        self.qtype = 'numerical'

    def gettype(self):
        """ Determine the amc question type.
        """
        # test if question or questionmult
        amcqtype = 'questionmultx'


        return amcqtype

    def answers(self):
        """ Create and parse answers.
        """
        # eg: \AMCnumericChoices{3.141592653589793}{digits=6, decimals=5, sign=true}
        amc_choices = etree.Element('AMCnumericChoices')

        # Check if there is several answers
        ans_list = self.q.findall(".//answer")
        if len(ans_list) > 1:
            Logger.warning('Multiple answers in the moodle question. ')

        # Process the 1st good answer
        ok_list = self.q.findall(".//answer[@fraction='100']")
        if len(ok_list) != 1:
            Logger.warning('Multiple good answer. Take only the first one.')
        else:
            ans = ok_list[0]
            # get and cast the target
            target = float(ans.find('text').text)
            if target.is_integer():
                target = int(target)
            tolerance = float(ans.find('tolerance').text)
            # Get sign, if positive use default SIGN
            if target < 0:
                sign = True
            else:
                sign = SIGN
            # Estimate required the number of digit for floor(target)
            digits = max(DIGIT,
                         math.ceil(math.log10(abs(target))))
            # Estimate the requiered number of decimal from tolerance
            # if decimals > 0, need \usepackage{fp} in AMC
            if abs(tolerance) > EPS:
                decimals = abs(min(-DECIMAL,
                                   math.floor(math.log10(abs(tolerance)))))
            else:
                decimals = 0
            # Compute AMC tolerance for exact solution
            exact = round(tolerance*(10**decimals))
            # Populate the tree
            attrib = {'exact': exact,
                      'decimals': decimals,
                      'digits': digits + decimals,
                      'sign': str(sign).lower(),
                      'scoreexact': SCOREEXACT}
            # Check for looser bounds and update attrib if needed
            for a in ans_list:
                t = float(a.find('text').text)
                f = float(a.attrib['fraction'])
                if (a is not(ans)) and (f > 0) and (abs(t-target) < EPS):
                    Logger.warning('  Detect two identical targets.')
                    Logger.warning('    Try to generate approx scoring..')
                    tolerance_approx = float(a.find('tolerance').text)
                    scoreapprox = f*SCOREEXACT/100
                    approx = round(tolerance_approx*(10**decimals))
                    attrib.update({'scoreapprox': scoreapprox,
                                   'approx': approx})

            # Prepare the latex rendering
            amc_choices.text = self._render_dict(attrib)
            amc_choices.attrib['target'] = str(target)

        return amc_choices


    @staticmethod
    def _render_dict(d):
        """ Convert a dict in key=val, key=val, ...
        """
        out_=''
        for item in d.items():
            pair = '{} = {}, '.format(str(item[0]).strip("'"), str(item[1]).strip("'"))
            out_ += pair
        out = out_[0:-2]
        return out

class QuestionDescription(Question):
    """ Description question.
    """

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        super().__init__(q)
        self.q = q
        self.qtype = 'description'

    def gettype(self):
        """ Determine the amc question type.
        """
        amcqtype = 'question'

        return amcqtype

    def answers(self):
        """ Create and parse answers, nothing to do here.
        """

        return None

    def question(self):
        """ Get question text. Overwrite the class method.
        """
        # call the class method and add `\QuestionIndicative`
        text = super().question()
        text.text = u"\QuestionIndicative\n" + text.text

        return text

class QuestionCalculatedMulti(Question):
    """ Moodle Calculated question (question or questionmult).
    """

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        super().__init__(q)
        self.q = q
        self.qtype = 'calculatedmulti'

    def gettype(self):
        """ Determine the amc question type.
        """
        # test if question or questionmult
        single = self.q.find('single').text
        if single.lower() in TRUE:
            amcqtype = 'question'
        elif single.lower() in FALSE:
            amcqtype = 'questionmult'
        else:
            Logger.error(" Unknwon question type in '{}'".format(self.name))

        return amcqtype

    def _dataset(self):
        """ Parse XML dataset to built question header.
        """
        datasets = single = self.q.find('dataset_definitions')
        jockers = []
        # Collect jockers datas
        for data in datasets.iterfind('dataset_definition'):
            # check if dataset is private (if not, may have inconsistenies)
            if data.find('status/text').text.lower() !='private':
                Logger.warning("Some variables are shared between question. May leads to inconsistencies.")
            # get variable name and remove '_' as in CalculatedParser
            v = data.find('name/text').text
            v = v.replace('_','')
            # check distribution law
            if data.find('distribution/text').text !='uniform':
                Logger.warning("Only 'uniform' distribution is supported.")
            # Gets bounds
            vmin = data.find('minimum/text').text
            vmax = data.find('maximum/text').text
            ndec = data.find('decimals/text').text
            # Gets moodle values
            values = []
            for value in data.iterfind('dataset_items/dataset_item/value'):
                values.append(value.text)
            # store into a dict
            jockers.append({'name' : v, 'min': vmin, 'max': vmax,
                           'ndec': ndec, 'values': values})

        # Select the good layout to create moodle variable in LaTeX
        # TODO add other rules for other rendering strategies
        if CALCULATED_DEFAULT_PARSER == 'xml2fp':
            header_line = "\\FPeval{{\\{jname}}}{{trunc({jmin}+random*({jmax}-{jmin}), {jndec})}} % uniform in [{jmin}, {jmax}]"

        header = []
        # Render all the jockers/variables
        for j in jockers:
            header.append(header_line.format(jname=j['name'],
                                             jmin=j['min'], jmax=j['max'],
                                             jndec=j['ndec']))

        data_header = '\n'.join(header)

        return data_header


    def question(self):
        """ Get question text. Overwrite the class method to add a header that
        define the random variable.
        """

        # extract questiontext text
        questiontext = self.q.find('questiontext/text')
        rawtext = questiontext.text
        # call math expression parser
        # Create the parser /!\ need to be before latex rendring because of {}
        parser = CreateCalculatedParser(CALCULATED_DEFAULT_PARSER)
        # parse question
        parsed_text = parser.render(rawtext)
        # update questiontext
        questiontext.text = etree.CDATA(parsed_text)
        # call the class method (html2tex)
        text = super().question()
        # Create the header containg the definition of random variable
        header = self._dataset()
        # Concatenate both
        text.text = '\n'.join((header, text.text))

        return text

    def answers(self):
        """ Create and parse answers.
        """
        amc_choices = etree.Element('choices')
        # loop over all answers
        for i, ans in enumerate(self.q.findall('.//answer')):
            # TODO how to integrate the scoring aspect
            if self.gStrategy == 'std':
                # the fraction (scoring) field is not allways at the same place
                try:
                    fraction = ans.find('fraction').text
                except:
                    try:
                        fraction = ans.attrib['fraction']
                    except:
                        raise ValueError('fraction not found.')
                if float(fraction) > 0:
                    tag = 'correctchoice'
                else:
                    tag = 'wrongchoice'
            amc_ans = etree.Element(tag, attrib={'order': str(i)})

            # call math expression parser
            cdata_content = etree.tostring(ans.find('text'), encoding='utf8').decode('utf-8')
            # Create the parser
            parser = CreateCalculatedParser(CALCULATED_DEFAULT_PARSER)
            # parse answer
            text = parser.render(cdata_content)
            # convert to etree
            text_tree = etree.fromstring(text)
            # add to current answer
            amc_ans.append(text_tree)
            # store in a list of all answers
            amc_choices.append(amc_ans)

        return amc_choices



# dict of all available question
Q_FACTORY = {'multichoice': QuestionMultichoice,
             'essay': QuestionEssay,
             'description': QuestionDescription,
             'numerical': QuestionNumerical,
             'calculatedmulti': QuestionCalculatedMulti}

def CreateQuestion(qtype, question):
    """ Factory function for creating the Questions* objects.


    Parameters
    ----------
    qtype : string
        the moodle name of the question type.
    question : etree.Element
        The XML tree of the considered question.

    Returns
    -------
    Instance of concrete Questions class.

    """

    try:
        return Q_FACTORY[qtype](question)   # *args,**kwargs)
    except:
        raise KeyError(" 'qtype' argument should be in {}".format(Q_FACTORY.keys() ) )
