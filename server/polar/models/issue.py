import enum
from typing import TYPE_CHECKING
from uuid import UUID
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    MappedColumn,
    declared_attr,
    mapped_column,
    relationship,
)


from polar.issue.signals import issue_created, issue_updated
from polar.kit.db.models import RecordModel
from polar.kit.extensions.sqlalchemy import PostgresUUID, StringEnum
from polar.enums import Platforms

from polar.types import JSONDict, JSONList

import sqlalchemy as sa
from sqlalchemy_utils.types.ts_vector import TSVectorType  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from polar.models.issue_reference import IssueReference
    from polar.models.organization import Organization
    from polar.models.repository import Repository
    from polar.models.pledge import Pledge


class Platform(enum.Enum):
    GITHUB = "github"


class IssueFields:
    class State(str, enum.Enum):
        OPEN = "open"
        CLOSED = "closed"

    platform: Mapped[Platform] = mapped_column(StringEnum(Platforms), nullable=False)
    external_id: Mapped[int] = mapped_column(Integer, nullable=False)

    @declared_attr
    def organization_id(cls) -> MappedColumn[UUID]:
        return mapped_column(
            PostgresUUID,
            ForeignKey("organizations.id"),
            nullable=False,
            index=True,
        )

    @declared_attr
    def organization(cls) -> "Mapped[Organization]":
        return relationship("Organization", lazy="raise")

    @declared_attr
    def repository_id(cls) -> "MappedColumn[UUID]":
        return mapped_column(
            PostgresUUID,
            ForeignKey("repositories.id"),
            nullable=False,
            index=True,
        )

    @declared_attr
    def repository(cls) -> "Mapped[Repository]":
        return relationship("Repository", lazy="raise")

    number: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)

    author: Mapped[JSONDict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=dict
    )
    author_association: Mapped[str | None] = mapped_column(String, nullable=True)
    labels: Mapped[JSONList | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=list
    )
    assignee: Mapped[JSONDict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=dict
    )
    assignees: Mapped[JSONList | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=list
    )
    milestone: Mapped[JSONDict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=dict
    )
    closed_by: Mapped[JSONDict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=dict
    )
    reactions: Mapped[JSONDict | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, default=dict
    )

    state: Mapped[str] = mapped_column(StringEnum(State), nullable=False)
    state_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    issue_closed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    issue_created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    issue_modified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    title_tsv: Mapped[TSVectorType] = mapped_column(
        TSVectorType("title", regconfig="simple"),
        sa.Computed("to_tsvector('simple', \"title\")", persisted=True),
    )


issue_fields_mutables = {
    "title",
    "body",
    "comments",
    "author",
    "author_association",
    "labels",
    "assignee",
    "assignees",
    "milestone",
    "closed_by",
    "reactions",
    "state",
    "state_reason",
    "issue_closed_at",
    "issue_modified_at",
}


class Issue(IssueFields, RecordModel):
    __tablename__ = "issues"
    __table_args__ = (
        UniqueConstraint("external_id"),
        UniqueConstraint("organization_id", "repository_id", "number"),
        # Search index
        Index("idx_issues_title_tsv", "title_tsv", postgresql_using="gin"),
        Index(
            "idx_issues_id_closed_at",
            "id",
            "issue_closed_at",
        ),
        Index(
            "idx_issues_pledged_amount_sum",
            "pledged_amount_sum",
        ),
        Index(
            "idx_issues_reactions_plus_one",
            sqlalchemy.text("((reactions::jsonb ->> 'plus_one')::int)"),
            postgresql_using="btree",
        ),
    )

    pledge_badge_embedded_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    github_issue_etag: Mapped[str | None] = mapped_column(String, nullable=True)
    github_issue_fetched_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    github_timeline_etag: Mapped[str | None] = mapped_column(String, nullable=True)
    github_timeline_fetched_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    @declared_attr
    def references(cls) -> "Mapped[list[IssueReference]]":
        return relationship("IssueReference", lazy="raise", viewonly=True)

    @declared_attr
    def pledges(cls) -> "Mapped[list[Pledge]]":
        return relationship(
            "Pledge",
            lazy="raise",
            viewonly=True,
            primaryjoin="""and_(Issue.id == Pledge.issue_id, Pledge.state.in_(
                ['created', 'pending', 'paid', 'disputed']))""",
        )

    # calculated sum of pledges, used for sorting
    # not to be exported through APIs
    pledged_amount_sum: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )

    issue_has_in_progress_relationship: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    issue_has_pull_request_relationship: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    on_created_signal = issue_created
    on_updated_signal = issue_updated

    __mutables__ = issue_fields_mutables
