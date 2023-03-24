"""s3_path_fields

Revision ID: 22f9da51ea7f
Revises: 51d187719e71
Create Date: 2023-03-08 11:23:30.956265

"""
import sqlalchemy as sa
from alembic import op

from app.constants import INSTANCE_PATH_PREFIX

# revision identifiers, used by Alembic.
revision = "22f9da51ea7f"
down_revision = "51d187719e71"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("dataasset", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "s3_path_prefix",
                sa.String(length=1025),
                server_default=INSTANCE_PATH_PREFIX,
                nullable=False,
            )
        )
        batch_op.alter_column(
            "file_path", nullable=False, new_column_name="s3_partition_path"
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("dataasset", schema=None) as batch_op:
        batch_op.alter_column(
            "s3_partition_path", nullable=False, new_column_name="file_path"
        )
        batch_op.drop_column("s3_path_prefix")

    # ### end Alembic commands ###
