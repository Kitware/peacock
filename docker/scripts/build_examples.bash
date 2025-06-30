#!/bin/bash
cd /work/moose/examples

make -j $(( $(nproc) - 2))
