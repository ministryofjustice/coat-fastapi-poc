from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "eu-west-2"

    athena_database: str = "cur_v2_database"
    athena_workgroup: str = "primary"

    app_env: str = "development"

    @property
    def athena_output_location(self) -> str:
        if self.app_env == "production":
            return "s3://coat-production-cur-v2-hourly/athena-results"
        return "s3://coat-development-athena-output-clickops/Unsaved"

    class Config:
        env_file = ".env"


settings = Settings()