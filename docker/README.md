# peacock docker

Build the image:
```bash
docker build -f Dockerfile.common . -t peacock_common:latest
docker build -f Dockerfile . -t peacock:latest
```

Run the image:
```bash
docker run -it --rm -p 8080:8080 peacock:latest)
```

