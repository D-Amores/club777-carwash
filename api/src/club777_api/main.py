from contextlib import asynccontextmanager

from fastapi import FastAPI

from club777_api.core.config import settings
from club777_api.core.database import SessionLocal
from club777_api.organizations.models import Organization


@asynccontextmanager
async def lifespan(app: FastAPI):
    session = SessionLocal()
    try:
        organization = session.get(Organization, settings.default_org_id)
        if organization is None:
            raise RuntimeError(
                f"DEFAULT_ORG_ID={settings.default_org_id} no existe en la base de datos."
            )
        if not organization.is_active:
            raise RuntimeError(
                f"DEFAULT_ORG_ID={settings.default_org_id} corresponde a una organización inactiva."
            )
    finally:
        session.close()

    yield


app = FastAPI(title="Club777 API", lifespan=lifespan)
