from typing import Dict, Optional, TypedDict, List

from pydantic import Field, BaseModel, AnyUrl


class BotConfig(TypedDict):
    client_id: str
    token: str
    client_secret: str


# priority: alias > origin
class Config(BaseModel):
    """
    Kaiheila 配置类

    :配置项:

      - ``client_id`` : Kaiheila 开发者中心获得
      - ``token`` : Kaiheila 开发者中心获得
      - ``client_secret`` : Kaiheila 开发者中心获得
    """
    bots: List[BotConfig] = Field(default_factory=list)

    class Config:
        extra = "ignore"
        allow_population_by_field_name = True
