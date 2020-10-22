#!/usr/bin/env bash

set -e

TARGET=0
BATCH=500
END=140000

until [ $TARGET -gt $END ]; do
  echo "Starting $TARGET..."
  poetry run python scrape.py $TARGET $BATCH
  ((TARGET+=BATCH))
  sleep 5
done
