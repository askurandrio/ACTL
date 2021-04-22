#!/bin/bash


set -x
set -e


container_id="$(docker ps -aqf "name=github-runner")"


if [[ "${container_id}" ]]; then
  docker rm -f ${container_id}
fi


docker build -f runner_dockerfile -t runner_dockerfile .
docker run --rm --name github-runner \
  -e REPO_URL="https://github.com/askurandrio/ACTL" \
  -e RUNNER_NAME="actl-tests" \
  -e ACCESS_TOKEN="${1}" \
  -e RUNNER_WORKDIR="/tmp/github-runner-actl" \
  -e RUNNER_GROUP="actl-group" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/github-runner-actl:/tmp/github-runner-actl \
  runner_dockerfile
