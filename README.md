# ACTL

![tests](https://github.com/askurandrio/ACTL/actions/workflows/build.yaml/badge.svg)

ACTL this compiler A in C++

1. while expression
2. set expression
3. function input
4. String.split
5. unpacking args
6. String -> Number
7. function print
8. `./actl example.a`


Runner:

docker build -f runner_dockerfile -t runner_dockerfile .

RUNNER_TOKEN=

docker run --rm --name github-runner \
  -e REPO_URL="https://github.com/askurandrio/ACTL" \
  -e RUNNER_NAME="actl-tests" \
  -e RUNNER_TOKEN="${RUNNER_TOKEN}" \
  -e RUNNER_WORKDIR="/tmp/github-runner-actl" \
  -e RUNNER_GROUP="actl-group" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/github-runner-actl:/tmp/github-runner-actl \
  runner_dockerfile


remove:
    docker rm -f $(docker ps -aqf "name=github-runner")
