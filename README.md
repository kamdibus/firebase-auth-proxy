# Firebase Authentication Service

A lightweight authentication proxy service for PrimaLab that validates Firebase JWT tokens for Traefik ForwardAuth.

## Architecture

This service sits between Traefik and the business API, providing:
- Firebase JWT token validation
- Basic user info extraction from Firebase tokens
- Security header injection for business API

## Request Flow

```
Frontend → Traefik → Firebase Auth Service → Business API
              │            │                      │
              │            ├─ Validates JWT       │
              │            ├─ Extracts user info  │
              │            └─ Returns headers     │
              │                                   │
              └─ Forwards with headers ──────────►│
                 (X-User-Email, X-User-Name,      │
                  X-Firebase-UID)                 │
```

## Configuration

Set environment variables:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/service-account.json

# Service Configuration
PORT=8001
LOG_LEVEL=INFO
```

## Development

```bash
# Install dependencies
uv sync

# Run the service
uv run firebase-auth

# Run tests
uv run pytest
```

## Docker

```bash
# Build image
docker build -t primalab-firebase-auth .

# Run container
docker run -p 8001:8001 \
  -e FIREBASE_PROJECT_ID=your-project \
  -e MONGO_URI=mongodb://mongo:27017 \
  primalab-firebase-auth
```
