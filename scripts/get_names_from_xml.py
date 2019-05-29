# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Get vernacular names from Bosshard (XML) and associate them with scientific / German "booknames"
in triple structure.

# How to run the code:
$ python3 scripts/get_names_from_xml.py -i resources/pdf2txt_bosshard_extracted.xml -o triples/authorship-vern-triples.tsv -a Bosshard_Hans_Heinrich

"""
import argparse
import lxml.etree as ET
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

    # argparser.add_argument(
    #     '-l', '--latin',
    #     type=str,
    #     default='',
    #     help='pass stoplist gazetteer to block latin names')

    args = argparser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    #latin = args.latin
    #latin_stopwords = _read_stoplist(latin)


    with open(input_file, "rb") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for _, textline in ET.iterparse(infile, tag='textline'):
            print(textline)
            line = []
            for text_char in textline.iterfind('.//text'):
                #print(text_char.text)
                line.append(text_char.text)

            line_str = "".join(line)
            print(line_str)
            outfile.write("{}\n".format(line_str))
            line.clear()
            #title = article.findtext('.//ArticleTitle')
            #year = article.findtext('.//ArticleDate/Year')
            #authors = ', '.join(name.text for name in article.iterfind('.//AuthorList/Author/LastName'))
            #yield authors, year, title
            #article.clear()  # jeweils Knoten, der verarbeitet wurde verwerfen!

if __name__ == '__main__':
    main()
