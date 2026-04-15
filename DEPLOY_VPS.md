# Deploying To A Linux VPS

This guide describes a safe, simple production deployment for this project on a Linux VPS.

It assumes:

- a Debian or Ubuntu VPS
- Docker Engine and Docker Compose plugin
- a public domain such as `anime.example.com`
- TLS termination with Nginx on the host

This is the recommended layout:

- `frontend` listens on `127.0.0.1:20773`
- `api` listens on `127.0.0.1:43968`
- `db` listens on `127.0.0.1:5432`
- Nginx exposes only `80/443` to the internet

That keeps PostgreSQL and the API off the public internet.

## 1. Prepare the VPS

Update the system:

```sh
sudo apt update
sudo apt upgrade -y
```

Install basic tools:

```sh
sudo apt install -y ca-certificates curl git ufw
```

Configure a firewall:

```sh
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

If you use a cloud firewall from your VPS provider, mirror the same rules there.

## 2. Install Docker

Install Docker Engine and the Compose plugin using Docker's official instructions for your distro:

- https://docs.docker.com/engine/install/ubuntu/
- https://docs.docker.com/engine/install/debian/

After installation, verify:

```sh
sudo docker version
sudo docker compose version
```

## 3. Install Nginx and Certbot

Install Nginx and the Let's Encrypt helper:

```sh
sudo apt install -y nginx certbot python3-certbot-nginx
```

Verify:

```sh
sudo nginx -v
sudo certbot --version
```

## 4. Prepare the deployment directory

Use a predictable location:

```sh
sudo mkdir -p /opt/anime-tracker-web
sudo chown "$USER":"$USER" /opt/anime-tracker-web
cd /opt/anime-tracker-web
```

For a Docker-based VPS deployment, prefer deploying prebuilt container images instead of copying the full source tree to the server.

Create a minimal deployment directory that contains only the files the VPS needs:

- `compose.yaml`
- `compose.prod.yaml`
- `.env`

If you use a custom Nginx config on the VPS, that stays under `/etc/nginx`, not in this app directory.

## 5. Build and publish container images

Build images in CI or on a trusted build machine, then push them to a registry such as Docker Hub or GitHub Container Registry.

Recommended image tags:

- `ghcr.io/your-user/anime-tracker-api:latest`
- `ghcr.io/your-user/anime-tracker-frontend:latest`

The `db` service should keep using the official `postgres:17-alpine` image.

To support this deployment model cleanly, the Compose file used on the VPS should reference `image:` for `api` and `frontend` instead of `build:`.

Example production override file `compose.prod.yaml`:

```yaml
services:
  api:
    image: ghcr.io/your-user/anime-tracker-api:latest
    build: null

  frontend:
    image: ghcr.io/your-user/anime-tracker-frontend:latest
    build: null
```

Place that file on the VPS next to `compose.yaml`.

## 6. Create the production `.env`

Start from the example:

```sh
cp .env.example .env
```

Edit `.env` and set at minimum:

```dotenv
COMPOSE_PROJECT_NAME=anime-backlog

POSTGRES_DB=anime_backlog
POSTGRES_USER=anime
POSTGRES_PASSWORD=REPLACE_WITH_A_LONG_RANDOM_PASSWORD
POSTGRES_PORT=127.0.0.1:5432

API_PORT=127.0.0.1:43968
FRONTEND_PORT=127.0.0.1:20773

NEXT_PUBLIC_API_BASE_URL=https://anime.example.com/api/v1

APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO
UVICORN_WORKERS=1
CORS_ALLOW_ORIGINS=["https://anime.example.com"]
AUTH_OWNER_USERNAME=owner
AUTH_OWNER_PASSWORD=REPLACE_WITH_A_LONG_RANDOM_PASSWORD
AUTH_SESSION_SECRET=REPLACE_WITH_A_LONG_RANDOM_SECRET_AT_LEAST_32_CHARS
AUTH_SESSION_MAX_AGE_SECONDS=2592000

SHIKIMORI_GRAPHQL_URL=https://shikimori.one/api/graphql
SHIKIMORI_REQUEST_TIMEOUT_SECONDS=10
SHIKIMORI_CACHE_TTL_SECONDS=31536000
SHIKIMORI_USER_AGENT=anime-backlog-web/1.0
SHIKIMORI_HTTPS_PROXY_URL=
SHIKIMORI_SOCKS5_PROXY_URL=
```

Notes:

- Use a long random value for `POSTGRES_PASSWORD`.
- Bind all published ports to `127.0.0.1`, not `0.0.0.0`.
- `NEXT_PUBLIC_API_BASE_URL` must use your public HTTPS domain.
- `CORS_ALLOW_ORIGINS` must be a JSON array string.
- Set strong values for `AUTH_OWNER_PASSWORD` and `AUTH_SESSION_SECRET`.
- Set only one of `SHIKIMORI_HTTPS_PROXY_URL` or `SHIKIMORI_SOCKS5_PROXY_URL` if you need a proxy.

## 7. Configure DNS

Create a DNS record pointing your domain to the VPS public IP:

- `A` record for `anime.example.com`
- optionally `AAAA` if you have IPv6 configured

Wait until DNS resolves correctly before enabling HTTPS.

## 8. Configure Nginx

Create `/etc/nginx/sites-available/anime-tracker`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name anime.example.com;

    client_max_body_size 20m;

    location /api/ {
        proxy_pass http://127.0.0.1:43968;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:20773;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site and validate:

```sh
sudo ln -s /etc/nginx/sites-available/anime-tracker /etc/nginx/sites-enabled/anime-tracker
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status nginx
```

## 9. Enable HTTPS

After DNS is working and Nginx serves the site on port 80, request a certificate:

```sh
sudo certbot --nginx -d anime.example.com
```

Verify automatic renewal:

```sh
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

## 10. Start the application

Log in to your container registry first if the images are private:

```sh
docker login ghcr.io
```

Then start the stack from the deployment directory:

```sh
docker compose -f compose.yaml -f compose.prod.yaml pull
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

Check status:

```sh
docker compose -f compose.yaml -f compose.prod.yaml ps
docker compose -f compose.yaml -f compose.prod.yaml logs -f --tail=200
```

The backend startup flow already runs migrations on startup before serving traffic.

## 11. Verify the deployment

Check locally on the server:

```sh
curl -I http://127.0.0.1:20773
curl http://127.0.0.1:43968/api/v1/healthz
```

Then check externally:

```sh
curl -I https://anime.example.com
curl https://anime.example.com/api/v1/healthz
```

You should also open the site in a browser and verify:

- the UI loads
- API-backed pages work
- anonymous browsing is read only
- owner sign-in works
- adding an anime works after signing in
- Shikimori info loads

## 12. Updating the deployment

After publishing new container images:

```sh
cd /opt/anime-tracker-web
docker compose -f compose.yaml -f compose.prod.yaml pull
docker compose -f compose.yaml -f compose.prod.yaml up -d
docker compose -f compose.yaml -f compose.prod.yaml ps
```

If you want to clean up old images afterward:

```sh
docker image prune -f
```

## 13. Backups

Create backups regularly. For a minimal image-based deployment, use `docker exec` directly:

```sh
mkdir -p /opt/anime-tracker-web/backups
docker compose -f compose.yaml -f compose.prod.yaml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip \
  > /opt/anime-tracker-web/backups/postgres-$(date +%Y%m%d-%H%M%S).sql.gz
```

Backups are written under `/opt/anime-tracker-web/backups`.

To restore:

```sh
gzip -dc /opt/anime-tracker-web/backups/postgres-YYYYMMDD-HHMMSS.sql.gz | \
docker compose -f compose.yaml -f compose.prod.yaml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Treat restore as destructive to the target database.

Best practice:

- keep automated off-server backups
- test restore at least once before relying on backups

## 14. Day-2 operations

Useful commands:

```sh
docker compose -f compose.yaml -f compose.prod.yaml ps
docker compose -f compose.yaml -f compose.prod.yaml logs -f --tail=200
docker compose -f compose.yaml -f compose.prod.yaml restart
```

Shell access inside containers:

```sh
docker compose -f compose.yaml -f compose.prod.yaml exec api sh
docker compose -f compose.yaml -f compose.prod.yaml exec db sh
docker compose -f compose.yaml -f compose.prod.yaml exec frontend sh
```

## 15. Security checklist

Use this checklist for a sane baseline:

- Keep `POSTGRES_PORT`, `API_PORT`, and `FRONTEND_PORT` bound to `127.0.0.1`.
- Expose only `22`, `80`, and `443` from the VPS.
- Use HTTPS in `NEXT_PUBLIC_API_BASE_URL`.
- Set `CORS_ALLOW_ORIGINS` to your real domain only.
- Use a strong PostgreSQL password.
- Prefer immutable image tags or a controlled `latest` publishing workflow.
- Keep the system packages updated.
- Keep Docker, Nginx, and Certbot updated.
- Store backups off the VPS.
- Do not put secrets into the repository.

## 16. If you do not want a reverse proxy

This is not the recommended setup, but it works.

You can expose the frontend directly and keep the API local:

```dotenv
FRONTEND_PORT=20773
API_PORT=127.0.0.1:43968
POSTGRES_PORT=127.0.0.1:5432
NEXT_PUBLIC_API_BASE_URL=https://anime.example.com/api/v1
```

You would still need some HTTPS-capable reverse proxy in front of the API for browsers, so in practice Nginx is the simpler and safer option.
