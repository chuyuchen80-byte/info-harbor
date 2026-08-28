"""初始：sources, articles, crawl_tasks

Revision ID: 3c9d2c1976b3
Revises:
Create Date: 2026-08-26 00:03:09.819197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '3c9d2c1976b3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('sources',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('country', sa.String(length=8), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.Column('adapter_key', sa.String(length=64), nullable=False),
    sa.Column('config', mysql.JSON(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('health', mysql.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('articles',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('source_id', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('url', sa.String(length=512), nullable=False),
    sa.Column('raw_url', sa.String(length=512), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('author', sa.String(length=200), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('detected_lang', sa.String(length=8), nullable=True),
    sa.Column('translated_lang', sa.String(length=8), nullable=True),
    sa.Column('content_translated', sa.Text(), nullable=True),
    sa.Column('country', sa.String(length=8), nullable=True),
    sa.Column('source_type', sa.String(length=32), nullable=False),
    sa.Column('tags', mysql.JSON(), nullable=False),
    sa.Column('entities', mysql.JSON(), nullable=False),
    sa.Column('categories', mysql.JSON(), nullable=False),
    sa.Column('cluster_id', sa.String(length=64), nullable=True),
    sa.Column('raw_snapshot_key', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('ext_json', mysql.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_articles_source_id'), 'articles', ['source_id'], unique=False)
    op.create_index(op.f('ix_articles_status'), 'articles', ['status'], unique=False)
    op.create_table('crawl_tasks',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('source_id', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('task_type', sa.String(length=32), nullable=False),
    sa.Column('arq_job_id', sa.String(length=64), nullable=True),
    sa.Column('result_count', sa.Integer(), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('finished_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crawl_tasks_source_id'), 'crawl_tasks', ['source_id'], unique=False)
    op.create_index(op.f('ix_crawl_tasks_status'), 'crawl_tasks', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_crawl_tasks_status'), table_name='crawl_tasks')
    op.drop_index(op.f('ix_crawl_tasks_source_id'), table_name='crawl_tasks')
    op.drop_table('crawl_tasks')
    op.drop_index(op.f('ix_articles_status'), table_name='articles')
    op.drop_index(op.f('ix_articles_source_id'), table_name='articles')
    op.drop_table('articles')
    op.drop_table('sources')
