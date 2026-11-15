#!/usr/bin/env bash
set -euo pipefail

# Keep the Hugo version used by the previous production build.
HUGO_VERSION="${HUGO_VERSION:-0.128.0}"
build_tools_dir="$(mktemp -d)"
trap 'rm -rf "$build_tools_dir"' EXIT

curl --fail --silent --show-error --location --retry 3 \
  "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" \
  --output "$build_tools_dir/hugo.tar.gz"
tar -xzf "$build_tools_dir/hugo.tar.gz" -C "$build_tools_dir"

export HUGO_ENVIRONMENT=production
# Use the Render address until the custom domain is ready. HUGO_BASEURL can
# override it after the DNS cutover; local builds use hugo.toml.
base_url="${HUGO_BASEURL:-${RENDER_EXTERNAL_URL:-https://blog.cameronengineer.com}}"
"$build_tools_dir/hugo" --gc --minify --baseURL "${base_url%/}/"
