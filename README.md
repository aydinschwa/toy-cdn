# Toy CDN

A from-scratch implementation of a globally distributed Content Delivery Network, featuring geo-aware DNS routing and edge caching.

## Architecture

```
┌─────────────┐     DNS Query      ┌─────────────────┐
│   Client    │ ─────────────────► │   Nameserver    │
│             │ ◄───────────────── │  (geo-routing)  │
└─────────────┘   Closest Edge IP  └─────────────────┘
       │
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────────────┐
│                    Edge Servers                      │
│  ┌───────────┐                      ┌───────────┐   │
│  │  SF Edge  │                      │  LON Edge │   │
│  │  (Caddy)  │                      │  (Caddy)  │   │
│  └─────┬─────┘                      └─────┬─────┘   │
└────────┼────────────────────────────────────────────┘
         │              Cache Miss
         ▼
   ┌───────────┐
   │  Origin   │
   │  (Sydney) │
   └───────────┘
```

### Components

- **Nameserver**: Custom authoritative DNS server that uses MaxMind's GeoIP database to determine client location and return the IP of the geographically closest edge server
- **Edge Servers**: Caddy reverse proxies with caching enabled, deployed in San Francisco and London
- **Origin Server**: Simple Python HTTP server hosting static content, deployed in Sydney

## How It Works

1. Client queries the nameserver for `cdn-test.space`
2. Nameserver looks up client's IP geolocation using MaxMind GeoLite2
3. Nameserver calculates haversine distance to each edge server
4. Nameserver returns the IP of the closest edge server as an A record
5. Client connects to the edge server
6. Edge server serves from cache (hit) or fetches from origin (miss)

## Local Development

### Prerequisites

- Docker and Docker Compose
- [just](https://github.com/casey/just) (optional, for convenient commands)

### Running Locally

```bash
docker compose up
```

This starts:
- Origin server on port 8080 (via edge proxy)
- Nameserver on port 120/udp

## Deployment

The `terraform/` directory contains infrastructure-as-code for deploying to DigitalOcean.

### Prerequisites

1. A DigitalOcean account and API token
2. Terraform installed
3. A MaxMind GeoLite2-City database (free, requires [registration](https://www.maxmind.com/en/geolite2/signup))

### Setup

1. Create `terraform/terraform.tfvars`:
   ```hcl
   do_token = "your-digitalocean-api-token"
   ```

2. Place your GeoLite2-City.mmdb in `src/nameserver/data/`

3. Deploy:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

## Project Structure

```
├── src/
│   ├── edge/           # Caddy-based caching reverse proxy
│   ├── nameserver/     # Custom geo-aware DNS server
│   └── origin/         # Simple static file server
├── terraform/          # Infrastructure as code
└── docker-compose.yml  # Local development setup
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) for IP geolocation data

