#!/usr/bin/env bash

set -euo pipefail

version="0.92.0"
registry="container-registry.oracle.com/olcne"
comp_prefix=prometheus
container_manager="${CONTAINER_MANAGER:-podman}"
golang_version="${GOLANG_VERSION:-${1:-}}"

log() {
  echo "build-image.sh: $*"
}

set -x

log "starting Prometheus Operator OLM image build"
log "container manager: ${container_manager}"

if [[ -z "${golang_version}" ]]; then
  echo "build-image.sh: unable to determine Go version; set GOLANG_VERSION or pass it as the first argument" >&2
  exit 1
fi

log "using Go compiler version ${golang_version}"

build_args=(
  --pull
  --build-arg "https_proxy=${https_proxy:-}"
  --build-arg "GOLANG_VERSION=${golang_version}"
)

mount_yum_config() {
  local yum_repo_config_file="${YUM_REPO_CONFIG_FILE:-}"

  if [[ -z "${yum_repo_config_file}" ]]; then
    log "YUM_REPO_CONFIG_FILE is not set; using base image repository configuration"
    return
  elif [[ "${yum_repo_config_file}" != /* ]]; then
    yum_repo_config_file="$(pwd)/${yum_repo_config_file}"
  fi

  log "checking yum repo config file ${yum_repo_config_file}"
  if [[ ! -s "${yum_repo_config_file}" ]]; then
    echo "build-image.sh: yum repo config file ${yum_repo_config_file} is missing or empty" >&2
    exit 1
  fi

  log "mounting yum repo config file ${yum_repo_config_file}"
  build_args=(
    --volume "${yum_repo_config_file}:/etc/yum.repos.d/extra.repo:ro"
    "${build_args[@]}"
  )
}

mount_yum_config

tags=("${comp_prefix}-operator" "${comp_prefix}-config-reloader" "${comp_prefix}-admission-webhook")
for tag in "${tags[@]}"; do
  docker_tag="${registry}/${tag}:v${version}"
  dockerfile="./olm/builds/Dockerfile.${tag}"

  log "building ${docker_tag} with ${dockerfile}"
  "${container_manager}" build "${build_args[@]}" -t "${docker_tag}" -f "${dockerfile}" .

  log "saving ${docker_tag} to ${tag}.tar"
  "${container_manager}" save -o "${tag}.tar" "${docker_tag}"
done

log "completed Prometheus Operator OLM image build"
