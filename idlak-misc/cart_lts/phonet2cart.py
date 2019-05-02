#!/usr/bin/env python3

import os
import re
import argparse
import collections

def make_cart_entries(line, phone_groups, entry_dict, stress_list, wl=8):
    # Splits line up into grapheme/phone pairs
    groups = line.split()

    # Extracts the graphemes and combines them to create the word padded by #'s
    # to ensure that there is enough context to be printed
    letters = re.subn("}[^ ]+", "", line)[0].replace("|"," ").replace("_","").split()
    word = ['#'] * wl + letters + ['#'] * wl
    if "'" not in word:
        offset = 0
        for group in groups:
            # Splits grapheme/phone pairs into their two parts
            lg = group.split("}")

            # Ignore any phones that do not have a corresponding grapheme
            if lg[0] == "_":
                continue

            # Take care of graphemes that map onto nothing
            if lg[1] == "_":
                lg[1] = "0"

            # Separate any graphemes/phones that are part of a many-to-one or
            # one-to-many mapping
            graphemes = lg[0].split("|")
            phones = lg[1].split("|")

            stress_levels = ["0","1","2"]
            stress = "0 "
            vowel = False

            # Determine if phone group contains a vowel, and remove stress to
            # be processed separately
            # Stress is only removed for the last vowel in the phone group
            for index,phone in reversed(list(enumerate(phones))):
                for stress_level in stress_levels:
                    if stress_level in phone and phone != "0":
                        vowel = True
                        phones[index] = phone.replace(stress_level,"0")
                        stress = stress_level + " "
                        break
                if vowel:
                    break

            # Add phone_group to set of phones that can be mapped to a single
            # grapheme
            phone_groups.add("_".join(phones))

            # Moving window that creates a cart entry for each grapheme in the word,
            # padded by the correct number of #'s
            for i, grapheme in enumerate(graphemes):
                if i < len(graphemes) - 1:
                    output = "0"
                else:
                    output = "_".join(phones)
                stress_output = stress + " ".join(word[offset:offset + wl * 2 + 1])
                output_line = " ".join([output] + word[offset:offset + wl * 2 + 1])
                entry_dict[grapheme].append(output_line)
                if vowel:
                    stress_list.append(stress_output)
                offset += 1

def main():
    arg_parser = argparse.ArgumentParser(
            description="Necessary arguments")
    arg_parser.add_argument("-o", "--outdir", default = os.getcwd(),
                            help = "output directory")
    arg_parser.add_argument("alignment_file",
                            type = argparse.FileType('r', encoding='utf-8'),
                            help = "Alignment file from Phonetisaurus")
    args = arg_parser.parse_args()

    align_file = args.alignment_file
    outdir = args.outdir

    os.makedirs(outdir, exist_ok = True)

    entry = collections.defaultdict(list)
    stress = []
    phone_groups = set()
    for line in align_file:
        make_cart_entries(line, phone_groups, entry, stress)

    # Create and write .cart file for each letter
    for letter in entry.keys():
        if letter != "'":
            with open(os.path.join(outdir, letter + ".cart"), "w", encoding = 'utf-8') as lf:
                lf.write("\n".join(entry[letter]))

    # Create and write stress.cart
    with open(os.path.join(outdir, "stress.cart"), "w", encoding='utf-8') as sf:
        for stress_entry in stress:
            sf.write(stress_entry+"\n")

    # Create and write wagon file
    with open(os.path.join(outdir, "wagon_description.dat"), "w", encoding = 'utf-8') as wf:
        wf.write("(\n( phone\n0\n1\n2\n")
        for phone_group in phone_groups:
            if phone_group != "0":
                wf.write(phone_group + "\n")
        wf.write(")\n")
        for i in range(8,-1,-1):
            wf.write("( " + "p."*i + "name\n#\n0\n")
            for letter in entry.keys():
                if letter != "'" and letter != "0":
                    wf.write(letter + "\n")
            wf.write(")\n")
        for i in range(1,9):
            wf.write("( " + "n."*i + "name\n#\n0\n")
            for letter in entry.keys():
                if letter != "'" and letter != "0":
                    wf.write(letter + "\n")
            wf.write(")\n")
        wf.write(")")

if __name__=="__main__":
    main()
