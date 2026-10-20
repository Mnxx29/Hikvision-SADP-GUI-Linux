#!/bin/bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/packaging/upstream.env"
OUTPUT_DIR="${1:?Usage: build-helper.sh OUTPUT_DIR}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
TEMP_GO_DIR=$(mktemp -d)
trap 'rm -rf -- "$TEMP_GO_DIR"' EXIT
git -C "$TEMP_GO_DIR" init -q
git -C "$TEMP_GO_DIR" remote add origin "$SADP_UPSTREAM_URL"
git -C "$TEMP_GO_DIR" fetch -q --depth 1 origin "$SADP_UPSTREAM_COMMIT"
git -C "$TEMP_GO_DIR" checkout -q --detach FETCH_HEAD
test "$(git -C "$TEMP_GO_DIR" rev-parse HEAD)" = "$SADP_UPSTREAM_COMMIT"
(
    cd "$TEMP_GO_DIR"
    GOTOOLCHAIN="go$SADP_GO_VERSION" CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
        go build -mod=readonly -trimpath -ldflags='-s -w -buildid=' -o "$OUTPUT_DIR/sadp-linux-amd64" ./cmd/sadp
)
cp "$TEMP_GO_DIR/LICENSE" "$OUTPUT_DIR/HIKVISION-TOOLING-LICENSE"
printf 'hikvision-tooling %s\nGo %s\n' "$SADP_UPSTREAM_COMMIT" "$SADP_GO_VERSION" > "$OUTPUT_DIR/BUILD-INFO.txt"
