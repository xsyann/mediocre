#!/usr/bin/env python
# -*- coding: utf-8 -*-
# classes.py
#
# Author: Yann KOETH
# Created: Mon Nov 10 16:50:26 2014 (+0100)
# Last-Updated: Thu Nov 27 12:53:15 2014 (+0100)
#           By: Yann KOETH
#     Update #: 30
#

import string

from PyQt5.QtGui import QStandardItem, QStandardItemModel


class TreeModel(QStandardItemModel):
    pass


class TreeItem(QStandardItem):
    pass


class Class:
    def __init__(self, value, repr, folder):
        self.value = value
        self.repr = repr
        self.folder = folder


class Classes:
    ENGLISH_ALPHABET = "English Alphabet"
    UPPER = "Upper case"
    LOWER = "Lower case"
    DIGITS = "Digits"
    PUNCTUATION = "Punctuation"
    SYMBOLS = "Symbols"
    COMMON_PUNC = "Common"

    LOWER_SUFFIX = "_small"
    SYMBOLS_PREFIX = "sym_"
    DIGITS_PREFIX = "num_"

    classes = None

    @staticmethod
    def _addClass(parent, value, repr, name):
        item = TreeItem(repr)
        item.setData(Class(value, repr, name))
        parent.appendRow(item)

    @staticmethod
    def _addGroup(parent, name):
        group = TreeItem(name)
        group.setData(name)
        parent.appendRow(group)
        return group

    @staticmethod
    def _addLettersClasses(model):
        alpha = Classes._addGroup(model, Classes.ENGLISH_ALPHABET)
        upper = Classes._addGroup(alpha, Classes.UPPER)
        lower = Classes._addGroup(alpha, Classes.LOWER)
        for letter in list(string.ascii_lowercase):
            Classes._addClass(lower, letter, letter,
                              letter + Classes.LOWER_SUFFIX)
            uppercase = letter.upper()
            Classes._addClass(upper, uppercase, uppercase, letter)

    @staticmethod
    def _addDigitsClasses(model):
        digits = Classes._addGroup(model, Classes.DIGITS)
        for digit in list(string.digits):
            Classes._addClass(digits, digit, digit,
                              Classes.DIGITS_PREFIX + digit)

    @staticmethod
    def _addPunctuationClasses(model):
        punctuation = {
            '\'': ('apostrophe', 'apos'), ',': ('comma', 'comma'),
            ':': ('colon', 'colon'), '-': ('hyphen', 'hyphen'),
            '!': ('exclamation mark', 'exclmark'),
            '"': ('quote mark', 'quotmark'), ' ': ('space', 'space'),
            '{': ('left curly bracket', 'lcbracket'),
            '(': ('left parenthesis', 'lparen'),
            '[': ('left square bracket', 'lsqbracket'),
            '.': ('point', 'point'), '?': ('question mark', 'questmark'),
            '}': ('right curly bracket', 'rcbracket'),
            ')': ('right parenthesis', 'rparen'),
            ']': ('right square bracket', 'rsqbracket'),
            ';': ('semicolon', 'scolon'), '/': ('slash', 'slash')
        }
        symbols = {
            '&': ('ampersand', 'amper'),
            '@': ('at sign', 'arob'), '`': ('back quote', 'bquote'),
            '\\': ('backslash', 'bslash'), '^': ('caret', 'caret'),
            '$': ('dollar', 'dollar'), '=': ('equal', 'equal'),
            '>': ('greater than', 'gthan'),
            '<': ('lower than', 'lthan'), '#': ('number sign', 'num'),
            '%': ('percent', 'pcent'),
            '|': ('pipe', 'pipe'), '+': ('plus', 'plus'),
            '*': ('star', 'star'),
            '~': ('tilde', 'tilde'), '_': ('underscore', 'under')
        }

        punc = Classes._addGroup(model, Classes.PUNCTUATION)
        commonGroup = Classes._addGroup(punc, Classes.COMMON_PUNC)
        symbolGroup = Classes._addGroup(punc, Classes.SYMBOLS)
        for sym in list(string.punctuation + ' '):
            is_sym, is_punc = sym in symbols, sym in punctuation
            if is_sym or is_punc:
                repr, name = symbols[sym] if is_sym else punctuation[sym]
                parent = commonGroup if is_punc else symbolGroup
                repr = "{0} ({1})".format(sym, repr.capitalize())
                Classes._addClass(parent, sym, repr,
                                  Classes.SYMBOLS_PREFIX + name)

    @staticmethod
    def getClasses():
        if not Classes.classes:
            model = TreeModel()
            Classes._addLettersClasses(model)
            Classes._addDigitsClasses(model)
            Classes._addPunctuationClasses(model)
            Classes.classes = model
        return Classes.classes
