# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Get vernacular names from Bosshard and associate them with scientific / German "booknames"
in triple structure.

# How to run the code:
$ python3 scripts/add_authorship_triples.py -i resources/bosshard_out_corrected.txt -o triples/authorship-vern-triples.tsv -a Bosshard_Hans_Heinrich

"""
import argparse


def main():
    argparser = argparse.ArgumentParser(description='Link found plant names to DB-entries in Catalogue of Life.')

    argparser.add_argument(
        '-i', '--input_file',
        type=str,
        default='',
        help='pass input file')

    argparser.add_argument(
        '-o', '--output_file',
        type=str,
        default='',
        help='pass output file (to overwrite)')

    argparser.add_argument(
        '-a', '--author',
        type=str,
        default='',
        help='pass author name')

    args = argparser.parse_args()
    input_file = args.input_file
    author = args.author
    output_file = args.output_file

    with open(input_file, "r") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            print(line)
            line = line.rstrip("\n")
            outfile.write("{}\tuses_vernacular_name\t{}\n".format(author.upper(), line))


if __name__ == '__main__':
    main()
