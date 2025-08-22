FROM peacock_common:latest

WORKDIR /work

RUN git clone https://github.com/idaholab/moose.git --branch 2025-05-09-release --depth 1
RUN git clone https://github.com/bourdaisj/peacock.git && cd peacock && git checkout improve-exodus-viewer-time-and-block-handling

COPY scripts/ /work/

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
RUN node -v && npm -v

# setup python path for MOOSE and paraview
ENV PYTHONPATH=/opt/moose/share/moose/python:/opt/paraview/lib/python3.12/site-packages

RUN ["chmod", "+x", "/work/build_examples.bash"]
RUN ["chmod", "+x", "/work/build_peacock.bash"]
RUN ["chmod", "+x", "/work/entrypoint.bash"]
RUN ["chmod", "+x", "/work/run_example.bash"]
RUN ["chmod", "+x", "/work/setup_venv.bash"]
RUN ["chmod", "+x", "/work/setup.bash"]

ENTRYPOINT ["/work/entrypoint.bash"] 
CMD ["-I", "./moose/examples/ex08_materials/ex08.i"]
