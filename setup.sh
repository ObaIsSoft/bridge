#!/bin/bash
set -e

WORKSPACE_DIR="/Users/obafemi/bridge"
cd "$WORKSPACE_DIR"

echo "Setting up API Bridge Platform in $WORKSPACE_DIR..."

# Create directory structure
mkdir -p apps/{web,api,mcp-server}
mkdir -p packages/{shared-types,db-schema}
mkdir -p infrastructure/{docker,scripts}

# Initialize root package.json (Turborepo)
cat > package.json << 'PACKAGE'
{
  "name": "apibridge",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.3.3"
  }
}
PACKAGE

# Create turbo.json
cat > turbo.json << 'TURBO'
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {}
  }
}
TURBO

echo "Root structure created"

# Create Docker Compose
cat > docker-compose.yml << 'DOCKER'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: apibridge
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/docker/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
DOCKER

echo "Docker Compose created"

# Create database init script
mkdir -p infrastructure/docker
cat > infrastructure/docker/init.sql << 'SQL'
-- Initial database setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(64) UNIQUE NOT NULL,
    prefix VARCHAR(12) NOT NULL,
    last_four VARCHAR(4) NOT NULL,
    name VARCHAR(255) DEFAULT 'Default Key',
    rate_limit_per_day INT DEFAULT 100,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP
);

-- Bridges table
CREATE TABLE bridges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    target_url TEXT NOT NULL,
    schema JSONB NOT NULL,
    selectors JSONB,
    status VARCHAR(20) DEFAULT 'active',
    last_successful_extraction TIMESTAMP,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, domain) -- FIXED: Allow multiple bridges per user across different domains
);

-- Usage logs (partitioned)
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    bridge_id UUID REFERENCES bridges(id),
    api_key_id UUID REFERENCES api_keys(id),
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    status_code INT NOT NULL,
    latency_ms INT,
    cached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create current partition (FIXED: Updated for 2026-02)
CREATE TABLE usage_logs_2026_02 PARTITION OF usage_logs
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Indexes
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_bridges_user_id ON bridges(user_id);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
SQL

echo "Database init script created"

# Create apps/api/pyproject.toml
cat > apps/api/pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "apibridge-api"
version = "0.1.0"
description = "API Bridge Platform - Backend"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = "^2.0.25"
asyncpg = "^0.29.0"
redis = "^5.0.1"
pydantic = "^2.5.3"
pydantic-settings = "^2.1.0"
playwright = "^1.41.0"
openai = "^1.10.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
httpx = "^0.26.0"
celery = "^5.3.6"
pillow = "^10.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"
pytest-asyncio = "^0.23.3"
black = "^24.1.0"
mypy = "^1.8.0"
ruff = "^0.1.14"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"
PYPROJECT

echo "apps/api/pyproject.toml created"

# Create apps/api/main.py
cat > apps/api/main.py << 'MAIN'
"""
API Bridge Platform - Main FastAPI Application
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting API Bridge Platform...")
    # Initialize database connection pool
    # Initialize Redis connection
    # Install Playwright browsers
    yield
    logger.info("Shutting down API Bridge Platform...")
    # Cleanup connections


app = FastAPI(
    title="API Bridge Platform",
    description="Auto-generate APIs for websites without existing APIs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "API Bridge Platform",
        "version": "0.1.0"
    }


@app.get("/api/v1/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Check actual DB connection
        "redis": "connected",     # TODO: Check actual Redis connection
        "playwright": "ready"     # TODO: Check Playwright installation
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
MAIN

echo "apps/api/main.py created"

# Create app directory structure
mkdir -p apps/api/app/{core,models,routers,services,schemas}

# Create core modules
cat > apps/api/app/core/database.py << 'DB'
"""Database configuration and session management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/apibridge")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
DB

cat > apps/api/app/core/redis.py << 'REDIS'
"""Redis connection and cache utilities"""
import redis.asyncio as redis
import os
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
REDIS

cat > apps/api/app/core/config.py << 'CONFIG'
"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/apibridge"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Clerk
    clerk_secret_key: str = ""
    clerk_webhook_secret: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    
    # Rate Limiting
    default_rate_limit_per_day: int = 100
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
CONFIG

echo "Core modules created"

# Create .env.example
cat > .env.example << 'ENV'
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/apibridge

# Redis
REDIS_URL=redis://localhost:6379

# Clerk (get from https://clerk.com)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...

# OpenAI (for extraction)
OPENAI_API_KEY=sk-...

# API
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
ENV

echo " .env.example created"

echo "optimized Setup script execution complete!"
