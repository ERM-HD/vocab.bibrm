vocab.bibrm
===========

Vocabulary for Bibliographical Electronic Resource Management
------------------------------------------------------------

Status of this Document: draft

This work is in progress and will change from time to time. If you are interested in managing electronic resources in libraries don't hasitate to ask.

We are still collecting and searching ideas from existing vocabularies and models like:
* [ecpo](https://github.com/cKlee/ecpo)
* [bibo](http://bibliontology.com/)
* [holding](https://github.com/dini-ag-kim/holding-ontology)
* ermi
* [bibframe](http://bibframe.org/)  

An output of the vocabulary in HTML using the [OntoWiki's](http://ontowiki.net) [Site-Extension](https://github.com/AKSW/site.ontowiki/) can be seen [here](http://vocab.ub.uni-leipzig.de/bibrm/.html)

About this vocabulary
---------------------

This vocabulary is part of a shared project between the Leipzig University Library (UB) and the Saxon State and University Library Dresden (SLUB) supported by the european union with EFRE. The goal is to provide a Electronic Resource Management System for the UB based on linked data technologies using RDF.

Further information can be found on our [procect
site](http://aksw.org/Projects/)

Reusing vocabularies/ontologies
------------------------------

On the one hand reusing classes and properties provided by other ontolgies is quite easy and `rdf`, `rdfs`, `owl` or `foaf` are well known examples. On the other hand it's more difficult to provide  information to others about cases like in which of your classes yout want to use which properties of other ontologies.
So this document is a human readable version of those resources we reuse in our vocabulary to model the business processes we need.

In RDF we try to make use of `rdfs:subClassOf` or `owl:subClassOf` in case of adding further statements like 'owl:Restrictions' on properties to a class. (Note that we will add all restrictions on properties even if their usagage is optional, with help of `owl:minCardinality "0"`. In contrast to open world assumption this is a closed world even if we know one can add triples she wants)

    @prefix bibrm:  <http://vocab.ub.uni-leipzig.de/bibrm/> .


    @prefix bibo:   <http://purl.org/ontology/bibo/> .
    @prefix cc:     <http://creativecommons.org/ns#> .
    @prefix dc:     <http://purl.org/dc/elements/1.1/> .
    @prefix dct:    <http://purl.org/dc/terms/> .
    @prefix doap:   <http://usefulinc.com/ns/doap#>.
    @prefix foaf:   <http://xmlns.com/foaf/0.1/> .
    @prefix owl:    <http://www.w3.org/2002/07/owl#> .
    @prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix skos:   <http://www.w3.org/2004/02/skos/core#> .
    @prefix vann:   <http://purl.org/vocab/vann/>.
    @prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .

    bibrm:Journal rdf:type        owl:Class ;
                  rdfs:subClassOf bibo:Journal .

    bibrm:LicenseContract rdf:type        owl:Class ;
                          rdfs:subClassOf dcterms:LicenseDocument .

    bibrm:BibliographicResource rdf:type owl:Class ;
                                rdfs:subClassOf [ rdf:type owl:Restriction ;
                                                owl:onProperty dc:publisher ;
                                                owl:minCardinality "0"^^xsd:nonNegativeInteger
                                                ] ,
                                                [ rdf:type owl:Restriction ;
                                                owl:onProperty dc:title ;
                                                owl:cardinality "1"^^xsd:nonNegativeInteger
                                                ] .

Example of an instance of a `bibrm:Journal` to show how we reference ISSN 

    <http://ub.uni-leipzig.de/vokab/resource/examplejournal>    a bibrm:Journal ;
                                                                bibrm:hasEISSN <urn:ISSN:1234-5678> .
