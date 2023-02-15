# -*- coding: utf-8 -*-
# Copyright (c) 2017 Keith Ito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
from .numbers_to_thaana_transliterator import NumbersToThaanaTransliterator
from unidecode import unidecode

# numbers transliterator
transliterator = NumbersToThaanaTransliterator()

# Regular expression matching whitespace:
_whitespace_re = re.compile(r"\s+")

_suffixes = {
    "ދޭށެވެ" : "ދޭން",
    "ޑެވެ" : "ޑު",
    "ށެވެ" : "ށް",
    "ންނެވެ" : "ން",
    "ނެވެ" : "ން",
    "ކެވެ" : "އް",
    "މެވެ" : "ން" ,
    " އެވެ" : "",
    "ތެވެ" : "ތް",
    "ހެވެ" : "ސް"
}

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [
    (re.compile("\\b%s\\." % x[0], re.IGNORECASE), x[1])
    for x in [
        ("mrs", "misess"),
        ("mr", "mister"),
        ("dr", "doctor"),
        ("st", "saint"),
        ("co", "company"),
        ("jr", "junior"),
        ("maj", "major"),
        ("gen", "general"),
        ("drs", "doctors"),
        ("rev", "reverend"),
        ("lt", "lieutenant"),
        ("hon", "honorable"),
        ("sgt", "sergeant"),
        ("capt", "captain"),
        ("esq", "esquire"),
        ("ltd", "limited"),
        ("col", "colonel"),
        ("ft", "fort"),
    ]
]

_arabic_expressions = [
    (re.compile("ދުﷲ"), "ދުއްލޯ"),
    (re.compile("ﷲ"), "އައްލޯހު"),
]



def expand_abbreviations(text):
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text



def lowercase(text):
    return text.lower()


def collapse_whitespace(text):
    return re.sub(_whitespace_re, " ", text)



def convert_to_ascii(text):
    return unidecode(text)


def basic_cleaners(text):
    """Basic pipeline that lowercases and collapses whitespace without transliteration."""
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text

def expand_arabic_expressions(text):
    for regex, replacement in _arabic_expressions:
        text = re.sub(regex, replacement, text)
    return text

def remove_dhivehi_suffixes(text):
    for key, value in _suffixes.items():
        text = text.replace(key, value)
    return text
    

def dhivehi_cleaners(text):
    text = transliterator.transliterate(text)
    text = expand_arabic_expressions(text)
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = collapse_whitespace(text)
    text = remove_dhivehi_suffixes(text)
    return text