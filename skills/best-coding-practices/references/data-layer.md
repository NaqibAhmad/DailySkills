# Data layer (SQLAlchemy 2.0, async)

The repository layer of the One Pattern. Everything here lives in `<domain>/models.py`, `<domain>/repository.py` or `app/database.py`.

## Typed models

```python
# app/meetings/models.py
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Meeting(Base):
    __tablename__ = "dsr_discovery_meeting"  # snake_case, singular, domain prefix

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discovery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dsr_discovery_engagement.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(Text, default="")
    topic_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
```

- `Base` is defined once, in `app/database.py`.
- `_at` suffix for UTC datetimes, `_date` for dates.

## Indexes

Index every column used to filter, join or sort: foreign keys, status fields, scope ids, `created_at` when lists sort by it.

```python
from sqlalchemy import Index, text

__table_args__ = (
    Index("ix_order_user_status", "user_id", "status"),                              # composite: multi-column filter
    Index("ix_user_active_created", "created_at", postgresql_where=text("status = 'active'")),  # partial
    Index("ix_user_email_lower", text("lower(email)")),                             # expression
)
```

## Repository: the only SQL site

```python
# app/meetings/repository.py
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Meeting


class MeetingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_for_discovery(self, discovery_id: uuid.UUID) -> list[Meeting]:
        result = await self.session.execute(
            select(Meeting)
            .where(Meeting.discovery_id == discovery_id)   # scoped
            .order_by(Meeting.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, meeting_id: uuid.UUID, discovery_id: uuid.UUID) -> Meeting | None:
        result = await self.session.execute(
            select(Meeting).where(Meeting.id == meeting_id, Meeting.discovery_id == discovery_id)
        )
        return result.scalar_one_or_none()

    async def add(self, meeting: Meeting) -> Meeting:
        self.session.add(meeting)
        await self.session.flush()
        await self.session.refresh(meeting)
        return meeting
```

- Every query is scoped (see the three security rules in SKILL.md).
- Raw `text()` is for genuinely dynamic SQL only: isolated in the repository, parameterised, with a comment saying why.
- List endpoints that need a few fields select just those columns: `select(User.id, User.email)` returns rows, not ORM objects.

## Loading relationships in async

Lazy loading raises in async code, so load relationships in the query:

```python
from sqlalchemy.orm import joinedload, selectinload

select(User).options(
    joinedload(User.profile),                                   # many-to-one / one-to-one
    selectinload(User.orders).selectinload(Order.items),        # collections: avoids N+1
)
```

## Sessions, engine and the request commit

```python
# app/database.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    pass


_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        engine = create_async_engine(
            get_settings().database_url,
            pool_size=5, max_overflow=5, pool_timeout=30,
            pool_pre_ping=True, pool_recycle=300,
        )
        _sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return _sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _get_sessionmaker()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**One commit per request**, at this session boundary. Services and repositories `flush()` (to get ids, to surface constraint errors early); they leave committing to `get_db`. That makes every request atomic for free: order statements so constraints hold at flush time.

- Many rows: `session.add_all(rows)` or `await session.execute(insert(Model).returning(Model), rows)`. For thousands of rows, execute in chunks of ~1,000; still one commit.
- Work outside a request (scripts, workers) owns its own transaction: `async with sessionmaker() as session, session.begin(): ...`.
- Sessions are always opened with `async with`, so they close on every path.

## Migrations

- Shipped as files (`YYYYMMDDhhmmss_<what_it_does>.sql`, or Alembic dated slugs), static and reversible, and applied by the project owner rather than run ad hoc against a shared database.
- Large Postgres tables: `CREATE INDEX CONCURRENTLY` (in Alembic: `postgresql_concurrently=True` inside `op.get_context().autocommit_block()`).
- New NOT NULL column on a populated table, in three steps: add it nullable → backfill in batches → set NOT NULL.

```sql
-- batch backfill (repeat until 0 rows updated)
UPDATE users SET normalized_email = lower(email)
WHERE id IN (SELECT id FROM users WHERE normalized_email IS NULL LIMIT 1000);
```
