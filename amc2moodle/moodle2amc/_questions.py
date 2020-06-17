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

__all__ = ['Question', 'QuestionMultichoice', 'CreateQuestion',
           'SUPPORTED_QUESTION_TYPE']

from lxml import etree
from xml.sax.saxutils import unescape
import base64
import os
from abc import ABC, abstractmethod
from wand.image import Image
# decode filemame unsed in moodle
import urllib


# list of supported moodle question type for
SUPPORTED_QUESTION_TYPE = {'multichoice', 'essay'}

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
        self.name = q.find('name/text').text
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
        cdata_content = (cdata_content.replace('<text><![CDATA[', '<text>')
                         .replace('%', '\%')
                         .replace(']]></text>', '</text>')
                         .replace('\n', '')
                         .replace('<br>', ''))

        parser = etree.HTMLParser(recover=True)
        tree_content = etree.fromstring(unescape(cdata_content), parser)
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
        # perhaps not so obvious and will require to extract cdata
        cdata_content = etree.tostring(self.q.find('questiontext/text'),
                                       encoding='utf8').decode('utf-8')
        text = self.html2tex(cdata_content)

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

    def gettype(self,):
        """ Determine the amc question type.
        """
        # test if question or questionmult
        single = self.q.find('single').text
        if single.lower() == 'true':
            amcqtype = 'question'
        elif single.lower() == 'false':
            amcqtype = 'questionmult'
        else:
            print("> Unknwon question type in '{}'".format(self.name))

        return amcqtype

    def answers(self):
        """ Create and parse answers.
        """
        amc_choices = etree.Element('choices')
        # loop over all answers
        for i, ans in enumerate(self.q.findall('.//answer')):
            # bool use to check if html parsing (CDATA) is needed
            html = ans.attrib['format'].lower() == 'html'
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
            if html:
                cdata_content = etree.tostring(ans.find('text'), encoding='utf8').decode('utf-8')
                text = self.html2tex(cdata_content)
                amc_ans.append(text)
            else:
                latex = etree.tostring(ans.find('text'), encoding='utf8').decode('utf-8')
                amc_ans.text = latex
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

    def gettype(self,):
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


# dict of all available question
Q_FACTORY = {'multichoice': QuestionMultichoice,
             'essay': QuestionEssay}

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
