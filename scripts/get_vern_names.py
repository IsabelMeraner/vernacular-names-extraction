# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Get vernacular names from Bosshard and associate them with scientific / German "booknames"
in triple structure.

# How to run the code:
$ python3 scripts/get_vern_names.py -i resources/geo-latin-vernacular.txt -o triples/geo-vern_triples.tsv -g resources/geo-latin-vernacular.txt -s stoplist/swisstopo_short.txt -l stoplist/lat_genus.txt

"""

import argparse
from tika import parser
from collections import defaultdict


def extract_from_pdf(input_file, output_file):
    raw = parser.from_file(input_file)
    # print(raw['content'])
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(raw['content'])


def get_triples(geo, geo_stopwords, latin_stopwords):
    dictio = defaultdict(int)
    geo_triples_counter = 0
    total_geotriples = set()

    for line in geo:
        split_line = line.rstrip("\n").rstrip(",").split(" ")
        if split_line[0].isupper():
            # print(line)
            dictio[" ".join(split_line)] += 1
            canton = " ".join(split_line)
            if canton == "KANTON BASEL-LANDSCHAFT":
                if total_geotriples:
                    total_geotriples.pop()
                else:
                    continue

        elif line == "\n":
            continue
        elif line.rstrip("\n").isdigit():
            continue
        else:
            # print(line)
            split_line = line.rstrip("\n").split(" ")
            if len(split_line) < 2:
                print(line)
                continue
            if split_line[0].islower():  # bigram
                vernacular_name = " ".join(split_line[:2])
                if _check_vern_name(vernacular_name):
                    continue
                elif _check_stopwords(vernacular_name, geo_stopwords, latin_stopwords):
                    continue
                else:
                    total_geotriples.add("{}\tuses_vernacular_name\t{}\n".format(canton, vernacular_name))
                    geo_triples_counter += 1
            else:
                vernacular_name = split_line[0]
                if _check_vern_name(vernacular_name):
                    continue
                elif _check_stopwords(vernacular_name, geo_stopwords, latin_stopwords):
                    continue
                else:
                    total_geotriples.add("{}\tuses_vernacular_name\t{}\n".format(canton, vernacular_name))
                    geo_triples_counter += 1

    return total_geotriples, geo_triples_counter, dictio


def _check_vern_name(vernacular_name):
    if "Bez." in vernacular_name or vernacular_name.endswith(",") or vernacular_name.isdigit():
        return True
    else:
        return False


def _check_stopwords(vernacular_name, geo_stopwords, latin_stopwords):
    if vernacular_name in geo_stopwords or vernacular_name in latin_stopwords:
        return True
    else:
        return False


def _read_stoplist(stoplist):
    with open(stoplist, "r") as stopfile:
        return {name.rstrip("\n") for name in stopfile}


def main():
    argparser = argparse.ArgumentParser(description='Extract triples CANTON uses_vernacular_name XY')

    argparser.add_argument(
        '-i', '--input_file',
        type=str,
        default='',
        help='pass input file (original PDF)')

    argparser.add_argument(
        '-g', '--geo_file',
        type=str,
        default='',
        help='pass input file with geo snippet')

    argparser.add_argument(
        '-o', '--output_file',
        type=str,
        default='',
        help='pass output file (to overwrite)')

    argparser.add_argument(
        '-s', '--stoplist',
        type=str,
        default='',
        help='pass stoplist gazetteer to block geogr. names')

    argparser.add_argument(
        '-l', '--latin',
        type=str,
        default='',
        help='pass stoplist gazetteer to block latin names')

    args = argparser.parse_args()
    input_file = args.input_file
    output_file = args.output_file

    geo_file = args.geo_file
    stoplist = args.stoplist
    latin = args.latin

    geo_stopwords = _read_stoplist(stoplist)
    latin_stopwords = _read_stoplist(latin)

    triple_path_geo = "./triples/geo-vern_triples.tsv"
    #triple_path_book = "./triples/book-vern_triples.tsv"
    #triple_path_latin = "./triples/latin-vern_triples.tsv"

    # 1. get text data from pdf (uncomment if needed)
    # extract_from_pdf(input_file, output_file)

    # 2. get geo-vern triples from pdf
    with open(geo_file, "r") as geo, open(triple_path_geo, "w", encoding="utf-8") as triples_geo:
        total_geotriples, geo_triples_counter, dictio = get_triples(geo, geo_stopwords, latin_stopwords)

        print("Extracted names from cantons: \n", dictio, end="\n\n")
        print("Extracted triples (not unique): {}".format(geo_triples_counter))

        # write triples to geo-triple file in triples/geo-vern_triples.tsv
        unique_triples = 0
        for tr in total_geotriples:
            unique_triples += 1
            triples_geo.write(tr)
        print("Extracted triples (unique): {}".format(unique_triples))


if __name__ == '__main__':
    main()
