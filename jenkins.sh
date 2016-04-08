#!/usr/bin/env bash

function setup_package() {
    echo "[Setup Pip Packages]"
    pip install -r requirements.txt -q
}

echo "[Jenkins Test]"
virtualenv -p python3 .venv
. .venv/bin/activate
setup_package