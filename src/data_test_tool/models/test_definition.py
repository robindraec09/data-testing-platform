from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, root_validator, validator, model_validator


class SourceConfig(BaseModel):
    type: str
    connection: str | None = None
    table: str | None = None
    query: str | None = None
    path: str | None = None
    format: str | None = None
    url: str | None = None
    method: str | None = None
    headers: dict[str, str] | None = None
    params: dict[str, Any] | None = None
    body: Any | None = None
    timeout: int | None = None


class RuleDefinition(BaseModel):
    name: str | None = None
    type: str | None = None
    column: str | None = None
    min: float | int | None = None
    max: float | int | None = None
    pattern: str | None = None
    schema: str | None = None
    file: str | None = None
    response_code: int | None = None
    max_response_time: str | None = None
    sql: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

    @validator("type", pre=True, always=True)
    def normalize_type(cls, value, values):
        if value is None and values.get("name"):
            return values["name"]
        return value

    @root_validator(pre=True)
    def extract_extra(cls, values):
        known_keys = {"name", "type", "column", "min", "max", "pattern", "schema", "file", "response_code", "max_response_time", "sql"}
        extra = {k: v for k, v in values.items() if k not in known_keys}
        values["extra"] = extra
        return values


class TestDefinition(BaseModel):
    name: str
    type: str
    source: SourceConfig
    target: SourceConfig | None = None
    rules: list[dict[str, Any]]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @validator("type")
    def lowercase_type(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode="after")
    def validate_rules(self):
        if not isinstance(self.rules, list):
            raise ValueError("rules must be a list")
        if self.type in {"etl", "etl_pipeline", "pipeline"} and self.target is None:
            raise ValueError("ETL tests require a target source definition")
        return self
