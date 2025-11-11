# Deployment Guide

## Quick Start

1. **Clone and setup**:
```bash
git clone <repository-url>
cd crypthography--vuln-scan
```

2. **Create .env file**:
```bash
cp ENV_EXAMPLE.txt .env
# Edit .env and change JWT_SECRET_KEY to a secure random string
```

3. **Start services**:
```bash
docker-compose up --build
```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Login**:
   - Email: admin@example.com
   - Password: admin123

## Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random string (min 32 characters)
- [ ] Change default database passwords
- [ ] Configure `ALLOWED_TARGETS` to restrict scan targets
- [ ] Enable HTTPS/TLS for API and frontend
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backup for PostgreSQL
- [ ] Review and adjust resource limits in docker-compose.yml
- [ ] Set up monitoring and alerting

### Environment Variables

Key variables to configure for production:

```bash
# Security
JWT_SECRET_KEY=<generate-strong-random-key>
ALLOWED_TARGETS=your-domain.com,another-domain.com

# Database
POSTGRES_PASSWORD=<strong-password>

# Storage
STORAGE_PATH=/var/lib/cryptscan/storage
REPORT_RETENTION_DAYS=90

# Performance
SCAN_TIMEOUT_SECONDS=600
MAX_CONCURRENT_SCANS=5
```

### Resource Requirements

Minimum:
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB

Recommended:
- CPU: 4 cores
- RAM: 8GB
- Disk: 100GB (for storage of reports)

### Scaling

For higher load:

1. **Increase worker concurrency**:
   - Edit `docker-compose.yml`: `--concurrency=5` in worker command

2. **Add multiple workers**:
   ```yaml
   worker-1:
     # ... same config
   worker-2:
     # ... same config
   ```

3. **Use external PostgreSQL/Redis**:
   - Point `DATABASE_URL` and `REDIS_URL` to external services

### Backup

1. **Database backup**:
```bash
docker-compose exec postgres pg_dump -U cryptscan cryptscan_db > backup.sql
```

2. **Storage backup**:
```bash
tar -czf storage_backup.tar.gz storage/
```

### Monitoring

Health check endpoints:
- API: `GET /health`
- Worker: Check Celery status

Logs:
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

### Troubleshooting

**Worker not processing tasks**:
- Check Redis connection: `docker-compose exec redis redis-cli ping`
- Check worker logs: `docker-compose logs worker`

**Scans failing**:
- Check worker logs for errors
- Verify testssl.sh and nmap are installed in worker container
- Check network connectivity from worker to targets

**PDF generation failing**:
- Ensure WeasyPrint dependencies are installed
- Check storage directory permissions

**Database connection issues**:
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check connection string in .env

