"""
Kaiheila 协议适配
============================

协议详情请看: `Kaiheila`

.. Kaiheila:
    https://developer.kaiheila.cn/doc
"""

from .event import *
from .permission import *
from .message import Message, MessageSegment
from .utils import log, escape, unescape, _b2s
from .bot import Bot, _check_at_me, _check_nickname, _check_reply, _handle_api_result
from .exception import CQHTTPAdapterException, ApiNotAvailable, ActionFailed, NetworkError
