import copy
from exception import InvalidMessage


class InternalMessageContent:
    """
    Internal message content
    """

    CONTENT_TYPE_PEER_CONNECTED = "PEER_CONNECTED"
    CONTENT_TYPE_PEER_DISCONNECTED = "PEER_DISCONNECTED"
    CONTENT_TYPE_MESSAGE_RESPONSE = "MESSAGE_RESPONSE"

    def __init__(self, content_type, peer_infos, data=None):
        """
        Constructor

        Args:
            content_type (string): content type (CONTENT_TYPE_XXX)
            peer_infos (PeerInfos): peer informations
            data (any): data depends on content type
        """
        self.content_type = content_type
        self.peer_infos = peer_infos
        self.data = data

    def __str__(self):
        string = f"InternalMessageContent: ${self.content_type} - ${self.peer_infos} - ${self.data}"
        return string

    def to_dict(self):
        output = {
            "content_type": self.content_type,
            "peer_infos": self.peer_infos.to_dict(),
        }
        if self.data:
            output["data"] = self.data.to_dict()

        return output


class InternalMessage:
    """
    Handle internal message to process it according to type
    """

    MESSAGE_TYPE_TOELECTRON = "TO_ELECTRON"
    MESSAGE_TYPE_FROMELECTRON = "FROM_ELECTRON"

    def __init__(self, message_type, content):
        """
        Constructor

        Args:
            message_type (str): message type (MESSAGE_TYPE_XXX)
            content (InternalMessageContent): message content
        """
        self.message_type = message_type
        self.content = content

    def __str__(self):
        return "InternalMessage: " + self.message_type + " " + str(self.content)


class PeerInfos:
    """
    Stores peer informations
    """

    def __init__(
        self,
        uuid=None,
        ident=None,
        hostname=None,
        ip=None,
        port=80,
        ssl=False,
        auth=False,
        macs=None,
        cleepdesktop=False,
        extra=None,
    ):
        """
        Constructor

        Args:
            uuid (string): peer uuid provided by cleep
            ident (string): peer identifier provided by external bus
            hostname (string): peer hostname
            ip (string): peer ip
            port (int): peer access port
            ssl (bool): peer has ssl enabled
            auth (bool): peer has auth enabled
            macs (list): list of macs addresses
            cleepdesktop (bool): is cleepdesktop peer
            extra (dict): extra peer informations (about hardware...)

        Note:
            Uuid is mandatory because device can change identifier after each connection.

            Id is the identifier provided by your external bus implementation.

            Hostname is mandatory because it is used to display user friendly peer name

            Mac addresses are mandatory because they are used to identify a peer that has been reinstalled (and
            has lost its previous uuid)
        """
        self.uuid = uuid
        self.ident = ident
        self.hostname = hostname
        self.ip = ip
        self.port = port
        self.ssl = ssl
        self.auth = auth
        self.macs = macs
        self.cleepdesktop = cleepdesktop
        self.online = False
        self.extra = extra or {}

    def to_dict(self, with_extra=False):
        """
        Return peer infos as dict

        Args:
            with_extra (bool): add extra data

        Returns:
            dict: peer infos
        """
        out = {
            "uuid": self.uuid,
            "ident": self.ident,
            "hostname": self.hostname,
            "ip": self.ip,
            "port": self.port,
            "ssl": self.ssl,
            "auth": self.auth,
            "macs": self.macs,
            "cleepdesktop": self.cleepdesktop,
            "online": self.online,
            "extra": self.extra,
        }
        if with_extra:
            out.update({"extra": self.extra})
        return out

    def __str__(self):
        """
        To string method

        Returns:
            string: peer infos as string
        """
        return (
            "PeerInfos(uuid:%s, ident:%s, hostname:%s, ip:%s port:%s, ssl:%s, auth:%s, macs:%s, cleepdesktop:%s, online:%s, extra:%s)"
            % (
                self.uuid,
                self.ident,
                self.hostname,
                self.ip,
                self.port,
                self.ssl,
                self.auth,
                self.macs,
                self.cleepdesktop,
                self.online,
                self.extra,
            )
        )

    def fill_from_dict(self, peer_infos):
        """
        Fill infos from dict

        Args:
            peer_infos (dict): peer informations
        """
        if not isinstance(peer_infos, dict):
            raise Exception('Parameter "peer_infos" must be a dict')
        self.uuid = peer_infos.get("uuid", None)
        self.ident = peer_infos.get("ident", None)
        self.hostname = peer_infos.get("hostname", None)
        self.ip = peer_infos.get("ip", None)
        self.port = peer_infos.get("port", None)
        self.ssl = peer_infos.get("ssl", False)
        self.auth = peer_infos.get("auth", False)
        self.macs = peer_infos.get("macs", None)
        self.cleepdesktop = peer_infos.get("cleepdesktop", False)
        self.extra = copy.deepcopy(peer_infos.get("extra", {}))


class MessageResponse:
    """
    Object that holds message response

    A response is composed of:

        * an error flag: True if error, False otherwise
        * a message: a message about request
        * some data: data returned by the request

    """

    def __init__(self, error=False, message="", data=None, broadcast=False):
        """
        Constructor

        Args:
            error (bool): error flag (default False)
            message (string): response message (default empty string)
            data (any): response data (default None)
            broadcast (bool): response comes from broadcast (default False)
        """
        self.error = error
        self.message = message
        self.data = data
        self.broadcast = broadcast

    def __str__(self):
        """
        Stringify
        """
        return 'MessageResponse(error:%r, message:"%s", data:%s, broadcast:%r)' % (
            self.error,
            self.message,
            str(self.data),
            self.broadcast,
        )

    def to_dict(self):
        """
        Return message response
        """
        return {"error": self.error, "message": self.message, "data": self.data}

    def fill_from_response(self, response):
        """
        Fill from other response

        Args:
            response (MessageResponse): message response instance
        """
        if not isinstance(response, MessageResponse):
            raise Exception('Parameter "response" must be a MessageResponse instance')

        self.error = response.error
        self.message = response.message
        self.data = copy.deepcopy(response.data)
        self.broadcast = response.broadcast

    def fill_from_dict(self, response):
        """
        Fill from dict

        Args:
            response (dict): response as dict
        """
        if not isinstance(response, dict):
            raise Exception('Parameter "response" must be a dict')

        self.error = response.get("error", False)
        self.broadcast = response.get("broadcast", False)
        self.message = response.get("message", "")
        self.data = response.get("data", None)


class MessageRequest:
    """
    Object that holds message request

    A message request is composed of:

        * in case of a command:

            * a command name
            * command parameters
            * the command sender

        * in case of an event:

            * an event name
            * event parameters
            * propagate flag to say if event can be propagated out of the device
            * a device id
            * a startup flag that indicates this event was sent during cleep startup

    Attribute peer_infos is filled when message comes from oustide. This field must also be filled when
    message is intented to be sent to outside.

    Members:
        command (string): command name
        event (string): event name
        propagate (bool): True if event can be propagated out of the device [event only]
        params (dict): list of event or command parameters
        to (string): message module recipient
        sender (string): message sender [command only]
        device_id (string): internal virtual device identifier [event only]
        peer_infos (PeerInfos): peer informations. Must be filled if message comes from outside the device

    Note:
        A message cannot be a command and an event, priority to command if both are specified.
    """

    def __init__(self, command=None, event=None, params=None, to=None):
        """
        Constructor

        Args:
            command (string): request command
            event (string): request event
            params (dict): message parameter if any
            to (string): message recipient if any
        """
        self.command = command
        self.event = event
        self.params = params or {}
        self.to = to
        self.propagate = False
        self.sender = None
        self.device_id = None
        self.peer_infos = None
        self.command_uuid = None
        self.timeout = None

    def __str__(self):
        """
        Stringify function
        """
        if self.command:
            msg = (
                "MessageRequest(command:%s, params:%s, to:%s, sender:%s, device_id:%s, peer_infos:%s, command_uuid:%s, timeout:%s"
                % (
                    self.command,
                    str(self.params),
                    self.to,
                    self.sender,
                    self.device_id,
                    self.peer_infos.to_dict() if self.peer_infos else None,
                    self.command_uuid,
                    self.timeout,
                )
            )
            return msg

        if self.event:
            msg = (
                "MessageRequest(event:%s, propagate:%s, params:%s, to:%s, device_id:%s, peer_infos:%s, command_uuid:%s)"
                % (
                    self.event,
                    self.propagate,
                    str(self.params),
                    self.to,
                    self.device_id,
                    self.peer_infos.to_dict() if self.peer_infos else None,
                    self.command_uuid,
                )
            )
            return msg

        return "MessageRequest(Invalid message)"

    def is_broadcast(self):
        """
        Return broadcast status

        Returns:
            bool: True if the request is broadcast
        """
        return self.to is None

    def is_command(self):
        """
        Return true if message is a command. If not it is an event

        Returns:
            bool: True if message is a command, otherwise it is an event
        """
        return bool(self.command)

    def is_external_event(self):
        """
        Return True if event comes from external device

        Returns:
            bool: True if event comes from external device
        """
        return self.peer_infos is not None

    def to_dict(self, startup=False, external_sender=None):
        """
        Convert message request to dict object

        Params:
            startup (bool): True if the message is startup message
            external_sender (string): specify module name that handles message from external bus

        Raise:
            InvalidMessage if message is not valid
        """
        if self.command and not self.peer_infos:
            # internal command
            return {
                "command": self.command,
                "params": self.params,
                "to": self.to,
                "sender": self.sender,
                "broadcast": self.is_broadcast(),
            }

        if self.event and not self.peer_infos:
            # internal event
            return {
                "event": self.event,
                "to": self.to,
                "params": self.params,
                "startup": startup,
                "device_id": self.device_id,
                "sender": self.sender,
            }

        if self.command and self.peer_infos:
            # external command
            return {
                "command": self.command,
                "params": self.params,
                "to": self.to,
                "sender": external_sender or self.sender,
                "broadcast": self.is_broadcast(),
                "peer_infos": self.peer_infos.to_dict(),
                "command_uuid": self.command_uuid,
                "timeout": self.timeout,
            }

        if self.event and self.peer_infos:
            # external event
            return {
                "event": self.event,
                "params": self.params,
                "startup": False,
                "device_id": None,
                "sender": external_sender or self.sender,
                "peer_infos": self.peer_infos.to_dict(),
                "command_uuid": self.command_uuid,
            }

        raise InvalidMessage()

    def fill_from_request(self, request):
        """
        Fill instance from other request

        Args:
            request (MessageRequest): message request instance
        """
        if not isinstance(request, MessageRequest):
            raise Exception('Parameter "request" must be a MessageRequest instance')

        self.command = request.command
        self.event = request.event
        self.propagate = request.propagate
        self.params = copy.deepcopy(request.params)
        self.to = request.to
        self.sender = request.sender
        self.device_id = request.device_id
        self.peer_infos = None
        self.command_uuid = request.command_uuid
        if request.peer_infos:
            self.peer_infos = PeerInfos()
            self.peer_infos.fill_from_dict(request.peer_infos.to_dict(True))

    def fill_from_dict(self, message):
        """
        Fill instance from other request

        Args:
            request (dict): message request infos
        """
        if not isinstance(message, dict):
            raise Exception('Parameter "message" must be a dict')

        self.command = message.get("command", None)
        self.event = message.get("event", None)
        self.propagate = message.get("propagate", False)
        self.params = copy.deepcopy(message.get("params", {}))
        self.to = message.get("to", None)
        self.sender = message.get("sender", None)
        self.device_id = message.get("device_id", None)
        self.command_uuid = message.get("command_uuid", None)
        self.timeout = message.get("timeout", 5.0)
        self.peer_infos = None
        if message.get("peer_infos", None):
            self.peer_infos = PeerInfos()
            self.peer_infos.fill_from_dict(message.get("peer_infos"))
