=============
peacock-trame
=============

MOOSE GUI developed using Trame from Kitware Inc.

License
-----------------------------------------------------------

Free software: Apache Software License

Mamba setup
-----------------------------------------------------------

.. code-block:: console

    curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-arm64.sh
    bash Mambaforge-MacOSX-arm64.sh -b -p ~/mambaforge3
    export PATH=$HOME/mambaforge3/bin:$PATH

You will probably have to move the code that was generated in `~/.bash_profile` to `~/.zshrc`.

Then after terminal restart add INL channel

.. code-block:: console

    conda config --add channels https://conda.software.inl.gov/public


Running the software
-----------------------------------------------------------

.. code-block:: console

    mkdir peacock-work
    cd peacock-work
    git clone --recursive git@github.com:Kitware/peacock.git
    git clone --recursive https://github.com/idaholab/moose.git
    curl -LO https://www.paraview.org/files/v5.11/ParaView-5.11.0-MPI-OSX11.0-Python3.9-arm64.dmg
    # Mount and copy ParaView-5.11.0.app/ in the current directory

Create venv with mamba locally

.. code-block:: console

    mamba install python=3.9
    mamba create -p ./venv python=3.9 moose-tools moose-libmesh
    mamba activate ./venv
    pip install ./peacock


Setup env property to ease execution later on

.. code-block:: console

    export MOOSE_DIR=$PWD/moose
    export PVPYTHON=$PWD/ParaView-5.11.0.app/Contents/bin/pvpython
    export PV_VENV=$PWD/venv
    export TRAME_APP=peacock_trame.app


Test application on a moose example

.. code-block:: console

    cd ./moose/examples/ex08_materials
    make
    $PVPYTHON -m paraview.apps.trame -I ./ex08.i -E ex08-opt

Running with language server
-----------------------------------------------------------
Clone and build the moose language server

.. code-block:: console

    git clone git@github.com:idaholab/moose-language-support.git
    cd moose-language-support
    npm run compile

Point to compiled language server when running app

.. code-block:: console

    $PVPYTHON -m paraview.apps.trame -I ./ex08.i -E ex08-opt \
        -L /path/to/moose-language-support/server/out/server.js

Development setup
-----------------------------------------------------------

Installing peacock using the local files

.. code-block:: console

    pip install -e ./peacock


Building the client code

.. code-block:: console

    cd vue-components
    npm i
    npm run build
    cd -

Run the application assuming the same layout as previously described

.. code-block:: console

    export MOOSE_DIR=$PWD/moose
    export PVPYTHON=$PWD/ParaView-5.11.0.app/Contents/bin/pvpython
    export PV_VENV=$PWD/venv
    export TRAME_APP=peacock_trame.app

.. code-block:: console

    cd ./moose/examples/ex08_materials
    make
    $PVPYTHON -m paraview.apps.trame -I ./ex08.i -E ex08-opt
