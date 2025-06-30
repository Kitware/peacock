#!/bin/bash
bash setup_venv.bash
bash build_peacock.bash
/work/venv/bin/python -m pip install /work/peacock
bash build_examples.bash
