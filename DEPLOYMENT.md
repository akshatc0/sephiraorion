# Sephira Orion - Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Use strong, unique API keys
- [ ] Configure secure `SECRET_KEY` if using authentication
- [ ] Set appropriate `MAX_QUERIES_PER_MINUTE` and `MAX_QUERIES_PER_HOUR`

### 2. Security
- [ ] Review and harden CORS settings in `backend/api/main.py`
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure rate limiting appropriately
- [ ] Review security logs regularly

### 3. Data & Database
- [ ] Ensure sentiment data is up to date
- [ ] Back up ChromaDB data (`data/chroma/`)
- [ ] Test data loading and embedding generation
- [ ] Verify all processed data files exist

### 4. Testing
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Test all API endpoints manually
- [ ] Load test the API
- [ ] Test frontend in production mode

## Deployment Options

### Option 1: Docker Deployment (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/chroma logs

# Expose ports
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
    
  frontend:
    build: .
    command: streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    depends_on:
      - backend
    env_file:
      - .env
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

### Option 2: Cloud Deployment (AWS)

#### Backend on EC2/ECS

1. **Prepare instance**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3-pip -y

# Clone repository
git clone <your-repo>
cd sephira4

# Install dependencies
pip3 install -r requirements.txt
```

2. **Set up systemd service** (`/etc/systemd/system/sephira-backend.service`):
```ini
[Unit]
Description=Sephira Orion Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/sephira4
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sephira-backend
sudo systemctl start sephira-backend
```

4. **Set up Nginx reverse proxy**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Frontend on Streamlit Cloud

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit dashboard
4. Deploy

### Option 3: Cloud Run (GCP)

1. **Create Dockerfile** (see Option 1)

2. **Build and push**:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/sephira
```

3. **Deploy**:
```bash
gcloud run deploy sephira \
  --image gcr.io/PROJECT-ID/sephira \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: Traditional VPS

1. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3.10 python3-pip nginx supervisor -y
```

2. **Set up Supervisor** (`/etc/supervisor/conf.d/sephira.conf`):
```ini
[program:sephira-backend]
directory=/home/user/sephira4
command=/usr/bin/python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
autostart=true
autorestart=true
stderr_logfile=/var/log/sephira/backend.err.log
stdout_logfile=/var/log/sephira/backend.out.log

[program:sephira-frontend]
directory=/home/user/sephira4
command=streamlit run frontend/app.py --server.port 8501
autostart=true
autorestart=true
stderr_logfile=/var/log/sephira/frontend.err.log
stdout_logfile=/var/log/sephira/frontend.out.log
```

3. **Start services**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

## Production Configuration

### Environment Variables

```env
# Production settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# API Keys (use secrets manager in production)
OPENAI_API_KEY=sk-...
NEWS_API_KEY=...
ALPHA_VANTAGE_KEY=...
FRED_API_KEY=...

# Database
CHROMADB_PATH=/var/lib/sephira/chroma

# Security
MAX_QUERIES_PER_MINUTE=20
MAX_QUERIES_PER_HOUR=500
MAX_RESPONSE_TOKENS=2000
RATE_LIMIT_ENABLED=true

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/sephira
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:8501;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }

    # API Documentation
    location /docs {
        proxy_pass http://backend/docs;
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

## Monitoring & Logging

### Set up logging

1. **Application logs**: Already configured in `backend/api/main.py`
2. **System logs**: Use `journalctl` or `supervisor logs`
3. **Nginx logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Monitoring tools

- **Uptime monitoring**: UptimeRobot, Pingdom
- **Application monitoring**: New Relic, DataDog
- **Log aggregation**: ELK Stack, Splunk
- **Metrics**: Prometheus + Grafana

### Key metrics to monitor

- API response times
- Error rates
- Rate limit violations
- Database query performance
- Memory and CPU usage
- Request volume

## Backup Strategy

### What to backup

1. **Data files**:
   - `data/raw/all_indexes_beta.csv`
   - `data/processed/*`

2. **Vector database**:
   - `data/chroma/*`

3. **Configuration**:
   - `.env` (store securely)
   - Custom configurations

4. **Logs** (optional):
   - `logs/*`

### Backup schedule

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/sephira/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/data.tar.gz data/

# Backup vector DB
tar -czf $BACKUP_DIR/chroma.tar.gz data/chroma/

# Backup configs
cp .env $BACKUP_DIR/.env.backup

# Keep only last 30 days
find /backups/sephira/ -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

## Scaling Considerations

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Enable Redis caching

### Horizontal Scaling
- Load balancer (HAProxy, AWS ELB)
- Multiple backend instances
- Shared ChromaDB or vector database cluster
- Redis for session management

### Performance Optimization
- Enable response caching
- Use CDN for static assets
- Optimize embedding generation
- Batch processing for predictions
- Connection pooling

## Troubleshooting

### Common issues

1. **High memory usage**:
   - Reduce batch sizes
   - Implement pagination
   - Clear unused sessions

2. **Slow responses**:
   - Enable caching
   - Optimize database queries
   - Scale horizontally

3. **Rate limit errors**:
   - Adjust limits in `.env`
   - Implement user authentication
   - Use Redis for distributed rate limiting

### Health checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Check logs
tail -f logs/sephira_$(date +%Y-%m-%d).log

# Monitor system resources
htop
df -h
```

## Security Best Practices

1. ✅ Use HTTPS everywhere
2. ✅ Keep dependencies updated
3. ✅ Regular security audits
4. ✅ Strong API keys
5. ✅ Rate limiting enabled
6. ✅ Input validation
7. ✅ Audit logging
8. ✅ Firewall configuration
9. ✅ Regular backups
10. ✅ Secrets management (AWS Secrets Manager, HashiCorp Vault)

## Post-Deployment

1. Test all endpoints
2. Monitor logs for errors
3. Set up alerts
4. Document any custom configurations
5. Train users
6. Establish support process

---

**Ready for Production! 🚀**
