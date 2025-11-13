from enum import Enum
import logging
import os
from pathlib import Path

from dynaconf import Dynaconf, ValidationError, Validator

APPLICATION_ENV = "APPLICATION_ENV"

logger = logging.getLogger(__name__)


class Environments(Enum):
    # Do not change this enum before understanding whole file
    TESTING_INTEGRATION = 1
    TESTING = 2
    LOCAL = 3
    DEVELOP = 4
    STAGING = 5
    PRODUCTION = 6


application_env = os.getenv(APPLICATION_ENV)
try:
    environment = Environments[str(application_env).upper()]
except (KeyError, AttributeError) as exc:
    raise ValidationError(
        f"{APPLICATION_ENV} must be one of {[e.name for e in Environments]},"
        + f" but it is '{application_env}'"
    ) from exc

validators = [
    Validator("DEBUG", default=False),
    Validator("HOST", default="127.0.0.1"),
    Validator("PORT", default=8000),
    Validator("SITE_URL", default=""),
    Validator("SITE_NAME", default=""),
    Validator("OPENROUTER.BASE_URL", default="https://openrouter.ai/api/v1"),
    Validator("ASSISTANT.ALLOWED_MODELS", is_type_of=list, must_exist=True),
    Validator("ASSISTANT.DEFAULT_MODEL", is_type_of=str, must_exist=True),
]

if environment not in [Environments.TESTING, Environments.TESTING_INTEGRATION]:
    validators.extend(
        [
            Validator("OPEN_ROUTER_API_KEY", is_type_of=str, must_exist=True),
        ]
    )



settings = Dynaconf(
    validators=validators,
    post_hooks=[],
    envvar_prefix=False,
    settings_files=[
        Path(__file__).parents[0] / v
        for v in ("settings.toml", ".secrets.toml")
    ],
    environments=True,
    load_dotenv=True,
    env_switcher="APPLICATION_ENV",
)
