from uuid import UUID

from sqlalchemy import select

from club777_api.organizations.models import Organization


def test_create_organization_with_defaults(db_session):
    organization = Organization(name="Club 777 Car Wash")

    db_session.add(organization)
    db_session.flush()

    assert isinstance(organization.id, UUID)
    assert organization.id.version == 7
    assert organization.timezone == "America/Mexico_City"
    assert organization.currency == "MXN"
    assert organization.is_active is True


def test_rollback_leaves_no_trace(db_session):
    result = db_session.execute(select(Organization)).scalars().all()

    assert result == []
