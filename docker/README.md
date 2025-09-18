# Peacock docker image

## Build
```bash
docker build -f Dockerfile.moosepv . -t moosepv:latest
docker build -f Dockerfile.peacock . -t peacock:latest
```


## Basic usage
```bash
# run the image with default entrypoint and builtin peacock
# ParaView OpenGL renderer will be llvmpipe
docker run -it --rm -p 8080:8080 peacock:latest

# same but if you have a NVIDIA GPU you want to use
docker run --privileged --runtime=nvidia --gpus all -it --rm -p 8080:8080 peacock:latest

# run with custom peacock input and executable, here porous_flow
docker run -it --rm -p 8080:8080 peacock:latest -I /work/moose/modules/porous_flow/examples/flow_through_fractured_media/diffusion.i -E /work/moose/modules/porous_flow/porous_flow-opt
```

## Advanced usage
```bash
# run the image with an interactive bash shell for more control
docker run -it --rm -p 8080:8080 --entrypoint /bin/bash peacock:latest

# map your local data into the container
# example: use host input file with container executable
# the -u flag is important so that the output files are written back to the host with correct permissions
docker run -it --rm -p 8080:8080 -u $UID:$GID -v /path/to/moose/examples/ex08_materials:/work/user_data peacock:latest -I /work/user_data/ex08.i -E /work/moose/examples/ex08_materials/ex08-opt

# by overriding the container entrypoint, you can do much more than just running peacock
# example, getting porous flow options as JSON
docker run -it --rm --entrypoint /work/moose/modules/porous_flow/porous_flow-opt peacock:latest -options_left 0 --json > porous_flow_params.json

# for peacock developers: mount your local peacock
cd /path/to/your/local/peacock
docker run -it --rm -p 8080:8080 --entrypoint /bin/bash -v $PWD:/work/peacock peacock:latest
# then, pip install peacock in editable mode
> $PYTHON_EXECUTABLE -m pip install -e /work/peacock
# you're now free to modify your host peacock and run it inside the container
# just make sure the vue-components and lang-server are built on the host
> /work/run_peacock.bash -I /work/moose/examples/ex08_materials/ex08.i
```
