#!/bin/bash
/opt/miniforge3/bin/python3.12 -m venv venv
./venv/bin/python -m pip install vtk && ./venv/bin/python -m pip install --upgrade pip
