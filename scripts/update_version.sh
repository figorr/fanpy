#!/usr/bin/env bash
set -euo pipefail

version="$1"

# manifest.json
jq --arg ver "$version" '.version = $ver' custom_components/fanpy/manifest.json > tmp.json && mv tmp.json custom_components/fanpy/manifest.json

# version.py
echo "__version__ = \"$version\"" > custom_components/fanpy/version.py

# package.json
jq --arg ver "$version" '.version = $ver' package.json > tmp.json && mv tmp.json package.json

# package-lock.json
jq --arg ver "$version" '.version = $ver | .packages[""].version = $ver' package-lock.json > tmp.json && mv tmp.json package-lock.json

rm -f tmp.json
