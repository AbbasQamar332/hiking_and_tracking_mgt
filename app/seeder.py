from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Permission, Role, User

PERMISSIONS = {
    "manage_users": "Create, update, and list users",
    "approve_events": "Approve hiking events",
  
    "create_event": "Create hiking events",
    "view_events": "View hiking events",
    "book_event": "Book hiking events",
    "write_review": "Submit reviews",
}

ROLE_PERMISSIONS = {
    "admin": list(PERMISSIONS.keys()),
    "owner": ["view_events", "create_event", "book_event", "write_review"],
    "visitor": ["view_events", "book_event", "write_review"],
}

DEFAULT_USERS = [
    {
        "email": "admin@example.com",
        "password": "Admin123!",
        "role": "admin",
    },
    {
        "email": "owner@example.com",
        "password": "Owner123!",
        "role": "owner",
    },
    {
        "email": "visitor@example.com",
        "password": "Visitor123!",
        "role": "visitor",
    },
]


def _get_or_create(session, model, defaults=None, **criteria):
    instance = session.query(model).filter_by(**criteria).first()
    if instance:
        return instance, False

    params = {**criteria, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    session.flush()
    return instance, True


def seed_permissions(session):
    created = 0
    for name, description in PERMISSIONS.items():
        permission, is_new = _get_or_create(
            session,
            Permission,
            defaults={"description": description},
            name=name,
        )
        if not is_new and permission.description != description:
            permission.description = description
        if is_new:
            created += 1
    if created:
        print(f"Created {created} permissions")
    return created


def seed_roles(session):
    created = 0
    for name, permission_names in ROLE_PERMISSIONS.items():
        role, is_new = _get_or_create(
            session,
            Role,
            defaults={"description": f"{name.capitalize()} role"},
            name=name,
        )
        if is_new:
            created += 1
        session.flush()
        role.permissions = []
        for permission_name in permission_names:
            permission = session.query(Permission).filter_by(name=permission_name).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    if created:
        print(f"Created {created} roles")
    return created


def seed_users(session):
    created = 0
    for user_data in DEFAULT_USERS:
        user = session.query(User).filter_by(email=user_data["email"]).first()
        if user:
            if user.role != user_data["role"]:
                user.role = user_data["role"]
            continue

        hashed_password = hash_password(user_data["password"])
        user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data["role"],
            is_verified=True,
        )
        session.add(user)
        created += 1

    if created:
        print(f"Created {created} default users")
    return created


def main():
    print("Creating tables and seeding roles, permissions, and default users...")
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_permissions(session)
        seed_roles(session)
        seed_users(session)
        session.commit()
        print("Seeding complete.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
