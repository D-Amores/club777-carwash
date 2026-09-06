from club777_api.auth.security import hash_password
from club777_api.core.database import SessionLocal
from club777_api.organizations.models import Organization
from club777_api.users.models import User


def run() -> None:
    session = SessionLocal()
    try:
        organization = (
            session.query(Organization)
            .filter(Organization.name == "Club 777 Car Wash")
            .one_or_none()
        )
        if organization is None:
            organization = Organization(name="Club 777 Car Wash")
            session.add(organization)
            session.flush()
            print(f"Organización creada: {organization.id}")
        else:
            print(f"Organización ya existía: {organization.id}")

        admin = (
            session.query(User)
            .filter(User.org_id == organization.id, User.email == "admin@club777.com")
            .one_or_none()
        )
        if admin is None:
            admin = User(
                org_id=organization.id,
                email="admin@club777.com",
                password_hash=hash_password("changeme123"),
                full_name="Administrador Club777",
                role="admin",
            )
            session.add(admin)
            print("Usuario admin creado (contraseña temporal: changeme123)")
        else:
            print("Usuario admin ya existía")

        session.commit()
        print(f"\nDEFAULT_ORG_ID={organization.id}")
    finally:
        session.close()


if __name__ == "__main__":
    run()
