from typing import Dict, List, Union, Optional, Type
from typing_extensions import Literal

from pydantic import BaseModel, Field, validator
from nonebot.typing import overrides
from nonebot.adapters import Event as BaseEvent, Message


class Role(BaseModel):
    role_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    color: Optional[int] = Field(None)
    position: Optional[int] = Field(None)
    hoist: Optional[int] = Field(None)
    mentionable: Optional[int] = Field(None)
    permissions: Optional[int] = Field(None)


class Channel(BaseModel):
    id_: Optional[str] = Field(None, alias="id")
    name: Optional[str] = Field(None)
    user_id: Optional[str] = Field(None)
    guild_id: Optional[str] = Field(None)
    topic: Optional[str] = Field(None)
    is_category: Optional[bool] = Field(None)
    parent_id: Optional[str] = Field(None)
    level: Optional[int] = Field(None)
    slow_mode: Optional[int] = Field(None)
    type: Optional[int] = Field(None)
    permission_overwrites: Optional[List[Dict]] = Field(None)
    permission_users: Optional[List[Dict[str, Union["User", int]]]] = Field(None)
    master_id: Optional[str] = Field(None)
    permission_sync: Optional[int] = Field(None)
    limit_amount: Optional[int] = Field(None)


class User(BaseModel):
    """
    https://developer.kaiheila.cn/doc/objects
    """
    id_: Optional[str] = Field(None, alias="id")
    username: Optional[str] = Field(None)
    nickname: Optional[str] = Field(None)
    identify_num: Optional[str] = Field(None)
    online: Optional[bool] = Field(None)
    bot: Optional[bool] = Field(None)
    os: Optional[str] = Field(None)
    status: Optional[int] = Field(None)
    avatar: Optional[str] = Field(None)
    vip_avatar: Optional[str] = Field(None)
    mobile_verified: Optional[bool] = Field(None)
    roles: Optional[List[int]] = Field(None)
    joined_at: Optional[int] = Field(None)
    active_time: Optional[int] = Field(None)


class Guild(BaseModel):
    id_: Optional[str] = Field(None, alias="id")
    name: Optional[str] = Field(None)
    topic: Optional[str] = Field(None)
    master_id: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    notify_type: Optional[int] = Field(None)  # 通知类型, 0代表默认使用服务器通知设置，1代表接收所有通知, 2代表仅@被提及，3代表不接收通知
    region: Optional[str] = Field(None)
    enable_open: Optional[bool] = Field(None)
    open_id: Optional[str] = Field(None)
    default_channel_id: Optional[str] = Field(None)
    welcome_channel_id: Optional[str] = Field(None)
    roles: Optional[List[Role]] = Field(None)
    channels: Optional[List[Channel]] = Field(None)


class Emoji(BaseModel):
    id_: str = Field(alias="id")
    name: str


class Attachment(BaseModel):
    type_: Optional[int] = Field(None, alias="type")
    url: str
    name: str
    file_type: Optional[str] = Field(None)
    size: Optional[int] = Field(None)
    duration: Optional[float] = Field(None)
    width: Optional[int] = Field(None)
    height: Optional[int] = Field(None)


class Body(BaseModel):
    msg_id: str
    user_id: str
    author_id: str
    target_id: str
    channel_id: str
    emoji: Optional[Emoji] = None
    content: Optional[str] = None
    updated_at: int
    chat_code: str

    class Config:
        extra = "allow"


class Extra(BaseModel):
    type_: Optional[int] = Field(None, alias="type")
    guild_id: Optional[str] = Field(None)
    channel_name: Optional[str] = Field(None)
    mention: Optional[List[str]] = Field(None)
    mention_all: Optional[bool] = Field(None)
    mention_roles: Optional[List[str]] = Field(None)
    mention_here: Optional[bool] = Field(None)
    author: Optional[User] = Field(None)
    body: Optional[Body] = Field(None)
    attachments: Optional[Attachment] = Field(None)
    code: Optional[str] = Field(None)

    @validator("body")
    def check_body(cls, v, values):
        if values["type_"] != 255 and v:  # 非系统消息 没有body
            raise ValueError("非系统消息不应该有body字段")
        return v


class Event(BaseEvent):
    """
    事件主要格式 來自 d字段
    Kaiheila 协议事件，字段与 Kaiheila 一致。各事件字段参考 `Kaiheila 文档`

    .. Kaiheila 文档:
        https://developer.kaiheila.cn/doc/event/event-introduction
    """
    __event__ = ""
    channel_type: Literal["PERSON", "GROUP"]
    type_: int = Field(alias="type")  # 1:文字消息, 2:图片消息，3:视频消息，4:文件消息， 8:音频消息，9:KMarkdown，10:card消息，255:系统消息, 其它的暂未开放
    target_id: str
    author_id: str
    content: str
    msg_id: str
    msg_timestamp: int
    nonce: str
    extra: Extra
    verify_token: Optional[str] = Field(None)

    post_type: str  # onebot兼容 message notice
    self_id: str  # onebot兼容

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return str(self.type_)

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return str(self.dict())

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


class NoticeEvent(Event):
    __event__ = "notice"
    post_type: Literal["notice"] = "notice"
    notice_type: str  # channel 之类的
    sub_type: str  # added_reaction详细的

    @overrides(Event)
    def get_type(self) -> str:
        return self.post_type

    @overrides(Event)
    def get_event_name(self) -> str:
        sub_type = getattr(self, "sub_type", None)
        return f"{self.post_type}.{self.notice_type}" + (f".{sub_type}"
                                                         if sub_type else "")

    @overrides(Event)
    def get_user_id(self) -> str:
        return self.extra.body.user_id

    @overrides(Event)
    def get_session_id(self) -> str:
        return self.extra.body.user_id


# 频道相关事件
class ChannelEvent(NoticeEvent):
    """
    频道相关事件
    """
    __event__ = "notice.channel"
    notice_type: Literal["channel"] = "channel"


class AddedReactionEvent(ChannelEvent):
    """
    频道内用户添加 reaction
    """
    __event__ = "notice.channel.added_reaction"
    sub_type: Literal["added_reaction"] = "added_reaction"

    # channel_id: Optional[str] = Field(None)  # 从extra抄出来 方便使用 todo msg_id 里面外面都有
    # user_id: Optional[str] = Field(None)
    # msg_id: Optional[str] = Field(None)
    # emoji: Optional[Emoji] = Field(None)
    #
    # @validator("channel_id")
    # def check_channel_id(cls, v, values):
    #     if v is None:
    #         v = values["extra"].body.channel_id
    #     return v
    #
    # @validator("user_id")
    # def check_user_id(cls, v, values):
    #     if v is None:
    #         v = values["extra"].body.user_id
    #     return v
    #
    # @validator("msg_id")
    # def check_msg_id(cls, v, values):
    #     if v is None:
    #         v = values["extra"].body.msg_id
    #     return v
    #
    # @validator("emoji")
    # def check_msg_id(cls, v, values):
    #     if v is None:
    #         v = values["extra"].body.emoji
    #     return v


class DeletedReactionEvent(ChannelEvent):
    """
    频道内用户取消 reaction
    """
    __event__ = "notice.channel.deleted_reaction"
    sub_type: Literal["deleted_reaction"] = "deleted_reaction"


class UpdatedMessageEvent(ChannelEvent):
    """
    频道消息更新
    """
    __event__ = "notice.channel.updated_message"
    sub_type: Literal["updated_message"] = "updated_message"


class DeletedMessageEvent(ChannelEvent):
    """
    频道消息被删除
    """
    __event__ = "notice.channel.deleted_message"
    sub_type: Literal["deleted_message"] = "deleted_message"


class AddedChannelEvent(ChannelEvent):
    """
    新增频道
    """
    __event__ = "notice.channel.added_channel"
    sub_type: Literal["added_channel"] = "added_channel"


class UpdatedChannelEvent(ChannelEvent):
    """
    修改频道信息
    """
    __event__ = "notice.channel.updated_channel"
    sub_type: Literal["updated_channel"] = "updated_channel"


class DeletedChannelEvent(ChannelEvent):
    """
    删除频道
    """
    __event__ = "notice.channel.deleted_channel"
    sub_type: Literal["deleted_channel"] = "deleted_channel"


class PinnedMessageEvent(ChannelEvent):
    """
    新的频道置顶消息
    """
    __event__ = "notice.channel.pinned_message"
    sub_type: Literal["pinned_message"] = "pinned_message"


class UnpinnedMessageEvent(ChannelEvent):
    """
    取消频道置顶消息
    """
    __event__ = "notice.channel.unpinned_message"
    sub_type: Literal["unpinned_message"] = "unpinned_message"


# 私聊消息事件
class PrivateNoticeEvent(NoticeEvent):
    __event__ = "notice.private"
    notice_type = "private"

    @overrides(NoticeEvent)
    def get_user_id(self) -> str:
        return self.extra.body.author_id

    @overrides(NoticeEvent)
    def get_session_id(self) -> str:
        return self.extra.body.author_id


class UpdatedPrivateMessageEvent(PrivateNoticeEvent):
    """
    私聊消息更新
    """
    __event__ = "notice.private.updated_private_message"
    sub_type: Literal["updated_private_message"] = "updated_private_message"


class DeletedPrivateMessageEvent(PrivateNoticeEvent):
    """
    私聊消息被删除
    """
    __event__ = "notice.private.deleted_private_message"
    sub_type: Literal["deleted_private_message"] = "deleted_private_message"


class PrivateAddedReactionEvent(PrivateNoticeEvent):
    """
    私聊内用户添加 reaction
    """
    __event__ = "notice.private.private_added_reaction"
    sub_type: Literal["private_added_reaction"] = "private_added_reaction"


class PrivateDeletedReactionEvent(PrivateNoticeEvent):
    """
    私聊内用户取消 reaction
    """
    __event__ = "notice.private.private_deleted_reaction"
    sub_type: Literal["private_deleted_reaction"] = "private_deleted_reaction"


# 服务器成员相关事件
class ServerMemberEvent(NoticeEvent):
    """
    服务器成员相关事件
    """
    __event__ = "notice.server_member"
    notice_type: Literal["server_member"] = "server_member"


class JoinedGuildEvent(ServerMemberEvent):
    """
    新成员加入服务器
    """
    __event__ = "notice.server_member.joined_guild"
    sub_type: Literal["joined_guild"] = "joined_guild"


class ExitedGuildEvent(ServerMemberEvent):
    """
    服务器成员退出
    """
    __event__ = "notice.server_member.exited_guild"
    sub_type: Literal["exited_guild"] = "exited_guild"


class UpdatedGuildMemberEvent(ServerMemberEvent):
    """
    服务器成员信息更新
    """
    __event__ = "notice.server_member.updated_guild_member"
    sub_type: Literal["updated_guild_member"] = "updated_guild_member"


class GuildMemberOnlineEvent(ServerMemberEvent):
    """
    服务器成员上线
    """
    __event__ = "notice.server_member.guild_member_online"
    sub_type: Literal["guild_member_online"] = "guild_member_online"


class GuildMemberOfflineEvent(ServerMemberEvent):
    """
    服务器成员下线
    """
    __event__ = "notice.server_member.guild_member_offline"
    sub_type: Literal["guild_member_offline"] = "guild_member_offline"


# 服务器角色相关事件
class ServerRoleEvent(NoticeEvent):
    """
    服务器角色相关事件
    """
    __event__ = "notice.server_role"
    notice_type: Literal["server_role"] = "server_role"


class AddedRoleEvent(ServerRoleEvent):
    """
    服务器角色增加
    """
    __event__ = "notice.server_role.added_role"
    sub_type: Literal["added_role"] = "added_role"


class DeletedRoleEvent(ServerRoleEvent):
    """
    服务器角色删除
    """
    __event__ = "notice.server_role.deleted_role"
    sub_type: Literal["deleted_role"] = "deleted_role"


class UpdatedRoleEvent(ServerRoleEvent):
    """
    服务器角色更新
    """
    __event__ = "notice.server_role.updated_role"
    sub_type: Literal["updated_role"] = "updated_role"


# 服务器相关事件
class ServerEvent(NoticeEvent):
    """
    服务器相关事件
    """
    __event__ = "notice.server"
    notice_type: Literal["server"] = "server"


class UpdatedGuildEvent(ServerEvent):
    """
    服务器信息更新
    """
    __event__ = "notice.server.updated_guild"
    sub_type: Literal["updated_guild"] = "updated_guild"


class DeletedGuildEvent(ServerEvent):
    """
    服务器删除
    """
    __event__ = "notice.server.deleted_guild"
    sub_type: Literal["deleted_guild"] = "deleted_guild"


class AddedBlockListEvent(ServerEvent):
    """
    服务器封禁用户
    """
    __event__ = "notice.server.added_block_list"
    sub_type: Literal["added_block_list"] = "added_block_list"


class DeletedBlockListEvent(ServerEvent):
    """
    服务器取消封禁用户
    """
    __event__ = "notice.server.deleted_block_list"
    sub_type: Literal["deleted_block_list"] = "deleted_block_list"


# 消息相关事件列表
class MessageEvent(Event):
    """消息事件"""
    __event__ = "message"
    post_type: Literal["message"] = "message"
    message_type: str  # group private 其实是person
    sub_type: str

    @property
    def sender(self) -> User:
        return self.extra.author

    @overrides(Event)
    def get_type(self) -> str:
        return "message"

    @overrides(Event)
    def get_event_name(self) -> str:
        sub_type = getattr(self, "sub_type", None)
        return f"{self.post_type}.{self.message_type}" + (f".{sub_type}"
                                                          if sub_type else "")

    @overrides(Event)
    def get_session_id(self) -> str:
        return self.author_id

    @overrides(Event)
    def get_user_id(self) -> str:
        return self.author_id

    @overrides(Event)
    def get_message(self) -> Message:
        return self.content  # todo 要写

    @overrides(Event)
    def get_plaintext(self) -> str:
        return self.content.extract_plain_text()  # todo 要写


# 私聊消息
class PrivateMessageEvent(MessageEvent):
    """私聊消息"""
    __event__ = "message.private"
    message_type: Literal["private"] = "private"

    @overrides(MessageEvent)
    def is_tome(self) -> bool:
        return True


# 群
class GroupMessageEvent(MessageEvent):
    """
    频道消息 为了和onebot一致还是叫群消息
    消息相关事件列表
    """
    __event__ = "message.group"
    message_type: Literal["group"] = "group"

    @overrides(MessageEvent)
    def is_tome(self) -> bool:
        return bool(self.extra.mention and self.self_id in self.extra.mention)

    @overrides(Event)
    def get_event_description(self) -> str:
        return (f'Message {self.msg_id} from {self.author_id}@[频道:{self.target_id}] "'
                + f"{self.content}")

    @overrides(MessageEvent)
    def get_session_id(self) -> str:
        return f"channel_{self.target_id}_{self.author_id}"


def get_event_model(event_name) -> List[Type[Event]]:  # todo 改写了
    """
    :说明:

      根据事件名获取对应 ``Event Model`` 及 ``FallBack Event Model`` 列表

    :返回:

      - ``List[Type[Event]]``
    """
    pass
