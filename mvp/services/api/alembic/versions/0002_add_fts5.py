"""add fts5 virtual table for memory search

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-19
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create FTS5 virtual table for full-text search on memory_nodes.

    We use a STANDALONE FTS5 table (not contentless) so that snippet() and
    highlight() work correctly. Triggers keep the FTS in sync with memory_nodes.

    Per docs/03 §40: text search P95 < 100ms for 10k memories.
    """
    # Standalone FTS5 table — stores its own copy of label + content_text
    op.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_nodes_fts
        USING fts5(
            label,
            content_text,
            workspace_id UNINDEXED,
            status UNINDEXED
        )
        """
    )

    # Populate from existing memory_nodes (if any)
    op.execute(
        """
        INSERT INTO memory_nodes_fts(rowid, label, content_text, workspace_id, status)
        SELECT rowid, label, COALESCE(content_ciphertext, ''), workspace_id, status
        FROM memory_nodes
        WHERE status = 'active'
        """
    )

    # Triggers to keep FTS in sync with memory_nodes
    # On INSERT: add to FTS
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS memory_nodes_ai
        AFTER INSERT ON memory_nodes
        BEGIN
            INSERT INTO memory_nodes_fts(rowid, label, content_text, workspace_id, status)
            VALUES (new.rowid, new.label, COALESCE(new.content_ciphertext, ''), new.workspace_id, new.status);
        END
        """
    )

    # On DELETE: remove from FTS
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS memory_nodes_ad
        AFTER DELETE ON memory_nodes
        BEGIN
            DELETE FROM memory_nodes_fts WHERE rowid = old.rowid;
        END
        """
    )

    # On UPDATE: update FTS (delete + reinsert)
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS memory_nodes_au
        AFTER UPDATE ON memory_nodes
        BEGIN
            DELETE FROM memory_nodes_fts WHERE rowid = old.rowid;
            INSERT INTO memory_nodes_fts(rowid, label, content_text, workspace_id, status)
            VALUES (new.rowid, new.label, COALESCE(new.content_ciphertext, ''), new.workspace_id, new.status);
        END
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS memory_nodes_au")
    op.execute("DROP TRIGGER IF EXISTS memory_nodes_ad")
    op.execute("DROP TRIGGER IF EXISTS memory_nodes_ai")
    op.execute("DROP TABLE IF EXISTS memory_nodes_fts")
