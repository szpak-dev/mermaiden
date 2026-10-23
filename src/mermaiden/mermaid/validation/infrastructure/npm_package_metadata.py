from pydantic import BaseModel, ConfigDict


class NpmPackageMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    name: str
    version: str
