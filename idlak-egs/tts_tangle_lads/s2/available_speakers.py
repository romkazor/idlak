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

def get_readme(url):
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')

def find_speakers(readme_contents):
    pattern = re.compile("<t[dh].*>(.*)</t[dh]>\n<t[dh].*>(.*)</t[dh]>\n"
                         "<t[dh].*>(.*)</t[dh]>\n<t[dh].*>(.*)</t[dh]>\n"
                         "<t[dh].*>(.*)</t[dh]>\n<t[dh].*>(.*)</t[dh]>")

    return [[match.group(1),match.group(2),match.group(3), \
             match.group(4),match.group(5),match.group(6)] \
             for match in re.finditer(pattern,readme_contents)]

if __name__ == "__main__":
    url = "https://github.com/Idlak/Living-Audio-Dataset/blob/master/README.md"
    readme_contents = get_readme(url)
    speakers = find_speakers(readme_contents)
    for speaker in speakers:
        print("%(S)-10s%(L)-20s%(A)-25s%(G)-10s%(D)-25s%(R)-20s" \
              %{"S":speaker[0],"L":speaker[1],"A":speaker[2], \
                "G":speaker[3],"D":speaker[4],"R":speaker[5]})

