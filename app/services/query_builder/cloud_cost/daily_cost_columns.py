
# Allowlist: query param name -> real SQL column name.
# This is the ONLY set of columns that can ever appear in SELECT/GROUP BY/WHERE.
DAILY_COST_DIMENSION_COLUMNS = {
    "account_name": "account_name",
    "region": "product_region_code",
    "environment": "environment",
    "business_unit": "business_unit",
    "application": "tag_application",
    "namespace": "tag_namespace",
    "service_area": "tag_service_area",
    "owner": "tag_owner",
    "product_name": "product_name",
}
