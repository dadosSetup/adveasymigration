from migration.mappers.migrate_users import migrate_users
from migration.mappers.migrate_user_basic_info import migrate_basic_info
from migration.mappers.migrate_doctors import migrate_lawyers


def main():
    migrate_users()
    migrate_basic_info()
    migrate_lawyers()


if __name__ == "__main__":
    main()
