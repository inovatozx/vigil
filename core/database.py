from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

from core.config import get_settings
from core.constants import DB_PATH

settings = get_settings()

# Ensure the data directory exists
import os
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    totp_secret = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    api_tokens = relationship("APIToken", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    documents = relationship("Document", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    notes = relationship("Note", back_populates="user")
    gallery_images = relationship("GalleryImage", back_populates="user")
    research_projects = relationship("ResearchProject", back_populates="user")
    provider_configs = relationship("ProviderConfig", back_populates="user")
    user_preferences = relationship("UserPreferences", uselist=False, back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    email_accounts = relationship("EmailAccount", back_populates="user")

class APIToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_tokens")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pinned = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    model = Column(String, nullable=True)
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    tool_calls = Column(Text, nullable=True) # JSON array
    attachments = Column(Text, nullable=True) # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True) # fact/preference/context
    source = Column(String, nullable=True) # de onde veio (chat, manual)
    embedding_id = Column(String, nullable=True) # referência no ChromaDB
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="memories")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    format = Column(String, default="markdown") # markdown/html/csv/txt
    folder = Column(String, nullable=True)
    tags = Column(Text, nullable=True) # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="documents")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending") # pending/in_progress/done/cancelled
    priority = Column(Integer, default=0)
    due_date = Column(DateTime, nullable=True)
    agent_assignable = Column(Boolean, default=False)
    cron_expression = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    pinned = Column(Boolean, default=False)
    tags = Column(Text, nullable=True) # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="notes")

class GalleryImage(Base):
    __tablename__ = "gallery_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    prompt = Column(Text, nullable=True)
    model = Column(String, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    tags = Column(Text, nullable=True) # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="gallery_images")

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    status = Column(String, default="running") # running/completed/failed
    report_html = Column(Text, nullable=True)
    sources = Column(Text, nullable=True) # JSON array de URLs
    steps_log = Column(Text, nullable=True) # JSON array de passos
    model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="research_projects")

class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String, nullable=False) # openai/anthropic/groq/ollama/etc
    api_key_encrypted = Column(Text, nullable=True)
    base_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="provider_configs")

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    theme = Column(String, default="dark")
    default_model = Column(String, nullable=True)
    language = Column(String, default="pt-BR")
    sidebar_collapsed = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    preferences_json = Column(Text, nullable=True) # JSON para prefs extras

    user = relationship("User", back_populates="user_preferences")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    all_day = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True) # RRULE
    location = Column(String, nullable=True)
    caldav_uid = Column(String, nullable=True) # para sync
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calendar_events")

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String, nullable=False)
    imap_host = Column(String, nullable=False)
    imap_port = Column(Integer, default=993)
    smtp_host = Column(String, nullable=False)
    smtp_port = Column(Integer, default=587)
    username = Column(String, nullable=False)
    password_encrypted = Column(Text, nullable=False) # criptografado
    display_name = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="email_accounts")
    emails = relationship("Email", back_populates="account", cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("email_accounts.id"))
    message_id = Column(String, unique=True, nullable=True)
    subject = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    recipients = Column(Text, nullable=True) # JSON
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    folder = Column(String, nullable=True)
    tags = Column(Text, nullable=True) # JSON array
    summary = Column(Text, nullable=True) # gerado por AI
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("EmailAccount", back_populates="emails")

# Create all tables
Base.metadata.create_all(bind=engine)
