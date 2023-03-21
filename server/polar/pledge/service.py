from __future__ import annotations

from uuid import UUID
from typing import List, Sequence

import structlog

from polar.kit.services import ResourceService
from polar.models.pledge import Pledge
from polar.postgres import AsyncSession, sql

from .schemas import PledgeCreate, PledgeUpdate

log = structlog.get_logger()


class PledgeService(ResourceService[Pledge, PledgeCreate, PledgeUpdate]):
    async def list_by_repository(
        self, session: AsyncSession, repository_id: UUID
    ) -> Sequence[Pledge]:
        statement = sql.select(Pledge).where(Pledge.repository_id == repository_id)
        res = await session.execute(statement)
        issues = res.scalars().unique().all()
        return issues

    async def get_by_issue_ids(
        self,
        session: AsyncSession,
        issue_ids: List[UUID],
    ) -> Sequence[Pledge]:
        if not issue_ids:
            return []
        statement = sql.select(Pledge).filter(Pledge.issue_id.in_(issue_ids))
        res = await session.execute(statement)
        issues = res.scalars().unique().all()
        return issues


pledge = PledgeService(Pledge)