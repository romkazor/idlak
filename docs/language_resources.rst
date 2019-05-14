.. _language-resources:

#########
Languages
#########

Idlak has been designed to work with and provide examples in multiple languages.
Generally languages are referred to by their languages codes in programs.

* Language (lng) codes are `2 letter ISO_639-1 codes <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_
* Accent (acc) codes are 2 ASCII letters, see :ref:`accents`

A note on architectures: In Idlak we allow for multiple versions of resources to
sit along side one another. These are called architectures and are
in the language resource xml names after the final "-".
Idlak requires that the default architecture be defined so the file
names below all have a ``-default.xml`` ending. In general Idlak
can choose alternative architectures for individual resources.

***********************
Creating a new language
***********************

The sections below explain the required resources for languages.
Some of the resources are accent specific, these have been marked.
In general all language resources can be overridden by specific accents.

Phoneset
========

.. code-block:: none

    idlak-data/<lng>/<acc>/phoneset-default.xml

*Accent specific*

In IPA there would be multiple ways to write "r" in English, that are from a comprehension
point of view the same, but a statistical model would need to learn all of them
seperately. Alternatively nasalisation does not affect English phonemes, but they do for French.
For this reason in Idlak we use limited phonesets for each accent.
This prevents the explosion of data requirements.

Within Idlak phonemes are lower case ASCII letters, normally limited
to three characters. Numbers are used for stress and tone, so cannot be part
of a phoneme name. As much as possible different accents should use the same
symbols for equivalent phonemes.

The format for the phoneset is as follows:

.. code-block:: xml

  <phoneset language="" accent="" >
      <phone name="" ipa="" example-word="" example-pron="" syllabic="" />
      ...
  </phoneset>

Where

* **name** - The ASCII name of the phoneme
* **ipa** - The canonical IPA representation, it should be noted that multiple IPA symbols
            can be mapped onto this phoneme, but this is what should be considered the representative
            pronunciation.
* **example-word** - The canonical example word for the phoneme
* **example-pron** - The full pronunciation for the example
* **syllabic** - True if the phoneme is syllabic

Lexicon
=======

.. code-block:: none

    idlak-data/<lng>/<acc>/lexicon-default.xml

*Accent specific*

The lexicon or pronunciation dictionary lists words that have known pronunciations
using the accent specific phoneset. It is possible to have multiple pronunciations for the
same word (grapheme). The lexicon format for a single entry is as follows:

.. code-block:: xml

    <lex pron="" entry="" default="">grapheme</lex>

for example

.. code-block:: xml

    <lex pron="ih0 g z ae1 m p ah0 l" entry="full" default="true">example</lex>


Where

* **pron** - The correct pronunciation, including stress, using the Idlak phoneset.
* **entry** - A name for different pronunciations. Commonly these can be something like
              ``full``,  ``reduced``, ``noun``, or ``verb``. Alternatively these can
              be numbers to indicate multiple correct pronunciations. The allows for
              homograph resolution and  for the user to change which entry is spoken in
              the input.
* **default** - Which entry should be pronounced given no other information,
                one and only one entry must be true.

The overall format for the lexicon is:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <lexicon>
        <lex pron="a0" entry="full" default="true">а</lex>
        ..
    </lexicon>

The lexicon has an optional ``name`` attribute.


Syllabification rules
=====================

.. code-block:: none

    idlak-data/<lng>/<acc>/sylmax-default.xml


LTS rules
=========

.. code-block:: none

    idlak-data/<lng>/<acc>/ccart-default.xml

*Accent specific*

Currently the Idlak front-end uses cart trees for letter-to-sound rules.

We have a script that can automatically generate this file from the lexicon, using
`Phonetisaurus <https://github.com/AdolfVonKleist/Phonetisaurus>`_.
(Fill in the path, language code, and accent code)

.. code-block:: none

    IDIR=<path to idlak>
    cd $IDIR/idlak-misc/cart_lts
    ./run.sh -l $IDIR/idlak-data/<lng>/<acc>/lexicon-default.xml \
             -s $IDIR/idlak-data/<lng>/<acc>/sylmax-default.xml \
             -p $IDIR/idlak-data/<lng>/<acc>/phoneset-default.xml \
             -o $IDIR/idlak-data/<lng>/<acc>/ccart-default.xml



Tokeniser rules
===============

.. code-block:: none

    idlak-data/<lng>/trules-default.xml

The tokeniser rules govern how text is split into individual tokens. These
are a series of regular expression (PCRE) that govern what is considered to be
letters, numbers, etc. All of the rules are mandatory. A rule is of the form:

.. code-block:: xml

    <regex name="matches a name in the tokeniser">
        <comment>
            Description as to the purpose of the rule and any interesting
            things about this language's version.
        </comment>
        <exp>
            <![CDATA[regex]>
        </exp>
    </regex>


The list of rules understood and required by the tokeniser is as follows:

* **whitespace** what is considered to be whitespace in the language
* **separators** characters that should always be put on their own token
* **alpha** the lower and uppercase letters of that language, note that you do not need to include diacritics
* **downcase** the mapping from uppercase to lowercase letters
* **decompose** lookup for utf8 decomposition into NFD form see
    `Unicode_equivalence <https://en.wikipedia.org/wiki/Unicode_equivalence>`_.
    This can be generated automatically from the lexicon.
* **convertillegal** a lookup for changing characters from one form to another
    especially useful for converting utf8 characters to ascii versions, ensuring and for
    stripping diacritics that are not part of the language.

* **utfpunc2ascii** a lookup for converting alternative utf-8 versions of punctuation to ascii versions
* **asdigits** The names in the language of numerals. (See the Normaliser rules about this)
* **symbols** The names in the language of symbols. (See the Normaliser rules about this)

In general you can copy the English one and make a few modifications.


Normalizer rules
================

**Whole language**:

.. code-block:: none

    idlak-data/<lng>/hrules-default.py  # hard coded rules
    idlak-data/<lng>/nrules-default/master.xml # Normalizer setup file
    idlak-data/<lng>/nrules-default/lookuptables.xml # Lookup table definitions
    idlak-data/<lng>/nrules-default/*.xml # rules

Hard coded rules
----------------

The normalizer can invoke hard coded rules. As currently the normalizer is written
in Python these rules are in a Python file that is loaded at runtime. In the future
this may change to a c++ source file.
If the hard coded rules file does not exist then the normaliser will assume there
are non. It should be noted this will drastically slow down the normaliser.

The key requirement as it stands is that the file defines a dictionary called ``NORMFUNCS``.
The hard coded functions must have the following function signature:

.. code:: python

  def function_name(norm, string, args):
    # norm = using normaliser defined by a Normrules
    # string = string to normalise
    # args = additional arguments in a dictionary


For example a common rule is to read out number as a sequence of individual digits,
normally called ``asdigits``. This version uses the normaliser's lookup tables.
In general it is better to put the lookup tables in the normaliser files rather than
hard code them.

.. code:: python

  def asdigits(norm, string, args):
    lkptable_name = 'digitlkp'
    if args.get('case', None) is not None:
      lkptable_name = args['case']
    lkptable = norm.lkps.get(lkptable_name, norm.lkps['digitlkp'])
    result = ''
    for c in string:
      if c in lkptable:
        result.append(lkptable[c])
    return ' '.join(result)

The dictionary then takes the form:

.. code:: python

    NORMFUNCS = {
        'asdigits' : asdigits,
        'aschars' : aschars,
        ...
        'function_name' : function
    }

Normally it is fine to just copy an existing language's one.

Normalizer Master File
----------------------

The normalizer master file controls which rules are included, their precedence,
and the available replacement functions.

.. code-block:: xml

    <nrules>
      <replacefunction>
        <function name="function_name" arg1 = "val1" arg2 = "val2" />
        <function name="function_name2"  /> <!-- no arguments -->
        ...
      </replacefunction>
      <ruleset>
        <rs name = "rulesetname" /> <!-- matches rule file name -->
        <rs name = "rulesetname2" />
        ...
      </ruleset>
    </nrules>

The replacement functions are normally in the hard coded rules. The name refers
to the fact that they replace text during normalisation. Some common ones are:

* ``aschars`` - letter and symbol names
* ``asdigits`` - the individual digits
* ``number`` - converting to number names if the digits are one big number
* ``roman`` - Roman numerals
* ``filter`` - combines the others

The ruleset (elements ``rs``) give an ordered list of rules to run. They are always
run in the given order. Once some text has been normalised within a rule set it will
not be normalized a second time, until the next rule set starts. The ruleset names
must match the file name of the ruleset in the same directory as the master file.


Lookup Tables
-------------


XML Rules
---------



Part of speech set and rules
============================




Abbreviations
=============




Phrasing rules
==============




Context extraction rules
========================




*******************
Available languages
*******************

* English
* Dutch
* Russian
