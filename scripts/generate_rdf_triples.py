# usr/bin/env python3
# author: Isabel Meraner
# Project: Extraction of vernacular names from Bosshard (1978)
# 2019

"""
Use information stored in json files to generate rdf-triples using the python rdf package.

Expected format:
@prefix :        <https://bio.isabelmeraner.name/ontology#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://vernbacular/312> rdf:type :NameOccurrence.
<http://vernbacular/312> rdf:value "Schnääball".
<http://vernbacular/312> :areaFine "Wädenswil" .
<http://vernbacular/312> :taxon <http://taxon-concept.plazi.org/id/Plantae/Viburnum_lantana> .
<http://vernbacular/312> :vernacularNamestatus :localName .
<http://vernbacular/312> :source <https://doi.org/10.5169/seals-664049> .

<http://vernbacular/394> rdf:type :NameOccurrence.
<http://vernbacular/394> rdf:value "Wolliger Schneeball".
<http://vernbacular/394> :areaCourse "DACHLST" .
<http://vernbacular/394> :taxon <http://taxon-concept.plazi.org/id/Plantae/Viburnum_lantana> .
<http://vernbacular/394> :vernacularNamestatus :bookName .

# How to run the code:
$ python3 scripts/generate_rdf_triples.py -j ./json/ -r ./triples/triples_v3_n3.ttl

"""
import argparse
import os
import json
from collections import defaultdict
from itertools import chain
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF


def load_geo_information(geo_dir):
    geo_storage = defaultdict(list)
    with open(geo_dir, "r") as geo_file:
        for line in geo_file:
            loc, canton = line.rstrip("\n").split("\t")
            geo_storage[canton].append(loc)

    return geo_storage


def load_json_data(json_dir):
    data_storage = dict()
    for fn in os.listdir(json_dir):
        with open(json_dir + fn, 'r') as json_f:
            data_storage[fn.split(".")[0]] = json.load(json_f)

    data_storage["book-lat"] = defaultdict(list)
    for lat_name, book_names in data_storage["lat-book"].items():
        for book_name in book_names:
            data_storage["book-lat"][book_name].append(lat_name)

    for n, l in data_storage["vern-lat"].items():
        data_storage["vern-lat"][n] = list(set(l))

    for n, l in data_storage["book-lat"].items():
        data_storage["book-lat"][n] = list(set(l))

    data_storage["names-lat"] = defaultdict(list)
    for k, v in chain(data_storage["book-lat"].items(), data_storage["vern-lat"].items()):
        data_storage["names-lat"][k].extend(v)

    return data_storage


def _build_ID(ID):
    ID_temp = "https://vernacular.plazi.org/{}".format(ID)  # @TODO: TBD which URL/URI to use?
    ID_URI = URIRef(ID_temp)

    return ID_URI


def has_latin_name(subdict, v_name):
    if subdict.get(v_name):
        return True
    return False


def add_graph_statements(g, ID_URI, v_name, Name_URI, data_storage, i_lat, areaCoarse, areaFine):
    DOI = "https://doi.org/10.5281/zenodo.293746"
    source_URI = URIRef(":source")
    status_URI = URIRef(":vernacularNameStatus")
    DOI_URI = URIRef(DOI)
    type_URI = URIRef(":NameOccurrence")
    areaGlobal_URI = URIRef(":areaGlobal")
    areaCoarse_URI = URIRef(":areaCoarse")
    areaFine_URI = URIRef(":areaFine")
    taxon_URI = URIRef(":taxon")
    area_global = "DACHLS"  # Germany, Austris,Switzerland, Liechtenstein, South Tyrol
    base_plazi_taxon_url = "http://taxon-concept.plazi.org/id/Plantae/"

    g.add((ID_URI, RDF.type, type_URI))
    g.add((ID_URI, RDF.value, Literal(v_name)))
    g.add((ID_URI, source_URI, DOI_URI))
    g.add((ID_URI, status_URI, Name_URI))
    g.add((ID_URI, areaGlobal_URI, Literal(area_global)))

    # ADD LATIN NAME
    plazi_uri = URIRef(
        "{}{}".format(base_plazi_taxon_url, data_storage["names-lat"][v_name][i_lat]))
    g.add((ID_URI, taxon_URI, plazi_uri))

    # ADD CANTON
    g.add((ID_URI, areaCoarse_URI, Literal(areaCoarse)))

    # ADD LOC
    g.add((ID_URI, areaFine_URI, Literal(areaFine)))


def add_information(g, data_storage, geo_storage, v_name, ID, Name_URI, standalone_loc):
    if has_latin_name(data_storage["names-lat"], v_name):
        #print("has lat name!", v_name, data_storage["names-lat"][v_name])
        for i_lat, lat_name in enumerate(data_storage["names-lat"][v_name]):
            #print(i_lat, v_name, lat_name)

            if data_storage["vern-canton"].get(v_name):
                for i_canton, areaCoarse in enumerate(data_storage["vern-canton"][v_name]):
                    areaCoarse = areaCoarse.replace("_", " ")
                    areaCoarse = " ".join([part.capitalize() for part in areaCoarse.split(" ")])
                    #print("adding canton {} for name {}".format(i_canton, areaCoarse, v_name))

                    if data_storage["vern-loc"].get(v_name):
                        for i_loc, areaFine in enumerate(data_storage["vern-loc"][v_name]):
                            areaFine = areaFine.replace("_", " ")
                            areaFine = " ".join([part.capitalize() for part in areaFine.split(" ")])
                            #print("adding locaton {} for name {}".format(i_loc, areaFine, v_name))

                            # print(areaFine, areaCoarse, geo_storage[areaCoarse])
                            if areaFine in geo_storage[areaCoarse]:
                                ID += 1
                                ID_URI = _build_ID(ID)
                                print("initialising instance for: ", v_name, Name_URI, areaCoarse, areaFine,
                                      data_storage["names-lat"][v_name][i_lat])
                                add_graph_statements(g, ID_URI, v_name, Name_URI, data_storage, i_lat, areaCoarse,
                                                     areaFine)
                            else:
                                # print("not found in geo storage: ", i_loc, areaFine)
                                #continue
                                if standalone_loc.get(v_name):
                                    if areaFine in standalone_loc[v_name]:
                                        continue
                                    else:
                                        FOUND = False
                                        for c, loc in geo_storage.items():
                                            if areaFine in loc:
                                                FOUND = True
                                        if not FOUND:
                                            ID += 1
                                            ID_URI = _build_ID(ID)
                                            add_graph_statements(g, ID_URI, v_name, Name_URI, data_storage, i_lat, "",
                                                                 areaFine)
                                            standalone_loc[v_name].append(areaFine)
                                else:
                                    FOUND = False
                                    for c, loc in geo_storage.items():
                                        if areaFine in loc:
                                            FOUND = True
                                    if not FOUND:
                                        ID += 1
                                        ID_URI = _build_ID(ID)
                                        add_graph_statements(g, ID_URI, v_name, Name_URI, data_storage, i_lat, "",
                                                             areaFine)
                                        standalone_loc[v_name].append(areaFine)


    return ID


def get_booknames(data_storage):
    all_booknames = set()
    for scientific_name, booknames in data_storage["lat-book"].items():
        for bookname in booknames:
            all_booknames.add(bookname)
    return all_booknames


def main():
    argparser = argparse.ArgumentParser(description='Extract triples CANTON uses_vernacular_name XY')

    argparser.add_argument(
        '-j', '--json_directory',
        type=str,
        default='./../json/',
        help='json_directory containing json files with triple information')

    argparser.add_argument(
        '-r', '--rdf_outfile',
        type=str,
        default='./../triples/triples_v5_n3.ttl',
        help='path for rdf output file')

    args = argparser.parse_args()
    json_dir = args.json_directory
    rdf_target = args.rdf_outfile

    data_storage = load_json_data(json_dir)

    localName_URI = URIRef(":localName")
    bookName_URI = URIRef(":bookName")

    geo_dir = "../resources/loc-cantons.tsv"
    geo_storage = load_geo_information(geo_dir)

    found_booknames = set()
    standalone_loc = defaultdict(list)
    all_booknames = get_booknames(data_storage)

    g = Graph()
    # http://purl.org/net/vern-names

    with open("../resources/authorship-vern-triples_unique_sorted.tsv", "r") as vern_names:
        ID = 0
        for line in vern_names:
            author, pred, v_name = line.rstrip("\n").split("\t")

            if v_name in all_booknames:
                #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> bookname", v_name)
                found_booknames.add(v_name)
                ID = add_information(g, data_storage, geo_storage, v_name, ID, bookName_URI, standalone_loc)
            else:
                #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> local name", v_name)
                ID = add_information(g, data_storage, geo_storage, v_name, ID, localName_URI, standalone_loc)

        missing_booknames = all_booknames.difference(found_booknames)
        for scientific_name, booknames in data_storage["lat-book"].items():
            for bookname in booknames:
                if bookname in missing_booknames:
                    #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> missing bookname", bookname)
                    ID = add_information(g, data_storage, geo_storage, bookname, ID, bookName_URI, standalone_loc)

    g.serialize(destination=rdf_target, format='n3')  # format='turtle'
    print(">> final graph has been serialized with '{}' statements.".format(len(g)))


if __name__ == '__main__':
    main()
