from datetime import date

from pydantic import BaseModel, model_validator


class DailyCostQueryParams(BaseModel):
    start_usage_date: date
    end_usage_date: date

    account_name: str | None = None
    region: str | None = None
    environment: str | None = None
    business_unit: str | None = None
    application: str | None = None
    namespace: str | None = None
    service_area: str | None = None
    owner: str | None = None
    product_name: str | None = None

    @model_validator(mode="after")
    def at_least_one_categorical_param(self) -> "DailyCostQueryParams":
        categorical_fields = [
            self.account_name,
            self.region,
            self.environment,
            self.business_unit,
            self.application,
            self.namespace,
            self.service_area,
            self.owner,
            self.product_name,
        ]
        if not any(categorical_fields):
            raise ValueError(
                "At least one categorical parameter is required: account_name, "
                "region, environment, business_unit, application, namespace, "
                "service_area, owner, product_name"
            )
        return self


class DailyCostRow(BaseModel):
    usage_date: str
    total_daily_cost: str

    account_name: str | None = None
    product_region_code: str | None = None
    environment: str | None = None
    business_unit: str | None = None
    tag_application: str | None = None
    tag_namespace: str | None = None
    tag_service_area: str | None = None
    tag_owner: str | None = None
    product_name: str | None = None


class DailyCostResponse(BaseModel):
    account_name: str | None = None
    results: list[DailyCostRow]
