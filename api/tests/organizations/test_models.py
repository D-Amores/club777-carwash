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
    organization = Organization(name="Empresa Temporal de Prueba")
    db_session.add(organization)
    db_session.flush()
    created_id = organization.id

    db_session.rollback()

    result = db_session.execute(
        select(Organization).where(Organization.id == created_id)
    ).scalar_one_or_none()

    assert result is None
