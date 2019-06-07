# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Use information stored in json files to generate rdf-triples using the python rdf package.

Expected format:
@prefix :        <https://bio.isabelmeraner.name/ontology#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://vernbacular/312> rdf:type :NameOccurence.
<http://vernbacular/312> rdf:value "Schnääball".
<http://vernbacular/312> :areaFine "Wädenswil" .
<http://vernbacular/312> :taxon <http://taxon-concept.plazi.org/id/Plantae/Viburnum_lantana> .
<http://vernbacular/312> :vernacularNamestatus :localName .
<http://vernbacular/312> :source <https://doi.org/10.5169/seals-664049> .

<http://vernbacular/394> rdf:type :NameOccurence.
<http://vernbacular/394> rdf:value "Wolliger Schneeball".
<http://vernbacular/394> :areaCourse "DACHLST" .
<http://vernbacular/394> :taxon <http://taxon-concept.plazi.org/id/Plantae/Viburnum_lantana> .
<http://vernbacular/394> :vernacularNamestatus :bookName .

# How to run the code:
$ python3 scripts/generate_rdf_triples.py -j ./json/ -r ./triples_v2.rdf

"""
import argparse
import os
import json
import sys
import rdflib
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF


def load_json_data(json_dir):
    data_storage = dict()
    for fn in os.listdir(json_dir):
        with open(json_dir + fn, 'r') as json_f:
            data_storage[fn.split(".")[0]] = json.load(json_f)
    print(data_storage.keys())
    return data_storage


def _build_ID(ID):
    ID_temp = "http://vernacular/{}".format(ID)
    ID_URI = URIRef(ID_temp)

    return ID_URI


def add_locations(g, subdict, v_name, ID_URI, area_URI, url=False):
    base_plazi_taxon_url = "http://taxon-concept.plazi.org/id/Plantae/"  # <http://taxon-concept.plazi.org/id/Plantae/Viburnum_lantana>

    if subdict.get(v_name):
        for i, area in enumerate(subdict[v_name]):
            # print(v_name, canton)
            if url:
                plazi_uri = URIRef("{}{}".format(base_plazi_taxon_url, subdict[v_name][i]))
                g.add((ID_URI, area_URI, plazi_uri))
            else:
                area = area.replace(" ", "_")
                g.add((ID_URI, area_URI, Literal(area)))
    else:
        pass

def add_graph_statements(ID_URI, g, name, Name_URI):
    DOI = "https://doi.org/10.5281/zenodo.293746"
    source_URI = URIRef(":source")
    status_URI = URIRef(":vernacularNameStatus")
    DOI_URI = URIRef(DOI)
    type_URI = URIRef(":NameOccurence")
    name = name.replace(" ", "_")

    g.add((ID_URI, RDF.type, type_URI))
    g.add((ID_URI, RDF.value, Literal(name)))
    g.add((ID_URI, source_URI, DOI_URI))
    g.add((ID_URI, status_URI, Name_URI))


def main():
    argparser = argparse.ArgumentParser(description='Extract triples CANTON uses_vernacular_name XY')

    argparser.add_argument(
        '-j', '--json_directory',
        type=str,
        default='',
        help='json_directory containing json files with triple information')

    argparser.add_argument(
        '-r', '--rdf_outfile',
        type=str,
        default='',
        help='path for rdf output file')

    args = argparser.parse_args()
    json_dir = args.json_directory
    rdf_target = args.rdf_outfile

    data_storage = load_json_data(json_dir)

    PREFIX = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """

    areaGlobal_URI = URIRef(":areaGlobal")
    areaCoarse_URI = URIRef(":areaCoarse")
    areaFine_URI = URIRef(":areaFine")

    taxon_URI = URIRef(":taxon")
    localName_URI = URIRef(":localName")
    bookName_URI = URIRef(":bookName")

    area_global = "DACHLS"  # Germany, Austris,Switzerland, Liechtenstein, South Tyrol

    all_booknames = set()
    found_booknames = set()

    g = Graph()

    for scientific_name, booknames in data_storage["lat-book"].items():
        for bookname in booknames:
            all_booknames.add(bookname)

    with open("./resources/authorship-vern-triples_unique_sorted.tsv", "r") as vern_names:
        ID = 0
        for line in vern_names:
            author, pred, v_name = line.rstrip("\n").split("\t")

            if v_name in all_booknames:
                #print(v_name)
                found_booknames.add(v_name)

                ID += 1
                ID_URI = _build_ID(ID)

                add_graph_statements(ID_URI, g, v_name, bookName_URI)
                add_locations(g, data_storage["vern-lat"], v_name, ID_URI, taxon_URI, url=True)
                add_locations(g, data_storage["vern-canton"], v_name, ID_URI, areaCoarse_URI)
                add_locations(g, data_storage["vern-loc"], v_name, ID_URI, areaFine_URI)
                g.add((ID_URI, areaGlobal_URI, Literal(area_global)))

            ID += 1
            ID_URI = _build_ID(ID)

            add_graph_statements(ID_URI, g, v_name, localName_URI)
            add_locations(g, data_storage["vern-lat"], v_name, ID_URI, taxon_URI, url=True)
            add_locations(g, data_storage["vern-canton"], v_name, ID_URI, areaCoarse_URI)
            add_locations(g, data_storage["vern-loc"], v_name, ID_URI, areaFine_URI)

        missing_booknames = all_booknames.difference(found_booknames)
        for scientific_name, booknames in data_storage["lat-book"].items():
            for bookname in booknames:
                if bookname in missing_booknames:
                    ID += 1
                    ID_URI = _build_ID(ID)

                    add_graph_statements(ID_URI, g, bookname, bookName_URI)

                    add_locations(g, data_storage["vern-lat"], bookname, ID_URI, taxon_URI, url=True)
                    add_locations(g, data_storage["vern-canton"], bookname, ID_URI, areaCoarse_URI)
                    add_locations(g, data_storage["vern-loc"], bookname, ID_URI, areaFine_URI)
                    g.add((ID_URI, areaGlobal_URI, Literal(area_global)))

    g.serialize(destination=rdf_target, format='n3') # format='turtle'
    print(">> final graph has been serialized with '{}' statements.".format(len(g)))


if __name__ == '__main__':
    main()
