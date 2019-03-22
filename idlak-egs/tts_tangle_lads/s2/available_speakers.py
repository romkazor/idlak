#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Cereproc Ltd. (author: Caoimhín Laoide-Kemp)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

import urllib.request
import re
import os

def get_readme(url):
    with urllib.request.urlopen(url) as response:
        contents = response.read().decode('utf-8')
    return contents

def find_speakers(contents):
    pattern = re.compile("<t[dh].*>(.*)</t[dh]>\n<t[dh].*>(.*)</t[dh]>\n"
                         "<t[dh].*>(.*)</t[dh]>\n<t[dh].*>(.*)</t[dh]>\n"
                         "<t[dh].*>(.*)</t[dh]>\n<t[dh].*>(.*)</t[dh]>")

    for match in re.finditer(pattern,contents):
        print("%(S)-10s%(L)-20s%(A)-25s%(G)-10s%(D)-25s%(R)-20s" \
                %{"S":match.group(1),"L":match.group(2),"A":match.group(3), \
                "G":match.group(4),"D":match.group(5),"R":match.group(3)})

    return

def delete_file(filename):
    os.remove(filename)
    return

if __name__ == "__main__":
    url = "https://github.com/Idlak/Living-Audio-Dataset/blob/master/README.md"
    contents = get_readme(url)
    find_speakers(contents)
