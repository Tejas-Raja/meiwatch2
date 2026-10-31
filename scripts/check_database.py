from sqlalchemy import text

from meiwatch.database import engine


def main():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version()")
        )

        version = result.scalar_one()

        print("Database connection successful!")
        print(version)


if __name__ == "__main__":
    main()