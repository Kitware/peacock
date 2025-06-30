#!/bin/bash
# setup python environment
/opt/miniforge3/bin/python -m venv venv
./venv/bin/python -m pip install vtk && ./venv/bin/python -m pip install --upgrade pip
