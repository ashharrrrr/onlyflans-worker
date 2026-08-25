from pydantic import BaseModel


class StorageLocation(BaseModel):
    uri: str


class TranscodeJob(BaseModel):
    id: str
    input: StorageLocation
    output: StorageLocation
