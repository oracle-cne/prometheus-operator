#!/usr/bin/env bash

mkdir -p bin
version="0.87.1"
comp_prefix=prometheus

GIT_REVISION=$(git rev-parse HEAD)
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
ldflags="
        -X main.version=v${version}
        -X github.com/prometheus/common/version.Version=${version}
        -X github.com/prometheus/common/version.Revision=${GIT_REVISION}
        -X github.com/prometheus/common/version.Branch=HEAD
        -X github.com/prometheus/common/version.BuildUser=${USER}@${HOST}
        -X github.com/prometheus/common/version.BuildDate=${BUILD_DATE}"

compsInput=(operator prometheus-config-reloader admission-webhook)
compsOutput=(prometheus-operator prometheus-config-reloader prometheus-admission-webhook)
for i in ${!compsInput[@]}; do
	go build -trimpath=false -v -o bin/${compsOutput[i]} \
      -ldflags "${ldflags}" \
      "${GOPATH_SRC}"/cmd/${compsInput[i]}
  ./bin/${compsOutput[i]} --version
done
