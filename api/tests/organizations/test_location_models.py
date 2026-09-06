from uuid import UUID

from club777_api.organizations.models import Location, Organization


def test_create_location_with_defaults(db_session):
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()

    location = Location(org_id=organization.id, name="Plaza Bella")
    db_session.add(location)
    db_session.flush()

    assert isinstance(location.id, UUID)
    assert location.id.version == 7
    assert location.org_id == organization.id
    assert location.address is None
    assert location.phone is None
    assert location.timezone is None
    assert location.is_active is True
