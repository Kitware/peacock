# peacock docker

Build the image:
```bash
docker build -f Dockerfile.common . -t peacock_common:latest
docker build -f Dockerfile . -t peacock:latest
```

Run the image with default entrypoint and builtin peacock:
```bash
docker run -it --rm -p 8080:8080 peacock:latest
```

Run the image with local peacock and bash shell for more control
```bash
cd /my/path/to/peacock/sources
docker run -it --rm -p 8080:8080 -v $PWD:/work/peacock --entrypoint /bin/bash peacock:latest
```
