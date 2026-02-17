# Production Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Domain name with SSL certificate
- Reverse proxy (Nginx/Traefik)
- Monitoring tools (optional)

## Security Hardening

### 1. Environment Variables

Never commit `.env` file. Use secrets management:

```bash
# Use Docker secrets
echo "your_hf_token" | docker secret create hf_token -
```

Update docker-compose.yml:
```yaml
services:
  llm-service:
    secrets:
      - hf_token
    environment:
      - HF_TOKEN_FILE=/run/secrets/hf_token
```

### 2. Add Authentication

Install in gateway:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

Add to gateway/app.py:
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials

@app.post("/voice/query", dependencies=[Depends(verify_token)])
async def voice_query(audio: UploadFile = File(...)):
    # ... existing code
```

### 3. Rate Limiting

Add to gateway/requirements.txt:
```
slowapi==0.1.9
```

Add to gateway/app.py:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/voice/query")
@limiter.limit("10/minute")
async def voice_query(request: Request, audio: UploadFile = File(...)):
    # ... existing code
```

### 4. HTTPS Configuration

Create nginx.conf:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://gateway:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Add to docker-compose.yml:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/conf.d/default.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - gateway
  networks:
    - voice-network
```

## Performance Optimization

### 1. Use GPU

Update docker-compose.yml:
```yaml
services:
  stt-service:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  llm-service:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. Model Optimization

Use quantized models:
```python
# In llm-service/app.py
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=quantization_config,
    device_map="auto"
)
```

### 3. Caching Layer

Add Redis:
```yaml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
  networks:
    - voice-network
```

Update gateway to cache responses:
```python
import redis
import hashlib

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def get_cache_key(audio_hash: str) -> str:
    return f"voice_query:{audio_hash}"

@app.post("/voice/query")
async def voice_query(audio: UploadFile = File(...)):
    audio_content = await audio.read()
    audio_hash = hashlib.md5(audio_content).hexdigest()
    cache_key = get_cache_key(audio_hash)
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # ... process request ...
    
    # Cache result
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result
```

### 4. Load Balancing

Use multiple replicas:
```yaml
services:
  llm-service:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Monitoring

### 1. Health Checks

Add to docker-compose.yml:
```yaml
services:
  gateway:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 2. Prometheus Metrics

Add to gateway/requirements.txt:
```
prometheus-fastapi-instrumentator==6.1.0
```

Add to gateway/app.py:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Create prometheus.yml:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'voice-agent'
    static_configs:
      - targets: ['gateway:9000']
```

Add to docker-compose.yml:
```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  networks:
    - voice-network

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  networks:
    - voice-network
```

### 3. Logging

Add centralized logging:
```yaml
loki:
  image: grafana/loki
  ports:
    - "3100:3100"
  networks:
    - voice-network

promtail:
  image: grafana/promtail
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - ./promtail-config.yml:/etc/promtail/config.yml
  networks:
    - voice-network
```

## Backup Strategy

### 1. Database Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup vector database
docker-compose exec -T rag-service tar czf - /data/vectordb > $BACKUP_DIR/vectordb.tar.gz

# Backup SQLite database
docker cp $(docker-compose ps -q rag-service):/data/knowledge.db $BACKUP_DIR/knowledge.db

# Backup models (optional, large files)
# tar czf $BACKUP_DIR/models.tar.gz ./models/

echo "Backup completed: $BACKUP_DIR"
```

### 2. Automated Backups

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Scaling Strategy

### Horizontal Scaling

```yaml
version: '3.8'

services:
  gateway:
    deploy:
      replicas: 2
  
  stt-service:
    deploy:
      replicas: 3
  
  llm-service:
    deploy:
      replicas: 2
```

### Kubernetes Deployment

Create k8s/deployment.yaml:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: voice-gateway
  template:
    metadata:
      labels:
        app: voice-gateway
    spec:
      containers:
      - name: gateway
        image: voice-gateway:latest
        ports:
        - containerPort: 9000
        env:
        - name: STT_SERVICE_URL
          value: "http://stt-service:8001"
---
apiVersion: v1
kind: Service
metadata:
  name: voice-gateway
spec:
  selector:
    app: voice-gateway
  ports:
  - port: 80
    targetPort: 9000
  type: LoadBalancer
```

## Cost Optimization

### 1. Use Smaller Models

- Whisper: `tiny` or `base` instead of `large`
- LLM: Use distilled models (DistilBERT, TinyLlama)

### 2. Auto-scaling

Scale based on load:
```yaml
services:
  llm-service:
    deploy:
      replicas: 1
      update_config:
        parallelism: 2
      restart_policy:
        condition: on-failure
```

### 3. Spot Instances

Use cloud spot/preemptible instances for non-critical services.

## Disaster Recovery

### 1. Multi-region Deployment

Deploy to multiple regions with DNS failover.

### 2. Database Replication

Use PostgreSQL instead of SQLite for production:
```yaml
postgres:
  image: postgres:15
  environment:
    POSTGRES_DB: knowledge
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
  volumes:
    - postgres-data:/var/lib/postgresql/data
```

### 3. Health Monitoring

Set up alerts:
```yaml
# alertmanager.yml
route:
  receiver: 'email'
  
receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@example.com'
        from: 'alerts@example.com'
```

## Checklist Before Going Live

- [ ] SSL certificates configured
- [ ] Authentication enabled
- [ ] Rate limiting active
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] Backups automated
- [ ] Monitoring dashboards set up
- [ ] Alerts configured
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations

## Maintenance

### Regular Tasks

**Daily:**
- Check service health
- Review error logs
- Monitor resource usage

**Weekly:**
- Review performance metrics
- Check backup integrity
- Update dependencies

**Monthly:**
- Security audit
- Cost analysis
- Capacity planning

### Updates

```bash
# Update services
docker-compose pull
docker-compose up -d

# Update models
docker-compose exec llm-service python -c "from transformers import AutoModel; AutoModel.from_pretrained('model-name')"
```
