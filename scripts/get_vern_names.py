# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Get vernacular names from Bosshard and associate them with scientific / German "booknames"
in triple structure.
"""

import argparse
from tika import parser
from collections import defaultdict

def extract_from_pdf(input_file, output_file):
    raw = parser.from_file(input_file)
    #print(raw['content'])
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(raw['content'])

def main():
    argparser = argparse.ArgumentParser(description='Link found plant names to DB-entries in Catalogue of Life.')

    argparser.add_argument(
        '-i', '--input_file',
        type=str,
        default='',
        help='pass input file')

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

    args = argparser.parse_args()
    input_file = args.input_file
    geo_file = args.geo_file
    output_file = args.output_file

    triple_path_geo = "./triples/geo-vern_triples.tsv"
    triple_path_book = "./triples/book-vern_triples.tsv"
    triple_path_latin = "./triples/latin-vern_triples.tsv"


    # 1. get text data from pdf (uncomment if needed)
    # extract_from_pdf(input_file, output_file)

    # 2. get geo-vern triples from pdf
    dictio = defaultdict(int)
    geo_triples_counter = 0
    total_geotriples = []
    with open(geo_file, "r") as geo, open(triple_path_geo, "w", encoding="utf-8") as triples_geo:
        for line in geo:
            split_line = line.rstrip("\n").split(" ")
            if split_line[0].isupper():
                #print(line)
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
                print(line)
                split_line = line.rstrip("\n").split(" ")
                if len(split_line) < 2:
                    continue
                if split_line[0].islower(): # bigram
                    vernacular_name = " ".join(split_line[:2])
                    total_geotriples.append("{}\temploys_vernacular_name\t{}\n".format(canton, vernacular_name))
                    #triples_geo.write("{}\temploys_vernacular_name\t{}\n".format(canton, vernacular_name))
                    geo_triples_counter += 1
                else:
                    vernacular_name = split_line[0]
                    total_geotriples.append("{}\temploys_vernacular_name\t{}\n".format(canton, vernacular_name))
                    #triples_geo.write("{}\temploys_vernacular_name\t{}\n".format(canton, vernacular_name))
                    geo_triples_counter += 1

        print(dictio)
        print("Extracted triples: {}".format(geo_triples_counter))
        for tr in total_geotriples:
            triples_geo.write(tr)




if __name__ == '__main__':
    main()
