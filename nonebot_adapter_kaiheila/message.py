import re
from io import BytesIO
from pathlib import Path
from base64 import b64encode
from typing import Type, Union, Tuple, Mapping, Iterable, Optional, BinaryIO

from nonebot.typing import overrides
from nonebot.adapters import Message as BaseMessage, MessageSegment as BaseMessageSegment

from .utils import log, escape, unescape, _b2s


class MessageSegment(BaseMessageSegment["Message"]):
    """
    Kaiheila 协议 MessageSegment 适配。具体方法参考协议消息段类型或源码。
    type=1
    data={"content":"xxx"}
    """
    type: int
    # https://developer.kaiheila.cn/doc/event/event-introduction
    types = {
        1: "文字消息", 2: "图片消息", 3: "视频消息", 4: "文件消息", 8: "音频消息", 9: "KMarkdown", 10: "card消息", 255: "系统消息"
    }

    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @overrides(BaseMessageSegment)
    def __str__(self) -> str:
        data = self.data.copy()
        return data.get("content")

    @overrides(BaseMessageSegment)
    def __add__(self, other) -> "Message":
        return Message(self) + (MessageSegment.text(other) if isinstance(
            other, str) else other)

    @overrides(BaseMessageSegment)
    def __radd__(self, other) -> "Message":
        return (MessageSegment.text(other)
                if isinstance(other, str) else Message(other)) + self

    @overrides(BaseMessageSegment)
    def is_text(self) -> bool:
        return self.type == 1

    @staticmethod
    def image(file: BinaryIO, **kwargs) -> "MessageSegment":
        """
        :param file:
        :param kwargs:
            target_id str
            content str
            quote str
            nonce str
            temp_target_id str

        :return:
        """
        return MessageSegment(2, ({"content": file}).update(kwargs))

    @staticmethod
    def text(text: str, **kwargs) -> "MessageSegment":
        """
        :param text:
        :param kwargs:
            target_id str
            content str
            quote str
            nonce str
            temp_target_id str

        :return:
        """
        return MessageSegment(1, ({"content": text}).update(kwargs))

    @staticmethod
    def video(file: BinaryIO, **kwargs) -> "MessageSegment":
        """
        :param file:
        :param kwargs:
            target_id str
            content str
            quote str
            nonce str
            temp_target_id str

        :return:
        """
        return MessageSegment(3, ({"content": file}).update(kwargs))

    @staticmethod
    def file(file: BinaryIO, **kwargs) -> "MessageSegment":
        """
        :param file:
        :param kwargs:
            target_id str
            content str
            quote str
            nonce str
            temp_target_id str

        :return:
        """
        return MessageSegment(4, ({"content": file}).update(kwargs))

    @staticmethod
    def audio(file: BinaryIO, **kwargs) -> "MessageSegment":
        """
        :param file:
        :param kwargs:
            target_id str
            content str
            quote str
            nonce str
            temp_target_id str

        :return:
        """
        return MessageSegment(8, ({"content": file}).update(kwargs))

    @staticmethod
    def kmarkdown(text: str, **kwargs) -> "MessageSegment":
        """
        :param file:
        :param kwargs:
            target_id str
            content str
            quote str
            nonce str
            temp_target_id str

        :return:
        """
        return MessageSegment(9, ({"content":text}).update(kwargs))


class Message(BaseMessage[MessageSegment]):
    """
    Kaiheila 协议 Message 适配。
    """

    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @overrides(BaseMessage)
    def __add__(self, other: Union[str, Mapping,
                                   Iterable[Mapping]]) -> "Message":
        return super(Message, self).__add__(
            MessageSegment.text(other) if isinstance(other, str) else other)

    @overrides(BaseMessage)
    def __radd__(self, other: Union[str, Mapping,
                                    Iterable[Mapping]]) -> "Message":
        return super(Message, self).__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other)

    @staticmethod
    @overrides(BaseMessage)
    def _construct(
            msg: Union[str, Mapping,
                       Iterable[Mapping]]) -> Iterable[MessageSegment]:
        if isinstance(msg, Mapping):
            yield MessageSegment(msg["type"], msg.get("data") or {})
            return
        elif isinstance(msg, Iterable) and not isinstance(msg, str):
            for seg in msg:
                yield MessageSegment(seg["type"], seg.get("data") or {})
            return
        elif isinstance(msg, str):

            def _iter_message(msg: str) -> Iterable[Tuple[str, str]]:
                text_begin = 0
                for cqcode in re.finditer(
                        r"\[CQ:(?P<type>[a-zA-Z0-9-_.]+)"
                        r"(?P<params>"
                        r"(?:,[a-zA-Z0-9-_.]+=[^,\]]+)*"
                        r"),?\]", msg):
                    yield "text", msg[text_begin:cqcode.pos + cqcode.start()]
                    text_begin = cqcode.pos + cqcode.end()
                    yield cqcode.group("type"), cqcode.group("params").lstrip(
                        ",")
                yield "text", msg[text_begin:]

            for type_, data in _iter_message(msg):
                if type_ == "text":
                    if data:
                        # only yield non-empty text segment
                        yield MessageSegment(type_, {"text": unescape(data)})
                else:
                    data = {
                        k: unescape(v) for k, v in map(
                            lambda x: x.split("=", maxsplit=1),
                            filter(lambda x: x, (
                                x.lstrip() for x in data.split(","))))
                    }
                    yield MessageSegment(type_, data)

    @overrides(BaseMessage)
    def extract_plain_text(self) -> str:
        return "".join(seg.data["text"] for seg in self if seg.is_text())
