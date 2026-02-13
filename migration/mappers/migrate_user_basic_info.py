from migration.db import connect
from enums.enums_v2 import userGender
from enums.enums_v1 import doctorsGender


def migrate_basic_info():
    with connect("v1") as conn_v1, connect("v2") as conn_v2:
        with conn_v1.cursor() as cur_v1, conn_v2.cursor() as cur_v2:

            cur_v1.execute(
                """
                SELECT
                    d.name,
                    d.cpf,
                    d.birthday,
                    d.gender,
                    d.cellphone,
                    d.deleted_at,
                    u.email
                FROM doctors d
                JOIN users u ON d.user_id = u.id
                JOIN doctor_subscriptions ds ON d.id = ds.doctor_id
                WHERE
                    d.account_stage IN (1, 2)
                    AND (
                        ds.canceled_at IS NULL
                        OR ds.canceled_at >= CURRENT_DATE - INTERVAL '30 days'
                    )
                    AND ds.started_at IS NOT NULL
            """
            )

            rows = cur_v1.fetchall()

            if not rows:
                print("Informations not found")
                return

            for name, cpf, birthday, gender_raw, cellphone, deleted_at, email in rows:

                cur_v2.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cur_v2.fetchone()

                if not user:
                    print(f"User not found in v2: {email}")
                    continue

                user_id = user[0]

                cur_v2.execute(
                    "SELECT 1 FROM user_basic_info WHERE user_id = %s", (user_id,)
                )
                if cur_v2.fetchone():
                    print(f"Basic info already exists: {cpf}")
                    continue

                gender_key = doctorsGender.get(gender_raw)
                gender_enum = userGender.get(
                    gender_key or "NOT_INFORMED", userGender["NOT_INFORMED"]
                )

                cur_v2.execute(
                    """
                    INSERT INTO user_basic_info
                        (user_id, name, cpf, birthday, gender, cellphone, deleted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, name, cpf, birthday, gender_enum, cellphone, deleted_at),
                )

                basic_info_id = cur_v2.fetchone()[0]
                print(f"Basic info migrated successfully: {cpf} -> ID {basic_info_id}")
