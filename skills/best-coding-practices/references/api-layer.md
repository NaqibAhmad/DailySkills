# API layer (FastAPI + Pydantic v2)

The router layer of the One Pattern, plus the schemas and settings it relies on.

## Thin routers

```python
# app/meetings/router.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security import CurrentUser, get_current_user, require_discovery_access

from .exceptions import MeetingNotFoundError
from .schemas import MeetingCreate, MeetingResponse
from .service import MeetingService

router = APIRouter(tags=["meetings"])


def get_service(db: AsyncSession = Depends(get_db)) -> MeetingService:
    return MeetingService(db)


ServiceDep = Annotated[MeetingService, Depends(get_service)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    discovery_id: UUID, payload: MeetingCreate, service: ServiceDep, user: UserDep, db: DbDep
) -> MeetingResponse:
    await require_discovery_access(db, user, discovery_id)   # scope check, first statement
    return await service.create(discovery_id, payload, user)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    discovery_id: UUID, meeting_id: UUID, service: ServiceDep, user: UserDep, db: DbDep
) -> MeetingResponse:
    await require_discovery_access(db, user, discovery_id)
    try:
        return await service.get(meeting_id, discovery_id)
    except MeetingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
```

`get_db` is cached per request, so the service and the access check share one session.

- Every route declares `response_model` and its status code: 201 create, 204 delete, 403/404/409/422 where they mean something. Multi-route domains set `tags`.
- The scope check is the first statement, through the shared helper in `app/security.py`.
- Checks that a referenced row exists go in a dependency or the service. Reuse one dependency across routes; FastAPI caches its result per request.
- A route body holds parsing, the access check, one service call and exception mapping. SQL, prompt building and response shaping belong to the layers below.

## Async discipline

- Blocking SDK calls inside an async route go through `fastapi.concurrency.run_in_threadpool`.
- Write dependencies as `async def`; sync dependencies spend threadpool threads on trivial work.
- CPU-heavy work goes to a worker or queue, off the request path.

## Schemas

One base model; every API schema inherits it:

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """snake_case in Python, camelCase on the wire."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
```

- Validate at the boundary: `Field(min_length=…, ge=…, pattern=…)`, `Literal` for enums, `model_validator` for cross-field rules. A `ValueError` in a validator becomes a 422.
- Create, Update and Response are separate models. Update fields are `T | None`, so "not sent" and "sent empty" stay distinct. Explicit fields per model also block mass assignment.
- Schemas stay independent of ORM models; the service converts explicitly (`to_response()` helpers).
- Query parameters carry bounds (`limit: int = Query(50, ge=1, le=200)`).

## Settings and docs

- One `Settings` (pydantic-settings) in `app/config.py`, read through a cached `get_settings()`. Domain-local settings may live in `<domain>/config.py`. A missing required env var fails at startup.
- Outside local and staging, serve no OpenAPI docs: `FastAPI(openapi_url=None)`.
