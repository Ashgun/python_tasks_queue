#!/bin/sh
docker-compose up --scale worker=2 --build "$@"

