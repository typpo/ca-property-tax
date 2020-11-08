#!/bin/bash -e

files=(
  san_diego.csv.gz
  santa_cruz.csv.gz
  santa_clara.csv.gz
  san_mateo.csv.gz
  san_francisco.csv.gz
  alameda.csv.gz
  contra_costa.csv.gz
  napa.csv.gz
  sonoma.csv.gz
  solano.csv.gz
  yolo.csv.gz
  marin.csv.gz
  napa.csv.gz
  los_angeles.csv.gz
  san_bernadino.csv.gz
  sacramento.csv.gz
  san_luis_obispo.csv.gz
  fresno.csv.gz
  butte.csv.gz
  orange.csv.gz
  placer.csv.gz
  kern.csv.gz
)

cat "${files[@]}" > ca_all.csv.gz
