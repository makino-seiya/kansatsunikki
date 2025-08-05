#!/bin/bash

echo "=== Plant Growth Tracker Health Check ==="

# Check if Docker Compose is running
echo "Checking Docker Compose services..."
docker-compose ps

echo ""
echo "=== Service Health Status ==="

# Check database
echo "Database:"
if docker-compose exec -T database mysqladmin ping -h localhost --silent; then
    echo "✅ MySQL is running"
else
    echo "❌ MySQL is not responding"
fi

# Check MinIO
echo "MinIO:"
if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo "✅ MinIO is running"
else
    echo "❌ MinIO is not responding"
fi

# Check Backend
echo "Backend:"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI backend is running"
else
    echo "❌ FastAPI backend is not responding"
fi

# Check Frontend
echo "Frontend:"
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Nuxt frontend is running"
else
    echo "❌ Nuxt frontend is not responding"
fi

echo ""
echo "=== Access URLs ==="
echo "Frontend (User): http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Admin Panel: http://localhost:8000/admin"
echo "MinIO Console: http://localhost:9001"
echo ""
echo "=== Default Credentials ==="
echo "Basic Auth (User): plant_user / plant_pass"
echo "Admin Login: admin / admin123"
echo "MinIO: minioadmin / minioadmin123"