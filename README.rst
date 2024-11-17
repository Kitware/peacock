=============
peacock-trame
=============

MOOSE GUI developed using Trame from Kitware Inc.

- `Blog post <https://www.kitware.com/the-evolution-of-peacock-a-powerful-interface-for-moose-simulations/>`_
- `Video <https://vimeo.com/838073269>`_

|image_1|

.. |image_1| image:: https://www.kitware.com/main/wp-content/uploads/2023/06/image1-1-1024x601.png
  :width: 50%


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

Create venv with mamba locally

.. code-block:: console

    mamba install python=3.10
    mamba create -n moose python=3.10 moose paraview -y
    mamba activate moose
    pip install peacock-trame

Test application on a moose example

.. code-block:: console

    peacock-trame -I ./moose/examples/ex08_materials/ex08.i

Running with language server
-----------------------------------------------------------
Clone and build the moose language server

.. code-block:: console

    git clone git@github.com:idaholab/moose-language-support.git
    cd moose-language-support
    npm run compile

Install middleware packages

.. code-block:: console

    cd /path/to/peacock/lang-server
    npm i

Point to compiled language server when running app

.. code-block:: console

    peacock-trame -I ./ex08.i -L /path/to/moose-language-support/server/out/server.js

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

    cd ./moose/examples/ex08_materials
    make
    peacock-trame -I ./ex08.i
