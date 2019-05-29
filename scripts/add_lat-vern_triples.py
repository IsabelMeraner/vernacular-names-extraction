# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Get vernacular names from Bosshard (XML) and associate them with scientific / German "booknames"
in triple structure.

# How to run the code:
$ python3 scripts/add_lat-vern_triples.py -i resources/lat-bookname-vernacular.txt -o triples/
"""
import argparse
from collections import defaultdict
import json
import os


def _check_stopwords(vernacular_name, latin_stopwords):
    if vernacular_name in latin_stopwords:
        return True
    else:
        return False


def _split_author(line):
    try:
        line.split("L.")
        return True
    except:
        return False


def _clean_string(name):
    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]
    print(name)
    for n_rom in romans:
        name = name.replace(n_rom, "")
    print(name)
    name = ''.join(c for c in name if c == "-" or c.isalpha() or c == " ")
    print(name)

    return name.lstrip(" ").rstrip(" ")


def main():
    argparser = argparse.ArgumentParser(description='Extract triples AUTHOR uses_vernacular_name XY.')

    argparser.add_argument(
        '-i', '--input_file',
        type=str,
        default='resources/lat-bookname-vernacular.txt',
        help='pass input file')

    argparser.add_argument(
        '-o', '--output_path',
        type=str,
        default='path/',
        help='pass output file (to overwrite)')

    args = argparser.parse_args()
    input_file = args.input_file
    path_out = args.output_path

    alternative_author_names = ["(L.) Crantz", "L.", "Ehrh.", "Ehr.", "Mill.", "Milk", "Gleditsch", "Huds."]

    with open(input_file, "r") as infile:
        lat_booknames = defaultdict(list)
        lat_vernnames = defaultdict(list)
        vern_latnames = defaultdict(list)

        for index, line in enumerate(infile):
            print(index)
            line = line.rstrip("\n")

            if any(n in line for n in alternative_author_names):
                for author_name in alternative_author_names:
                    try:
                        lname, bname = line.split(author_name)
                        latname = lname.replace("(", "")
                        bname = bname.replace(")", "")
                        bookname = bname.replace("Crantz ", "")
                        genus, *epithets = latname.split(" ")
                        formatted_latname = "{}_{}".format(genus, " ".join([epi.lower() for epi in epithets]).lstrip(
                            " ").rstrip(" "))

                        if "," in bookname:
                            bname1, *rest_bnames = bookname.split(", ")
                            bname1 = _clean_string(bname1)
                            #outfile.write("{}\thas_vernacular_name\t{}\n".format(formatted_latname, bname1))
                            if bname1:
                                lat_booknames[formatted_latname].append(bname1)

                            for add_name in rest_bnames:
                                add_name = _clean_string(add_name)
                                #outfile.write("{}\thas_vernacular_name\t{}\n".format(formatted_latname, add_name))
                                if add_name:
                                    lat_booknames[formatted_latname].append(add_name)

                        elif bookname == "":
                            bookname = "<unknown>"
                            #outfile.write("{}\thas_vernacular_name\t{}\n".format(formatted_latname, bookname))

                        else:
                            bookname = _clean_string(bookname)
                            #outfile.write("{}\thas_vernacular_name\t{}\n".format(formatted_latname, bookname))
                            if bookname:
                                lat_booknames[formatted_latname].append(bookname)

                        # print("latin name: {} {} - bookname: {}".format(genus, " ".join([epi.lower() for epi in epithets]), bookname))
                    except:
                        if line == "\n":
                            continue
                        elif line.split(" ")[0].rstrip(",").rstrip(";").rstrip(",").isdigit():
                            continue
                        elif line.isdigit():
                            continue
                        else:
                            # print("insiide any", line, type(line))
                            continue

            else:
                romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]
                if line == "\n":
                    continue
                elif line.split(" ")[0].rstrip(",").rstrip(";").rstrip(",").isdigit():
                    continue
                elif line.isdigit():
                    continue
                # @TODO: filter roman numbers
                elif line in romans:
                    continue
                else:
                    # print("outside any", line, type(line))
                    if "," in line:
                        vern1, *rest_vern = line.split(", ")
                        clean_vern = _clean_string(vern1)
                        #outfile.write("{}\thas_vernacular_name\t{}\n".format(formatted_latname, clean_vern))
                        if clean_vern:
                            lat_vernnames[formatted_latname].append(clean_vern)
                            vern_latnames[clean_vern].append(formatted_latname)

                        for vern in rest_vern:
                            clean_vern = _clean_string(vern)
                            #outfile.write("{}\thas_vernacular_name\t{}\n".format(formatted_latname, clean_vern))

                            if clean_vern:
                                lat_vernnames[formatted_latname].append(clean_vern)
                                vern_latnames[clean_vern].append(formatted_latname)

                    continue

    print("lat-book:\n{}".format(len(lat_booknames)))
    print("lat-vern:\n{}".format(len(lat_vernnames)))
    print("vern-lat:\n{}".format(len(vern_latnames)))

    book_out = os.path.join(path_out, 'lat-book.json')
    with open(book_out, 'w') as fp:
        json.dump(lat_booknames, fp)

    vern_out = os.path.join(path_out, 'lat-vern.json')
    with open(vern_out, 'w') as fp:
        json.dump(lat_vernnames, fp)

    vern_lat_out = os.path.join(path_out, 'vern-lat.json')
    with open(vern_lat_out, 'w') as fp:
        json.dump(vern_latnames, fp)


if __name__ == '__main__':
    main()
