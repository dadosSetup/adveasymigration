def resolve_state_id(cursor, uf: str) -> int | None:
    cursor.execute(" SELECT id FROM states WHERE code = %s", (uf,))
    row = cursor.fetchone()
    return row[0] if row else None
