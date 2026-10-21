"""Admin tool for clinician accounts. There is no sign-up page on purpose: only an admin
with access to this machine can create or unlock an account.

Run from backend/ with the backend venv active:
    python -m scripts.clinicians add <username> "<Full Name>"   (asks for the password)
    python -m scripts.clinicians unlock <username>
"""
import argparse
import getpass
import sys

from app.db import models  # noqa: F401  (registers the tables on Base)
from app.db.session import Base, SessionLocal, engine
from app.repositories import clinician_repo
from app.services import auth_service


def add(db, username: str, name: str) -> None:
    if clinician_repo.get_by_username(db, username):
        sys.exit(f"{username} already exists.")
    password = getpass.getpass("Password: ")
    if len(password) < 8:
        sys.exit("Password must be at least 8 characters.")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords don't match.")
    clinician_repo.create(db, username, name, auth_service.hash_password(password))
    print(f"Created {username}.")


def unlock(db, username: str) -> None:
    clinician = clinician_repo.get_by_username(db, username)
    if clinician is None:
        sys.exit(f"No clinician called {username}.")
    clinician.failed_logins = 0
    clinician.locked = False
    clinician_repo.save(db, clinician)
    print(f"Unlocked {username}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    add_cmd = commands.add_parser("add", help="create a clinician account")
    add_cmd.add_argument("username")
    add_cmd.add_argument("name")
    unlock_cmd = commands.add_parser("unlock", help="reset a locked account")
    unlock_cmd.add_argument("username")
    args = parser.parse_args()

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if args.command == "add":
            add(db, args.username, args.name)
        else:
            unlock(db, args.username)


if __name__ == "__main__":
    main()