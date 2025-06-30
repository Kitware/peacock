#!/bin/bash
EXAMPLE_PATH=/opt/moose/share/combined/reactor/hexagonal_grid_positions.i
/work/venv/bin/peacock-trame --server --host 0.0.0.0 -I ./moose/examples/ex08_materials/ex08.i -L /work/moose-language-support/out/main.js
