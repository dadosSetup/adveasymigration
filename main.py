from migration.mappers.migrate_users import migrate_users
from migration.mappers.migrate_user_basic_info import migrate_basic_info


def main():
    # migrate_users()
    migrate_basic_info()


if __name__ == "__main__":
    main()
