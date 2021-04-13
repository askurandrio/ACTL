# ACTL
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

RUNNER_TOKEN=

docker run --rm --name github-runner \
  -e REPO_URL="https://github.com/askurandrio/ACTL" \
  -e RUNNER_NAME="actl-tests" \
  -e RUNNER_TOKEN="${RUNNER_TOKEN}" \
  -e RUNNER_WORKDIR="/tmp/github-runner-actl" \
  -e RUNNER_GROUP="actl-group" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/github-runner-actl:/tmp/github-runner-actl \
  myoung34/github-runner:latest