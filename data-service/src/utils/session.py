from sqlalchemy.ext.asyncio import AsyncSession
from db import async_session


async def get_session() -> AsyncSession:
    """Getting async session"""
    async with async_session() as session:
        yield session
