#!/usr/bin/env bash

version="0.87.0"
registry="container-registry.oracle.com/olcne"
comp_prefix=prometheus

tags=(${comp_prefix}-operator ${comp_prefix}-config-reloader ${comp_prefix}-admission-webhook)
for i in ${!tags[@]}; do
  docker_tag="${registry}/${tags[i]}:v${version}"
  docker build --pull \
      --build-arg https_proxy=${https_proxy} \
      -t ${docker_tag} -f ./olm/builds/Dockerfile.${tags[i]} .
  docker save -o ${tags[i]}.tar ${docker_tag}
done
