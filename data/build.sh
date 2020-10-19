#!/bin/bash -e

# Note: Santa Cruz has to come first due to some weird formatting issue
cat santa_cruz_2017.2.csv.gz santa_clara.csv.gz san_mateo.csv.gz san_francisco.csv.gz alameda.csv.gz contra_costa.csv.gz sonoma.csv.gz solano.csv.gz yolo.csv.gz marin.csv.gz los_angeles.csv.gz san_bernadino.csv.gz > ca_all.csv.gz
