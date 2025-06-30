#!/bin/bash

export PYTHONPATH=/opt/moose/share/moose/python:/opt/paraview/lib/python3.12/site-packages:$PYTHONPATH
/work/venv/bin/peacock-trame --server --host 0.0.0.0 -L /work/moose-language-support/out/main.js $@
