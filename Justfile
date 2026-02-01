
build-edge:
    docker build -t toy-cdn-edge ./src/edge/

run-edge:
    docker run --rm -it \
      -p 120:2080 \
      -v "./src/edge/Caddyfile:/etc/caddy/Caddyfile" \
      toy-cdn-edge
      
build-origin:
    docker build -t toy-cdn-origin ./src/origin/

run-origin:
    docker run --rm -it \
    -p 130:8000 \
    toy-cdn-origin

push-all: push-origin push-edge push-nameserver

push-origin:
    docker build -t aydinschwa/toy-cdn-origin:latest --platform linux/amd64 ./src/origin/
    docker push aydinschwa/toy-cdn-origin:latest

push-edge:
    docker build -t aydinschwa/toy-cdn-edge:latest --platform linux/amd64 ./src/edge/
    docker push aydinschwa/toy-cdn-edge:latest

push-nameserver:
    docker build -t aydinschwa/toy-cdn-nameserver:latest --platform linux/amd64 ./src/nameserver/
    docker push aydinschwa/toy-cdn-nameserver:latest