# Docker Homework

This homework assignment focuses on learning Docker concepts through hands-on exercises with a multi-service application.

## Overview

Build and manage a containerized data platform consisting of PostgreSQL database and pgAdmin web interface using Docker Compose.

## Services

### PostgreSQL Database (`pgdatabase`)
- **Image**: postgres:18
- **Purpose**: Primary database for storing NYC taxi data
- **Configuration**:
  - Database: ny_taxi
  - User: root
  - Password: root
  - Optimized for high-performance data ingestion
- **Ports**: 5432 (host) -> 5432 (container)
- **Volumes**: Persistent data storage

### pgAdmin (`pgadmin`)
- **Image**: dpage/pgadmin4
- **Purpose**: Web-based PostgreSQL administration interface
- **Configuration**:
  - Email: admin@admin.com
  - Password: root
- **Ports**: 8085 (host) -> 80 (container)
- **Volumes**: Persistent session data

## Getting Started

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

3. **Access pgAdmin**:
   - Open http://localhost:8085 in your browser
   - Login with admin@admin.com / root

4. **Connect to database in pgAdmin**:
   - Host: pgdatabase (service name)
   - Port: 5432
   - Database: ny_taxi
   - Username: root
   - Password: root

## Exercises

### Exercise 1: Basic Docker Operations
- Start/stop individual services
- View logs: `docker-compose logs [service_name]`
- Execute commands in containers: `docker-compose exec pgdatabase psql -U root -d ny_taxi`

### Exercise 2: Data Ingestion
- Use the pipeline from the `../pipeline/` directory
- Ingest NYC taxi data into the database
- Monitor ingestion progress and performance

### Exercise 3: Database Administration
- Create additional databases/tables through pgAdmin
- Run SQL queries and analyze data
- Export/import data

### Exercise 4: Docker Compose Configuration
- Modify docker-compose.yaml (add environment variables, networks, etc.)
- Add a new service (e.g., Redis, Nginx)
- Implement health checks

## Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Clean up (removes volumes)
docker-compose down -v
```

## Database Optimization

The PostgreSQL configuration includes performance optimizations:
- `synchronous_commit=off`: Faster writes (less durable)
- `shared_buffers=2GB`: Memory for caching
- `maintenance_work_mem=512MB`: Memory for maintenance operations
- `wal_compression=on`: Compress transaction logs
- `checkpoint_timeout=15min`: Checkpoint frequency
- `max_wal_size=4GB`: Maximum WAL size

## Troubleshooting

- **Port conflicts**: Ensure ports 5432 and 8085 are available
- **Permission issues**: Check Docker daemon permissions
- **Data persistence**: Data is stored in named volumes
- **Connection issues**: Use service names for inter-container communication