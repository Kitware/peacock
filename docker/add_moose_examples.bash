#!/bin/bash
git clone https://github.com/idaholab/moose.git /work/moose --branch 2025-05-09-release --depth 1
cd /work/moose/examples
source /environment
make -j $(( $(nproc) - 2))
