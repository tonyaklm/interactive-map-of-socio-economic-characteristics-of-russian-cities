from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def add_column(table_name: str, column_name: str, column_type: str, session: AsyncSession):
    await session.execute(text('ALTER TABLE "%s" ADD COLUMN "%s" %s NULL' % (table_name, column_name, column_type)))
    await session.commit()


async def get_columns(table_name: str, session: AsyncSession):
    result = await session.execute(text('SELECT * FROM "%s" WHERE 1=0' % table_name))
    await session.commit()

    return result


async def get_column_type(column_name: str, table_name: str, session: AsyncSession):
    result = await session.execute(
        text('SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = :table_name'),
        {"table_name": table_name}
    )
    await session.commit()

    columns = {}
    for el in result.fetchall():
        columns[el[0]] = el[1]

    return columns
