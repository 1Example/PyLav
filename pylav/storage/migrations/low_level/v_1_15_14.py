from __future__ import annotations

from asyncpg import Connection

from pylav.storage.migrations.logging import LOGGER


TIMED_FEATURE_COLUMNS = ("empty_queue_dc", "alone_dc", "alone_pause")


async def low_level_v_1_15_14_migration(con: Connection) -> None:
    """Repair legacy boolean values stored in player timed-feature JSONB columns."""
    has_table = await con.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'player'
        )
        """
    )
    if not has_table:
        return

    # A few older database states contain JSON booleans (true/false) in these
    # columns, while the current schema expects {"enabled": bool, "time": int}.
    # Repair them in-place so existing installations can migrate without
    # requiring manual SQL intervention.
    for column in TIMED_FEATURE_COLUMNS:
        result = await con.execute(
            f"""
            UPDATE player
            SET "{column}" = jsonb_build_object(
                'enabled', ("{column}" = 'true'::jsonb),
                'time', 60
            )
            WHERE jsonb_typeof("{column}") = 'boolean'
            """
        )
        if result != "UPDATE 0":
            LOGGER.warning(
                "Repaired %s malformed boolean player timed-feature value(s): %s",
                column,
                result,
            )
