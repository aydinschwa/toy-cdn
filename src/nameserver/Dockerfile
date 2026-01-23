FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 53/udp
CMD ["uv", "run", "server.py"]