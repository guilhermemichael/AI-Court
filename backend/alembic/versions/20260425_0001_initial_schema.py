"""initial schema

Revision ID: 20260425_0001
Revises:
Create Date: 2026-04-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "20260425_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("plaintiff_name", sa.String(length=80), nullable=False),
        sa.Column("defendant_name", sa.String(length=80), nullable=False),
        sa.Column("plaintiff_argument", sa.Text(), nullable=False),
        sa.Column("defendant_argument", sa.Text(), nullable=False),
        sa.Column("conflict_type", sa.String(length=80), nullable=False),
        sa.Column("drama_level", sa.Integer(), nullable=False),
        sa.Column("allow_precedents", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="SUBMITTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("drama_level BETWEEN 1 AND 10", name="ck_cases_drama_level"),
    )
    op.create_table(
        "trial_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence_index", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("agent_role", sa.String(length=60), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("case_id", "sequence_index", name="uq_case_event_sequence"),
    )
    op.create_table(
        "verdicts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("winner", sa.String(length=40), nullable=False),
        sa.Column("guilt_index", sa.Numeric(5, 2), nullable=False),
        sa.Column("sentence", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("compensation_order", sa.Text(), nullable=True),
        sa.Column("appeal_allowed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "precedents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("principle", sa.String(length=140), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("outcome_trend", sa.String(length=80), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "house_laws",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("article_number", sa.String(length=20), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("severity BETWEEN 1 AND 10", name="ck_house_laws_severity"),
    )
    op.bulk_insert(
        sa.table(
            "house_laws",
            sa.column("title", sa.String()),
            sa.column("article_number", sa.String()),
            sa.column("description", sa.Text()),
            sa.column("severity", sa.Integer()),
        ),
        [
            {
                "title": "Lei da Louca Compartilhada",
                "article_number": "Art. 1o",
                "description": "Quem cozinha nao lava, salvo se sujar panelas demais por exibicionismo culinario.",
                "severity": 7,
            },
            {
                "title": "Abandono Textil",
                "article_number": "Art. 2o",
                "description": "Esquecer roupa na maquina por mais de 6 horas constitui abandono textil presumido.",
                "severity": 6,
            },
            {
                "title": "Crime Emocional do Ultimo Pedaco",
                "article_number": "Art. 3o",
                "description": "Consumir o ultimo pedaco sem aviso previo e ilicito emocional de alta gravidade.",
                "severity": 9,
            },
        ],
    )
    op.execute("CREATE INDEX precedents_embedding_idx ON precedents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")


def downgrade() -> None:
    op.drop_index("precedents_embedding_idx", table_name="precedents")
    op.drop_table("house_laws")
    op.drop_table("precedents")
    op.drop_table("verdicts")
    op.drop_table("trial_events")
    op.drop_table("cases")
