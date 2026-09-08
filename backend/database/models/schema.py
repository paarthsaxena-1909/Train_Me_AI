from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class AuditFields:
    _id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deletedAt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Agent(AuditFields, Base):
    __tablename__ = "agents"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)


class Admin(AuditFields, Base):
    __tablename__ = "admins"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class BlobItem(AuditFields, Base):
    __tablename__ = "blob_items"

    key: Mapped[str] = mapped_column(String(1024), nullable=False)
    bucket: Mapped[str] = mapped_column(String(255), nullable=False)


class Assignment(AuditFields, Base):
    __tablename__ = "assignments"

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AssignmentQuestion(AuditFields, Base):
    __tablename__ = "assignment_questions"

    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation: Mapped[str] = mapped_column(Text, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products._id", ondelete="CASCADE"), nullable=False, index=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments._id", ondelete="CASCADE"), nullable=False, index=True
    )


class AssignmentAgentMapping(AuditFields, Base):
    __tablename__ = "assignment_agent_mapping"

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents._id", ondelete="CASCADE"), nullable=False, index=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments._id", ondelete="CASCADE"), nullable=False, index=True
    )


class AgentQuery(AuditFields, Base):
    __tablename__ = "agent_queries"

    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products._id", ondelete="CASCADE"), nullable=False, index=True)


class ProductLineup(AuditFields, Base):
    __tablename__ = "product_lineups"

    lineup_identifier: Mapped[str] = mapped_column(String(255), nullable=False)


class ProductVariant(AuditFields, Base):
    __tablename__ = "product_variants"

    specs: Mapped[str] = mapped_column(Text, nullable=False)
    product_lineup_id: Mapped[int] = mapped_column(
        ForeignKey("product_lineups._id", ondelete="CASCADE"), nullable=False, index=True
    )


class Product(AuditFields, Base):
    __tablename__ = "products"

    product_lineup_id: Mapped[int] = mapped_column(
        ForeignKey("product_lineups._id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants._id", ondelete="CASCADE"), nullable=False, index=True
    )
