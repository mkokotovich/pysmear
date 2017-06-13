#!/bin/bash
tools_dir=$(cd $(dirname $0) ; pwd)
docker run --name testdb -p 27017:27017 -v ${tools_dir}/data:/data -d jixer/rpi-mongo

