#!/usr/bin/env bash

mkdir -p bin
version="0.85.0"
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

comps=(operator config-reloader admission-webhook)
for i in ${!tags[@]}; do
	go build -trimpath=false -v -o bin/${comp_prefix}-${comps[i]} \
      -ldflags "${ldflags}" \
      "${GOPATH_SRC}"/cmd/${comps[i]}
  ./bin/${comp_prefix}-${comps[i]} --version
done
