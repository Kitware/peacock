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

## Testing an example

```bash
mamba activate moose
cd moose/python
export MOOSE_DIR=$PWD
cd ../examples/ex08_materials
make
peacock-trame -I ./ex08.i -E ex08-opt
```
