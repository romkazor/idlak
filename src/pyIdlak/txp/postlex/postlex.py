# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude
#                                       Skaiste Butkute)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

# postlex module for Idlak

import os
import sys
from lxml import etree
from pcre import compile
from .. import idargparse, xmldoc, pyIdlak_txp, pytxplib

_valid_input_types = ['pron', 'pos', 'norm']


class Pattern:

    def __init__(self, index, input_type, rgx, verboselvl=0):
        self.verboselvl = verboselvl
        self.index = index
        if input_type not in _valid_input_types and self.verboselvl:
            sys.stderr.write("WARNING: The input type {} is invalid, valid " +
                             "input types: {}".format(input_type,
                                                      _valid_input_types))

        self.input_type = input_type
        self.rgx = compile(rgx)

    def __repr__(self):
        return ("{{Pattern: index {}, input type {}, rgx {}}}"
                .format(self.index, self.input_type, self.rgx))

    @staticmethod
    def create_pattern(xml, verboselvl=0):
        index = 0
        input_type = ""
        rgx = ""
        if xml.tag == "pattern":
            index = int(xml.get("index"))
            input_type = xml.get("input_type")
            rgx = xml.get("rgx")
        return Pattern(index, input_type, rgx, verboselvl)

    def apply(self, tkxml):
        # check the input type
        input = tkxml.get(self.input_type)
        # in case the tokens did not go through a normaliser
        if input is None and self.input_type == "norm":
            input = tkxml.get("tknorm")
        # reject if the input is empty or was not found
        if input is None or input == "":
            return False
        if self.rgx.match(input) is not None:
            return True
        return False


class Action:

    def __init__(self, rgx, grp, replace, verboselvl=0):
        self.verboselvl = verboselvl
        self.rgx = compile(rgx)
        self.grp = grp
        self.replace = replace

    def __repr__(self):
        return "{{Action: rgx {}, grp {}, replace {}}}".format(self.rgx,
                                                               self.grp,
                                                               self.replace)

    @staticmethod
    def create_action(xml, verboselvl=0):
        rgx = ""
        grp = 0
        replace = ""
        if xml.tag == "action":
            rgx = xml.get("rgx")
            grp = int(xml.get("grp"))
            replace = xml.get("replace")
        return Action(rgx, grp, replace, verboselvl)

    def apply(self, tkxml):
        pron = tkxml.get("pron")
        matched = self.rgx.match(pron)
        if not matched:
            return False
        if len(matched.groups()) > self.grp + 1:
            return False
        pron = (pron[0:matched.start(self.grp+1)] + self.replace +
                pron[matched.end(self.grp+1):])
        tkxml.set("pron", pron)
        return True


class Rule:

    def __init__(self, name, verboselvl=0):
        self.name = name
        self.patterns = []
        self.verboselvl = verboselvl
        self.action = None

    def append_pattern(self, pattern):
        self.patterns.append(pattern)
        # sort patterns by indexes?

    def set_action(self, action):
        self.action = action

    def __repr__(self):
        patterns_str = ""
        for p in self.patterns:
            patterns_str += p.__repr__() + "\n"
        patterns_str = patterns_str[:-1]
        return ("{{Rule:\n\t{}\n\t{}\n}}"
                .format("\n\t".join(patterns_str.split('\n')),
                        self.action.__repr__()))

    def apply(self, pretk, tk, posttk):
        for pttrn in self.patterns:
            # match pretks
            if pttrn.index < 0:
                if len(pretk) == 0:
                    return False
                pre = pretk[len(pretk)+pttrn.index]
                if not pttrn.apply(pre):
                    return False
            # match tk
            elif pttrn.index == 0 and not pttrn.apply(tk):
                return False
            # match posttks
            elif pttrn.index > 0:
                if len(posttk) == 0:
                    return False
                post = posttk[len(posttk)-pttrn.index]
                if not pttrn.apply(post):
                    return False
        # when all patterns were matched, continue with
        # replacing pronounciation
        if not self.action.apply(tk) and self.verboselvl:
            sys.stderr.write("WARNING: The patterns matched, action could " +
                             "not be processed!! Rule: {}, rgx: {}, pron: {}\n"
                             .format(self.name, self.action.rgx.pattern,
                                     tk.get("pron")))
        return True


class PostlexRules:
    def __init__(self, ruledir, verboselvl=0):
        self.minoffset = 0
        self.maxoffset = 0
        self.verboselvl = verboselvl
        self.rules = []
        self.read_rules(ruledir)

    def read_rules(self, ruledir):
        if self.verboselvl:
            sys.stderr.write('\tLoading postlex rules file\n')
        ruleset = etree.parse(ruledir).getroot().findall("rule")
        for rulexml in ruleset:
            # create rule
            rule = Rule(rulexml.get("name"), self.verboselvl)
            for r_child in rulexml.getchildren():
                # create patterns and append to pattern list
                if r_child.tag == "pattern":
                    rule.append_pattern(Pattern
                                        .create_pattern(r_child,
                                                        self.verboselvl))
                    if self.minoffset > int(r_child.get('index')):
                        self.minoffset = int(r_child.get('index'))
                    if self.maxoffset < int(r_child.get('index')):
                        self.maxoffset = int(r_child.get('index'))
                # create and set action of the rule
                elif r_child.tag == "action":
                    rule.set_action(Action.create_action(r_child,
                                                         self.verboselvl))
                elif self.verboselvl:
                    sys.stderr.write("Unrecognised element detected: " +
                                     etree.tostring(r_child))

            self.rules.append(rule)

    def runruleset(self, tokens):
        if self.verboselvl:
            sys.stderr.write('\tRunning postlex rules\n')
        pretk = []
        posttk = []
        if self.maxoffset > 0:
            posttk = (tokens[1:self.maxoffset+1]
                      if len(tokens) > self.maxoffset else tokens[1:])
        for tk in tokens:
            # skip tokens that weren't tokenised or have no pronounciation
            if ("tknorm" not in tk.attrib or "pron" not in tk.attrib or
                    tk.get("pron") is None):
                continue
            # try to apply each rule
            for rule in self.rules:
                rule.apply(pretk, tk, posttk)
            # at the end take care of pre & post tokens
            if abs(self.minoffset) > 0:
                if len(pretk) > 0:
                    pretk.pop(0)
                pretk.append(tk)
            if self.maxoffset > 0 and len(posttk) > 0:
                posttk.pop(0)
                if len(tokens) > tokens.index(tk) + self.maxoffset + 1:
                    posttk.append(tokens[tokens.index(tk)+self.maxoffset+1])


class PostLex(object):

    _modname = 'PostLex'

    def __init__(self, idargs):
        """ Creates the PostLex object and finds
            the location of postlex rules """
        if type(idargs) != idargparse.TxpArgumentParser:
            raise ValueError("idargs must be a TxpArgumentParser")

        config = pytxplib.PyTxpParseOptions_GetConfig(idargs.idlakopts)
        self.lang = config.get('general-lang', '')
        self.acc = config.get('general-acc', '')
        self.spk = config.get('general-spk', '')
        self.region = config.get('general-region', '')
        # TODO change to postlex, or creat a arch parameter for all
        self.arch = config.get('normalise-arch', '')
        self.tpdb = pyIdlak_txp.PyTxpParseOptions_GetTpdb(idargs.idlakopts)
        self._idargs = idargs

        # Getting possible directories
        normdir = ['postlex-' + self.arch, 'postlex-default']
        paths = []
        if self.spk != "" and self.acc != "" and self.lang != "":
            paths.append(os.path.join(self.lang, self.acc, self.spk))
        if self.acc != "" and self.lang != "":
            paths.append(os.path.join(self.lang, self.acc))
        if self.region != "" and self.lang != "":
            paths.append(os.path.join(self.lang, self.region))
        if self.lang != "":
            paths.append(self.lang)

        # Find existing directory
        self.ruledir = ''
        for last in normdir:
            if self.ruledir != '':
                break
            for middle_dir in paths:
                path = os.path.join(self.tpdb, middle_dir, last + ".xml")
                if os.path.exists(path):
                    self.ruledir = path
                    break

        if self.ruledir == "" and self.arch == 'default':
            raise NameError("Directory for postlex rules (\"" +
                            "%s\") could not be found." % (normdir[0]))
        elif self.ruledir == "":
            raise NameError("Directory for postlex rules (\"" +
                            "%s\" or \"%s" % (normdir[0], normdir[1]) +
                            "\") could not be found.")

    def process(self, doc):
        """ process the document in place """
        if not type(doc) is xmldoc.XMLDoc:
            raise ValueError("doc must be a XMLDoc")

        if self._idargs.get('verbose'):
            sys.stderr.write('\tLoading input\n')

        plexrules = PostlexRules(self.ruledir, self._idargs.get('verbose'))
        if len(plexrules.rules) == 0:
            if self._idargs.get('verbose'):
                sys.stderr.write('\tNo rules in postlex file, ' +
                                 'skipping postlex processing\n')
            return

        # xmldoc to lxml
        strin = str(doc.to_string())
        xmlparser = etree.XMLParser(encoding='utf8')
        xmlin = etree.fromstring(strin, parser=xmlparser)

        tokens = xmlin.xpath('.//tk')
        plexrules.runruleset(tokens)

        # lxml to xmldoc
        strout = str(etree.tostring(xmlin, encoding='utf8').decode('utf8'))
        doc.load_string(strout)

    @property
    def name(self):
        """ Gets the name of the module """
        return self._modname
