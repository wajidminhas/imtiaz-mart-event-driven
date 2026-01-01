"""Initial migration - create payments table

Revision ID: 069c3f395de3
Revises: 
Create Date: 2025-12-27 16:24:28.686585

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '069c3f395de3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create payments table."""
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('payment_method', sa.String(), nullable=False),
        sa.Column('payment_provider', sa.String(length=50), nullable=False),
        sa.Column('provider_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('provider_payment_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('payment_metadata', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('refunded_amount', sa.Float(), nullable=False),
        sa.Column('failure_reason', sa.String(length=500), nullable=True),
        sa.Column('failure_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('expired_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_payments_order_id', 'payments', ['order_id'])
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_provider_transaction_id', 'payments', ['provider_transaction_id'])


def downgrade() -> None:
    """Downgrade schema - drop payments table."""
    op.drop_index('ix_payments_provider_transaction_id', table_name='payments')
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_user_id', table_name='payments')
    op.drop_index('ix_payments_order_id', table_name='payments')
    op.drop_table('payments')
