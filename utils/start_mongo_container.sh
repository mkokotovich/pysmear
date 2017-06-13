#!/bin/bash
tools_dir=$(cd $(dirname $0) ; pwd)
mkdir -p ${tools_dir}/data

platform=$(uname)
docker_image="jixer/rpi-mongo"

if [[ ${platform} == "Darwin" ]] ; then
    docker_image="mongo"
fi
docker run --name testdb -p 27017:27017 -v ${tools_dir}/data:/data -d ${docker_image}

