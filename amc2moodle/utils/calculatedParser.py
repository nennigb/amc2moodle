#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illustration of Basic Feature of Pyparsing

Created on Wed Jul 15 21:04:36 2020

@author: bn
"""
from abc import ABC, abstractmethod
from pyparsing import Word, alphas, nums, alphas, alphanums, Char, oneOf,\
                      Suppress, Combine, Regex, Group, ZeroOrMore, Literal,\
                      Forward, Optional, ParseResults, _flatten
import logging


__all__ = ['CalculatedParserToFP', 'CalculatedParserFromFP',
           'CreateCalculatedParser']

# TODO create test suite
# TODO create CalculatedParserToPGF
# TODO create Parser for loop with python evaluation


"""

# FPeval operators
+ pow e round sin arcsin - root pi trunc cos arccos *
exp / ln abs min clip tan arctan cot arccot neg max
pow(#1,#2) returns #2 to the power of #1
round(#1:#2) round #1 to #2 decimal places

# MOODLE operators https://docs.moodle.org/3x/fr/Question_calcul%C3%A9e
there is more function in moodle
abs, acos, acosh, asin, asinh, atan2, atan, atanh, bindec, ceil, cos,
cosh, decbin, decoct, deg2rad, exp, expm1, floor, fmod, is_finite
is_infinite , is_nan , log10, log1p , log, max , min, octdec , pi()
pow (numberToRaise, NumberRaisedTo), rad2deg, rand , round , sin , sinh
sqrt , tan , tanh

# Remarks
The unary prefix operation “-” is not known, therefore one should use the 
function neg() instead.
"""


# moodle to fpeval
FP_EVAL_FUNCTION = {'atan': 'arctan',
                    'pow': 'pow',  # need to swap args
                    'sin': 'sin',
                    'asin': 'arcsin',
                    'cos': 'cos',
                    'acos': 'arccos',
                    'tan': 'tan',
                    'atan': 'arctan',
                    'sqrt': 'sqrt',  # need to use root
                    'abs': 'abs',
                    'exp': 'exp',
                    'log': 'ln',
                    'min': 'min',
                    'max': 'max',
                    'pi': '\\FPpi'}

FP_UNSUPPORTED = {'atan2', 'atanh', 'bindec', 'decbin', 'decoct', 'deg2rad',
                  'expm1', 'fmod', 'is_finite', 'is_infinite', 'is_nan',
                  'log10', 'log1p', 'octdec', 'rad2deg', 'rand', 'cosh',
                  'sinh', 'tanh', 'acosh', 'asinh', 'atanh', 'ceil', 'floor'}

FP_MAX = 999999999999999999.999999999999999999


# FP to moodle
MDL_FUNCTION = {'arctan': 'atan',
                'pow': 'pow',  # need to swap args
                'sin': 'sin',
                'arcsin': 'asin',
                'cos': 'cos',
                'arccos': 'acos',
                'tan': 'tan',
                'arctan': 'atan',
                'root': 'sqrt',  # need to use sqrt or pow
                'abs': 'abs',
                'exp': 'exp',
                'ln': 'log',
                'min': 'min',
                'max': 'max',
                'clip': '',
                'neg': '-'}

MDL_UNSUPPORTED = {'clip'}

''' Usefull info for pgfmathparse
http://tug.ctan.org/tex-archive/graphics/pgf/base/doc/pgfmanual.pdf p 1033

The following functions are recognized:

abs,acos,add,and,array,asin,atan,atan2,bin,ceil,cos,
 cosec,cosh,cot,deg,depth,div,divide,e,equal,factorial, false,
 floor,frac,gcd,greater,height,hex,Hex,int,ifthenelse,iseven,isodd,isprime,
 less,ln,log10,log2,max,min,mod,Mod,multiply,
 neg,not,notequal,notgreater,notless,
 oct,or,pi,pow,rad,rand,random,real,rnd,round,
 scalar,sec,sign,sin,sinh,sqrt,subtract,tan,tanh,true, veclen,width


 pow(x,y) Raises x to the power y
 \pgfmathpi
 default is in degree need : \pgfkeys{/pgf/trig format=rad} -> use a header

 pgf can change its aruthmetic between fp and fpu
'''


# activate logger
Logger = logging.getLogger(__name__)


class CalculatedParser(ABC):
    """ Define abstract class for parsing moodle calculted question and a 
    common interface for latex rendering.
    """
    @property
    @abstractmethod
    def varformat(self):
        """A formater string for rendering variable in tex. Must contains {name}"""
        pass

    def grammar(self):
        """ Define the parser grammar.
        """
        # Ignore TeX commands between delimiters $$, \(,  \)
        tex_eq = (Literal(r'\(') | Literal(r'$$') | Literal(r'\[')) + ... + (Literal(r'\)') | Literal(r'$$') | Literal(r'\]'))

        # Define elemtary stuff
        leftAc = Literal('{').suppress()
        rightAc = Literal('}').suppress()
        lpar = Literal('(')
        rpar = Literal(')')
        integer = Word(nums)            # simple unsigned integer
        real = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
        real.setParseAction(self.real_hook)
        number = real | integer

        # Define function
        fnname = Word(alphas, alphanums + "_")('name')
        # Require expr to finalize the def
        function = Forward()
        function.setParseAction(self.function_hook)

        # What are the namming rule for the jocker? Need to start by a letter,
        # may contain almost everything
        variable = Combine(leftAc + Word(alphas, alphanums + "_") + rightAc)('name')
        variable.setParseAction(self.variable_hook)
        variable.ignore(tex_eq)
        # arithmetic operators
        minus = Literal('-')
        arithOp = oneOf("+ * /") | minus
        equal = Literal('{=').suppress()
        # Require atom to finalize the def
        expr = Forward()
        # Define atom
        atom = number | (0, None)*minus + (Group(lpar + expr + rpar) | variable | function)
        atom.setParseAction(self.atom_hook)
        # Finalize postponed elements...
        expr << atom + ZeroOrMore(arithOp + atom)
        # Need to group arguments for swapping them
        function << fnname + Group(lpar + Group(ZeroOrMore(expr)) + Optional(Literal(',') + Group(expr)) + rpar)
        # Define equation
        equation = equal + expr + rightAc
        equation.setParseAction(self.equation_hook)
        return equation, variable

    def render(self, s):
        """ Render the input string s to the targeted latex output.
        """
        # create the parser
        equation, variable = self.grammar()
        # parse and replace 'equation'
        out = equation.transformString(s)
        # parse and replace for the 'variable'
        # different syntax because render variable alone or in equations is different
        out2 = self._render_variable(variable, out)
        return out2

    def _render_variable(self, variable, s):
        """ Transform variable to the targeted LaTeX output. Since rendering
        variable alone and in equation is different, need specific method.
        """
        vout = []
        # initial start value
        start_ = 0
        # call the concrete value
        vrender = self.varformat
        for tok, start, end in variable.scanString(s):
            vout.append(s[start_:start])
            vout.append(vrender.format(name=tok.name))
            start_ = end
        vout.append(s[start_::])
        return ''.join(vout)

    @staticmethod
    def variable_hook(tokens):
        """ Change variable name for fp package.
        """
        # notpossible to use '_' in tex name
        out = tokens.name.replace('_', '')
        if out.isalpha() == False:
            Logger.warning("  The variable '{}' is not compatible with LaTeX naming convention. You will need to change this name in our tex file.".format(out))
        return "\\" + out +' '

    @staticmethod
    def real_hook(tokens):
        """ Convert real number to decimal notation and overflow checks.
        """
        # check for overflow
        x = float(tokens[0])
        if abs(x) > FP_MAX:
            Logger.warning(" This number {} will lead to overflow in FP.".format(x))
        # if floating point notation, need to convert to fixed point in FP
        if 'e' in tokens[0]:
            # conversion to fixed decimal format
            strx = format(x, '.18f')
            # strip to avoid tailling 0 (if possible)
            left, right = strx.split('.')
            out = left + '.' + right.rstrip('0')
        else:
            # do nothing
            out = tokens[0]
        return out

    @staticmethod
    @abstractmethod
    def atom_hook(tokens):
        """ Render atmo. Usefull to change unary minus into neg(exp) at
        atom level.
        """
        pass

    @staticmethod
    @abstractmethod
    def equation_hook(tokens):
        """ Render 'equation' expression for the LaTeX target package.
        """
        pass

    @staticmethod
    @abstractmethod
    def function_hook(tokens):
        """ Modify the moodle function API to conform to the LaTeX target
        package api.
        """
        pass


class CalculatedParserToFP(CalculatedParser):
    """ Define the class for parsing moodle calculted question into FP.


    Normally only hooks have to be given.
    """
    # string to use for variable replacement in render
    varformat = '\\FPprint{{{name}}}'

    @staticmethod
    def atom_hook(tokens):
        """ Change unary minus into neg(exp) at atom level.
        """
        # not possible to use '- expr' in tex with fp
        out = tokens.asList()
        if out[0] == '-':
            out[0] = 'neg('
            out.extend([')'])
        return out

    @staticmethod
    def equation_hook(tokens):
        """ Render 'equation' expression for FP package
        """
        out = []
        for tok in tokens:
            if isinstance(tok, ParseResults):
                out += tok.asList()
            elif isinstance(tok, list):
                out += tok
            else:
                out.append(tok)
        # call ParseResults _flatten to un-nest the list before the final rendering
        out = ''.join(_flatten(out))
        return "\\FPprint{\\FPeval{\\out}{clip(" + out + ")}\\out}"

    @staticmethod
    def function_hook(tokens):
        """ Modify the moodle function API to conform to FP api.
        """
        # to check : ceil; (floor 	Arrondit à l'entier inférieur ); (ceil 	Arrondit à l'entier supérieur )
        # possible with playing with trunc(#1:#2) or round()
        out = tokens.asList().copy()
        # print('In hook :' , tokens)
        # start wit pathological case
        # sqrt(x) doen't exist in FP, neead to use root(x, 2)
        if tokens.name == 'sqrt':
            out[0] = 'root'
            # TODO better to use dequee for left side op
            out[1].pop(0)
            out[1].insert(0, '(2, ')
        elif tokens.name == 'pow':
            out = tokens.asList()
            out[1][1], out[1][3] = out[1][3], out[1][1]
        elif tokens.name == 'pi':
            # remove ()
            out = FP_EVAL_FUNCTION['pi']
        # other name are just rename
        elif tokens.name in FP_EVAL_FUNCTION.keys():
            out[0] = FP_EVAL_FUNCTION[tokens.name]
        # check that only valid expression are used
        elif tokens.name in FP_UNSUPPORTED:
            Logger.error("Unsupported *function* '{}' by `fp` package in the expression.".format(tokens.name))
            out = tokens
        else:
            Logger.error("Unsupported *function* '{}' in the expression.".format(tokens.name))
            out = tokens
        # print('In hook end :' , out)
        return out


class CalculatedParserFromFP(CalculatedParser):
    """ Define the class for parsing LaTeXML/FP expression into moodle.


    Normally only hooks have to be given.

    Only equation are usefull here
    """
    # string to use for variable replacement in render
    varformat = '{name}'

    def __init__(self):
        # store all wildcards encounter during the parsing
        self.wildcards = set()

    def grammar(self):
        """ Define the parser grammar for FP syntaxe. Modified from base class.
        """
        # Define elemtary stuff
        leftAc = Literal('{').suppress()
        rightAc = Literal('}').suppress()
        lpar = Literal('(')
        rpar = Literal(')')
        integer = Word(nums)            # simple unsigned integer
        real = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
        # add extra input parameter to the parseaction to keep in mind all variable
        real.setParseAction(self.real_hook)
        number = real | integer

        # Define function
        fnname = Word(alphas, alphanums + "_")('name')
        # Require expr to finalize the def
        function = Forward()
        function.setParseAction(self.function_hook)

        # Normally, no variable excepted random*, pi ...
        # may contain almost everything
        variable = Word(alphas, alphanums + "_")('name')
        variable.setParseAction(lambda t : self.variable_hook(self.wildcards, t))
        # arithmetic operators
        minus = Literal('-')
        arithOp = oneOf("+ * /") | minus
        # Require atom to finalize the def
        expr = Forward()
        # Define atom
        atom = number | (0, None)*minus + (Group(lpar + expr + rpar) | function | variable)
        atom.setParseAction(self.atom_hook)
        # Finalize postponed elements...
        expr << atom + ZeroOrMore(arithOp + atom)
        function << fnname + Group(lpar + Group(ZeroOrMore(expr)) + Optional(Literal(',') + Group(expr)) + rpar)
        # Define equation
        equal = Literal('fp{').suppress()
        equation = equal + expr + rightAc
        equation.setParseAction(self.equation_hook)
        return equation, variable

    def render(self, s):
        """ Render the input string s to the targeted moodle output.
        """
        # create the parser
        equation, variable = self.grammar()
        # parse and replace 'equation'
        out = equation.transformString(s)

        return out

    @staticmethod
    def variable_hook(wildcards, tokens):
        """ Change variable name for moodle interpreter.
        """
        out = tokens.asList()
        if out[0] == 'pi':
            # pi is a function in moodle
            return 'pi()'
        else:
            # return the moodle variable format
            wildcards.add(out[0])
            return '{' + out[0] +'}'

    @staticmethod
    def atom_hook(tokens):
        """ Change unary minus into neg(exp) at atom level.
        """      
        return tokens

    @staticmethod
    def equation_hook(tokens):
        """ Render 'equation' expression for moodle interpreter.
        """
        out = []
        for tok in tokens:
            if isinstance(tok, ParseResults):
                out += tok.asList()
            elif isinstance(tok, list):
                out += tok
            else:
                out.append(tok)
        # call ParseResults _flatten to un-nest the list before the final rendering
        out = ''.join(_flatten(out))
        return "{=" + out + "}"

    @staticmethod
    def function_hook(tokens):
        """ Modify the moodle function API to conform to FP api.
        """
        # to check : ceil; (floor 	Arrondit à l'entier inférieur ); (ceil 	Arrondit à l'entier supérieur )
        # possible with playing with trunc(#1:#2) or round()
        out = tokens.asList().copy()
        # start wit pathological case
        # try to use sqrt
        if tokens.name == 'root':
            try:
                # is it possible to evaluate the exponent
                expo = float(''.join(out[1][1]))
                if abs(expo - 2) < 1e-12:
                    out[0] = 'sqrt'
                    out[1] = ['(', out[1][3], ')']
            except :
                # use pow with 1/nth
                out[0] = 'pow'
                # take the inverse of the exponent
                out[1][1] = ['1', '/', '(' , out[1][1] , ')']
                # need to swap arg order
                out[1][1], out[1][3] = out[1][3], out[1][1]
        elif tokens.name == 'pow':
            out = tokens.asList()
            out[1][1], out[1][3] = out[1][3], out[1][1]
        # other name are just rename
        elif tokens.name in MDL_FUNCTION.keys():
            out[0] = MDL_FUNCTION[tokens.name]
        # check that only valid expression are used
        elif tokens.name in MDL_UNSUPPORTED:
            Logger.error("Unsupported *function* '{}' by `moodle` interpreter in the expression.".format(tokens.name))
            out = tokens
        else:
            Logger.error("Unsupported *function* '{}' in the expression.".format(tokens.name))
            out = tokens
        return out

# dict of all available question
PARSER_FACTORY = {'xml2fp': CalculatedParserToFP,
                  'fp2xml': CalculatedParserFromFP}

def CreateCalculatedParser(ptype):
    """ Factory function for creating the CalculatedParser* objects.
    
    Parameters
    ----------
    ptype : string
        the kind of parser to create picked from PARSER_FACTORY.

    Returns
    -------
    Instance of concrete CalculatedParser* class.

    """

    try:
        return PARSER_FACTORY[ptype]()   # *args,**kwargs)
    except:
        raise KeyError(" 'qtype' argument should be in {}".format(PARSER_FACTORY.keys() ) )

if __name__=="__main__":
    # Basic example of usage
    # moodle2amc
    s= "<text><![CDATA[<p><b>Moodle</b> and <b>fp</b> latex package syntax is not always equivalent. Here some test for pathological cases.</p><p>Let {x} and {y} some real number.<br></p><ul><li>argument of 'pow' function are in a different order {=pow({x},2)}</li><li>the 'sqrt' function doesn't exist, need 'root(n, x)' in fp, {=sqrt(({x}-{y})*({x}+{y}))}</li><li>'pi' is a function in moodle, {=sin(1.5*pi())}</li><li>test with '- unary' expression {=-{x}+(-{y}+2)}<br></li></ul>]]></text>"
    parser = CreateCalculatedParser('xml2fp')
    out = parser.render(s)
    print('> moodle2amc:\n', out)

    # amc2moodle
    #s= "fp{(sin(3) + clip((trunc(1+rand0*(10-1), 1))+(trunc(1+rand1*(10-1), 1))))}"
    s= "blabla fp{ ( root(2, 3.0+1.0) + sin(pi+rand0) + arctan(rand1)) } blabla"
    parser = CreateCalculatedParser('fp2xml')
    out = parser.render(s)
    print('> amc2moodle:\n', out)

    print('> wildcards set:', parser.wildcards)
    

