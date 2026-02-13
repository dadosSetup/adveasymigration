from migration.db import connect


def migrate_users():
    with connect("v1") as conn_v1, connect("v2") as conn_v2:
        with conn_v1.cursor() as cursor_v1, conn_v2.cursor() as cursor_v2:

            cursor_v1.execute(
                """
                SELECT DISTINCT ON (u.email)
                    u.email,
                    u.created_at,
                    u.updated_at
                FROM
                    doctors d
                    LEFT JOIN doctor_subscriptions ds ON d.id = ds.doctor_id
                    JOIN users u ON d.user_id = u.id
                WHERE
                    d.account_stage IN (1, 2)
                    AND (
                        ds.canceled_at IS NULL
                        OR ds.canceled_at >= CURRENT_DATE - INTERVAL '30 days'
                    )
                    AND ds.started_at IS NOT NULL
                ORDER BY
                    ds.started_at
            """
            )
            rows = cursor_v1.fetchall()

            if not rows:
                print("No users to migrate")
                return

            for email, created_at, updated_at in rows:

                cursor_v2.execute("SELECT 1 FROM users WHERE email =%s", (email,))

                if cursor_v2.fetchone():
                    print(f"User already exists: {email}")
                    continue

                cursor_v2.execute(
                    """
                    INSERT INTO users (email, type, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (email, 2, created_at, updated_at),
                )

                user_id = cursor_v2.fetchone()[0]
                print(f"User migrated successfully: {email} -> ID: {user_id})")
