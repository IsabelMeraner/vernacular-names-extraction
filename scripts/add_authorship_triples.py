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
from get_vern_names import _read_stoplist


def _check_stopwords(vernacular_name, latin_stopwords):
    if vernacular_name in latin_stopwords:
        return True
    else:
        return False

def main():
    argparser = argparse.ArgumentParser(description='Extract triples AUTHOR uses_vernacular_name XY.')

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

    argparser.add_argument(
        '-l', '--latin',
        type=str,
        default='',
        help='pass stoplist gazetteer to block latin names')

    args = argparser.parse_args()
    input_file = args.input_file
    author = args.author
    output_file = args.output_file
    latin = args.latin
    latin_stopwords = _read_stoplist(latin)


    with open(input_file, "r") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        triples_counter = 0
        for line in infile:
            print(line)
            vernacular_name = line.rstrip("\n")
            if _check_stopwords(vernacular_name, latin_stopwords):
                continue
            else:
                triples_counter += 1
                outfile.write("{}\tuses_vernacular_name\t{}\n".format(author.upper(), vernacular_name))

        print("Extracted triples (unique): {}".format(triples_counter))


if __name__ == '__main__':
    main()
