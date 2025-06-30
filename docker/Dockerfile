FROM peacock_common:latest

WORKDIR /work

RUN git clone https://github.com/idaholab/moose.git
RUN git clone https://github.com/Kitware/peacock.git



RUN source /environment && ./build_examples.bash
SHELL ["bash" , "-c"]

RUN source $NVM_DIR/nvm.sh && \
nvm install 16 && \
nvm use 16 && \
nvm alias default 16

# Export PATH for node/npm access in later layers
ENV NODE_VERSION=16
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# Verify node installation
RUN node -v && npm -v && echo yesss
RUN ./setup_venv.bash
RUN ./build_peacock.bash && \
    /work/venv/bin/python -m pip install /work/peacock

# setup python path for MOOSE and paraview
ENV PYTHONPATH=/opt/moose/share/moose/python:/opt/paraview/lib/python3.12/site-packages

ENTRYPOINT ["/work/entrypoint.bash"] 
CMD ["-I", "./moose/examples/ex08_materials/ex08.i"]
