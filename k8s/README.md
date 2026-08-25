# Kubernetes Manifests

These manifests deploy the current app stack to k3s with:

- `postgres:17-alpine`
- `skeirs/anime-backlog-api:$tag`
- `skeirs/anime-backlog-frontend:$tag`
- one namespace: `anime-backlog`
- an internal API service
- a frontend Ingress through Traefik

## Setup the secrets

1. Set the values in `secret.example.yaml`

2. Rename: `mv secret.example.yaml secret.yaml` 

## Apply

```sh
kubectl apply -k k8s/
```

## Verify

```sh
kubectl get all -n anime-backlog
kubectl get ingress -n anime-backlog
kubectl logs -n anime-backlog deploy/anime-backlog-api
kubectl logs -n anime-backlog deploy/anime-backlog-frontend
kubectl logs -n anime-backlog deploy/anime-backlog-db
```

## Access

With default k3s Traefik, browse to the node IP:

```text
http://<k3s-node-ip>/
```

## Important

- Rename `secret.example.yaml` to `secret.yaml`
- `secret.yaml` currently contains the values from the repo `.env`. Replace them before a real deployment.
- `configmap.yaml` currently keeps `APP_ENV=development` to match the current repo `.env`.
- If you move to a real domain, update `CORS_ALLOW_ORIGINS` and add a host and TLS section to `ingress.yaml`.
- PostgreSQL is deployed as a single-instance `Deployment` with a PVC. For stricter production behavior, move it to a `StatefulSet` or external database.
