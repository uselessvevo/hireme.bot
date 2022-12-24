import json
import typing
import asyncio

from asyncpg import UniqueViolationError, ForeignKeyViolationError

from core.database import Database


def setup_database() -> Database:
    loop = asyncio.get_event_loop()
    database = Database(loop)
    return database


def read_json_file(json_file: str = "areas.json") -> typing.Any:
    with open(json_file, "r", encoding="utf8") as output:
        return json.load(output)


async def try_int(value, default) -> typing.Any:
    try:
        return int(value)
    except TypeError:
        return default


async def populate_areas_table() -> None:
    for output in read_json_file("areas.json"):
        print("Country: %s" % output.get("name"))
        if not await db.pool.fetch(
            """
            SELECT id FROM areas WHERE id = $1
            """,
            int(output.get("id"))
        ):
            await db.pool.execute(
                """
                INSERT INTO areas VALUES ($1, $2, $3)
                """,
                int(output.get("id")),
                await try_int(output.get("parent_id"), None),
                output.get("name"),
            )

        if output.get("areas"):
            for area in output.get("areas"):
                try:
                    print("Area: %s\n" % area.get("name"))
                    await db.pool.execute(
                        """
                        INSERT INTO areas VALUES ($1, $2, $3)
                        """,
                        int(area.get("id")),
                        int(area.get("parent_id")),
                        area.get("name"),
                    )
                except UniqueViolationError:
                    pass
                except ForeignKeyViolationError:
                    print("ForeignKeyViolationError %s" % area.get("id"))


if __name__ == '__main__':
    db = setup_database()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(populate_areas_table())
