
build-edge:
    docker build -t toy-cdn-edge ./src/edge/

run-edge:
    docker run --rm -it \
      -p 120:2080 \
      -v "./src/edge/Caddyfile:/etc/caddy/Caddyfile" \
      toy-cdn-edge
      
