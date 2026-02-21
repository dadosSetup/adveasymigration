from migration.db import connect


def migrate_lawyers():
    with connect("v1") as conn_v1, connect("v2") as conn_v2:
        with conn_v1.cursor() as cursor_v1, conn_v2.cursor() as cursor_v2:

            cursor_v1.execute(
                """
                SELECT
                    d.user_id,
                    u.email,
                    d.crm,
                    d.crm_uf,
                    d.payer_user,
                    d.approved_at,
                    d.created_at,
                    d.updated_at
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
                print("No lawyers to migrate")
                return

            for (
                old_user_id,
                email,
                crm,
                crm_uf,
                payer_user,
                approved_at,
                created_at,
                updated_at,
            ) in rows:

                cursor_v2.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,),
                )
                user = cursor_v2.fetchone()

                if not user:
                    print(f"User not found in v2: old_user_id {old_user_id}")
                    continue

                new_user_id = user[0]

                cursor_v2.execute(
                    "SELECT 1 FROM lawyers WHERE user_id = %s",
                    (new_user_id,),
                )

                if cursor_v2.fetchone():
                    print(f"Lawyer already exists for user_id {new_user_id}")
                    continue

                cursor_v2.execute(
                    """
                    INSERT INTO lawyers (
                        user_id,
                        oab,
                        oab_state_id,
                        is_payer_user,
                        approved_at,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        new_user_id,
                        crm,
                        crm_uf,
                        payer_user,
                        approved_at,
                        created_at,
                        updated_at,
                    ),
                )

                lawyer_id = cursor_v2.fetchone()[0]
                print(
                    f"Lawyer migrated successfully: old_user_id {old_user_id} -> new_user_id {new_user_id} -> ID: {lawyer_id}"
                )

        conn_v2.commit()
