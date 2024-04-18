from sqlalchemy import text


async def add_column(table_name: str, column_name: str, column_type: str, session):
    await session.execute(text('ALTER TABLE "%s" ADD COLUMN "%s" %s NULL' % (table_name, column_name, column_type)))
    await session.commit()
