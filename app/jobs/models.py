from pydantic import BaseModel


class StorageLocation(BaseModel):
    path: str


class TranscodeJob(BaseModel):
    id: str
    input: StorageLocation
    output: StorageLocation
