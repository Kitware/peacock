# Peacock/trame app

This document describe the setup for development and testing.
The following steps have been extracted from https://mooseframework.inl.gov/getting_started/installation/conda.html.

## Use Mamba for Python environment

```bash
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-arm64.sh
bash Mambaforge-MacOSX-arm64.sh -b -p ~/mambaforge3
export PATH=$HOME/mambaforge3/bin:$PATH
```

You will probably have to move the code that was generated in `~/.bash_profile` to `~/.zshrc`.

Then after terminal restart add INL channel

```bash
conda config --add channels https://conda.software.inl.gov/public
```

Create a virtual-environment for moose

```bash
mamba create -n moose moose-tools moose-libmesh
```

Now you can use the moose venv by running `mamba activate moose`

## Getting moose example project

```bash
mamba activate moose
git clone https://github.com/idaholab/moose.git
cd moose/test
make -j 4
./run_tests -j 4
```

## Installing trame peakock

```bash
mamba activate moose
pip install .
```

## Build/Install ParaView

Mamba by default will run with Python 3.10. ParaView needs to be built with the same version of Python.

```bash
git clone --recursive https://gitlab.kitware.com/paraview/paraview.git
mkdir build
cd build
ccmake -GNinja ../paraview
# Make sure Python 3.10 is used
ninja
export PYTHONPATH=$PWD/lib/python3.10/site-packages
```

## Testing an example

```bash
mamba activate moose
cd moose
export MOOSE_DIR=$PWD
cd ./examples/ex08_materials
make
peacock-trame -I ./ex08.i -E ex08-opt
```


## Using ParaView binary

Attempt to get application working with ParaView pre-built executable.

```bash
mkdir peacock-work
cd peacock-work
git clone --recursive git@github.com:Kitware/peacock.git
git clone --recursive https://github.com/idaholab/moose.git
curl -LO https://www.paraview.org/files/v5.11/ParaView-5.11.0-MPI-OSX11.0-Python3.9-arm64.dmg
# Mount and copy ParaView-5.11.0.app/ in the current directory


mamba install python=3.9
mamba create -p ./venv python=3.9 moose-tools moose-libmesh
mamba activate ./venv
pip install ./peacock

export MOOSE_DIR=$PWD/moose
export PVPYTHON=$PWD/ParaView-5.11.0.app/Contents/bin/pvpython
export PV_VENV=$PWD/venv
export TRAME_APP=peacock_trame.app


cd ./moose/examples/ex08_materials
make

$PVPYTHON -m paraview.apps.trame -I ./ex08.i -E ex08-opt
```
