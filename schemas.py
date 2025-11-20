"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user"
- Article -> "article"
- AuditRequest -> "auditrequest"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ---------------------------------------------------------------------
# Core site schemas
# ---------------------------------------------------------------------

class Article(BaseModel):
    """
    Articles for the Knowledge Hub (blog).
    Collection: "article"
    """
    title: str = Field(..., description="Article title")
    slug: str = Field(..., description="URL-friendly slug")
    summary: str = Field(..., description="Short summary for listing")
    content: str = Field(..., description="HTML/Markdown content")
    author: str = Field(..., description="Author display name")
    tags: List[str] = Field(default_factory=list, description="Topic tags")
    published: bool = Field(default=False, description="Publish status")
    published_at: Optional[datetime] = Field(default=None, description="Publish time")

class AuditRequest(BaseModel):
    """
    Lead submissions for the Marketing Governance Audit.
    Collection: "auditrequest"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Work email")
    firm: str = Field(..., description="Firm name")
    industry: str = Field(..., description="Industry vertical")
    monthly_marketing_spend: Optional[float] = Field(None, ge=0, description="Approx monthly spend")
    phone: Optional[str] = Field(None, description="Phone number")
    notes: Optional[str] = Field(None, description="Context, risks, objectives")
    preferred_time: Optional[str] = Field(None, description="Preferred time for a call")
    source: Optional[str] = Field("website", description="Submission source")

# Example user schema retained for reference/testing
class User(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True
