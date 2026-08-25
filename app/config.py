from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    queue_backend: str = "local"
    storage_backend: str = "local"

    s3_bucket: str = ""
    aws_region: str = "ap-south-1"

    sqs_queue_url: str = ""

    model_config = SettingsConfigDict(
        env_prefix="WORKER_", env_file=".env", extra="ignore"
    )


settings = Settings()
