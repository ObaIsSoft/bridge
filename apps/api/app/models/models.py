from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bridges = relationship("Bridge", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="user", cascade="all, delete-orphan")

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    key_hash = Column(String(64), unique=True, nullable=False)
    prefix = Column(String(12), nullable=False)
    last_four = Column(String(4), nullable=False)
    name = Column(String(255), default="Default Key")
    rate_limit_per_day = Column(Integer, default=100)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")

class Bridge(Base):
    __tablename__ = "bridges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=True) # For named lookups
    domain = Column(String(255), nullable=False)
    target_url = Column(Text, nullable=False)
    extraction_schema = Column(JSON, nullable=False)
    selectors = Column(JSON, nullable=True)
    
    # Phase 4: User Simulation & Auth
    auth_config = Column(JSON, nullable=True) # { "type": "cookie"|"login", "data": ... }
    interaction_script = Column(JSON, nullable=True) # [ { "action": "click", "selector": "#login" }, ... ]
    session_data = Column(JSON, nullable=True) # Persistent session storage (Cookies, LocalStorage)
    
    status = Column(String(20), default="active")
    last_successful_extraction = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="bridges")
    usage_logs = relationship("UsageLog", back_populates="bridge", cascade="all, delete-orphan")

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    bridge_id = Column(UUID(as_uuid=True), ForeignKey("bridges.id", ondelete="CASCADE"), nullable=True)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True)
    
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Integer, nullable=True)
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="usage_logs")
    bridge = relationship("Bridge", back_populates="usage_logs")

class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    url = Column(String(500), nullable=False)
    name = Column(String(255), default="Default Webhook")
    secret = Column(String(255), nullable=True) # For signing requests
    is_active = Column(Boolean, default=True)
    events = Column(JSON, default=lambda: ["extraction.success", "extraction.failed"])
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="webhooks")
    logs = relationship("WebhookLog", back_populates="webhook", cascade="all, delete-orphan")

class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id", ondelete="CASCADE"))
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    webhook = relationship("Webhook", back_populates="logs")

class DomainPermission(Base):
    __tablename__ = "domain_permissions"

    domain = Column(String(255), primary_key=True)
    status = Column(String(20), nullable=False) # ALLOWED, RESTRICTED, DENIED
    robots_txt = Column(Text, nullable=True)
    security_txt = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    twitter_handle = Column(String(255), nullable=True)
    github_handle = Column(String(255), nullable=True)
    linkedin_handle = Column(String(255), nullable=True)
    crawl_delay = Column(Integer, default=1) # Seconds
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class HandshakeRequest(Base):
    __tablename__ = "handshake_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    domain = Column(String(255), nullable=False)
    
    # Outreach Details
    method = Column(String(50), nullable=False) # 'EMAIL', 'TWITTER', 'GITHUB'
    recipient = Column(String(255), nullable=False) # email, handle, or username
    status = Column(String(50), default="DRAFT") # DRAFT, PENDING_APPROVAL, SENT, FAILED
    
    # Message Content
    message_subject = Column(String(255), nullable=True)
    message_body = Column(Text, nullable=False)
    
    # Tracking
    remote_id = Column(String(255), nullable=True) # Tweet ID, GitHub Issue ID, Message ID
    error_log = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
