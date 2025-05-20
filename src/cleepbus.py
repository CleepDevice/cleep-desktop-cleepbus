import json
import time
import logging
import platform
import uuid
from pyrebus import PyreBus
from common import (
    InternalMessageContent,
    MessageRequest,
    PeerInfos,
    InternalMessage,
    str2bool,
)
from version import VERSION


class CleepBus:
    """
    CleepBus class to handle message from Cleep mesh network
    """

    UNCONFIGURED_DEVICE_HOSTNAME = "cleepdevice"

    def __init__(self, message_queue, config):
        """
        Args:
            message_queue (Queue): message queue instance
            config (dict): app configuration
        """
        debug = config.get("debug", False)
        self.logger = logging.getLogger(self.__class__.__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.message_queue = message_queue
        self.uuid = config.get("uuid") or str(uuid.uuid4())
        self.peers = {}

        self.pyrebus = PyreBus(
            self.__on_message_received,
            self.__on_peer_connected,
            self.__on_peer_disconnected,
            self.__decode_peer_infos,
            debug,
            None,
        )

    def start(self):
        """
        Start bus
        """
        infos = self.get_cleepbus_headers()
        self.pyrebus.start(infos)

    def stop(self):
        """
        Stop bus
        """
        if self.pyrebus:
            self.pyrebus.stop()

    def read_messages(self):
        """
        Read message from bus and returns
        """
        self.pyrebus.run_once()

    def send_message(self, message):
        """
        Send message to bus

        Args:
            message (dict): message data to send
        """
        msg = MessageRequest()
        msg.fill_from_dict(message)
        self.pyrebus.send_message(msg)

    def get_cleepbus_headers(self):
        """
        Headers to send at bus connection (values must be in string format!)

        Returns:
            dict: dict of headers (only string supported)
        """
        macs = self.pyrebus.get_mac_addresses()
        headers = {
            "uuid": self.uuid,
            "version": VERSION,
            "hostname": platform.node(),
            "port": "80",
            "macs": json.dumps(macs),
            "ssl": "0",
            "auth": "0",
            "cleepdesktop": "1",
            "apps": json.dumps({}),
        }
        self.logger.debug("headers: %s", headers)

        return headers

    def __on_message_received(self, peer_uuid, message):
        """
        Handle received message from external bus

        Args:
            peer_uuid (string): peer identifier
            message (MessageResponse): message from external bus
        """
        self.logger.debug("Message received from %s: %s", peer_uuid, message)
        content = InternalMessageContent(
            content_type=InternalMessageContent.CONTENT_TYPE_MESSAGE_RESPONSE,
            peer_infos=self.peers[peer_uuid],
            data=message,
        )
        msg = InternalMessage(
            message_type=InternalMessage.MESSAGE_TYPE_TOELECTRON,
            content=content,
        )
        self.message_queue.put(msg)

    def __on_peer_connected(self, peer_uuid, peer_infos):
        """
        Device is connected

        Args:
            peer_uuid (string): peer identifier
            peer_infos (PeerInfos): peer informations (ip, port, ssl...)
        """
        self.logger.info("Peer %s connected with %s", peer_uuid, peer_infos.to_dict())

        # drop other cleep-desktop connection
        if peer_infos.cleepdesktop:
            self.logger.debug("Drop other cleep-desktop connection")
            return

        # save new peer
        peer_infos.online = True
        peer_infos.extra["connectedat"] = int(time.time())
        peer_infos.extra["configured"] = False
        if (
            len(peer_infos.hostname.strip()) > 0
            and peer_infos.hostname != self.UNCONFIGURED_DEVICE_HOSTNAME
        ):
            peer_infos.extra["configured"] = True
        self.peers[peer_uuid] = peer_infos
        self.logger.debug("Peer %s connected: %s", peer_uuid, peer_infos)

        # queue message
        content = InternalMessageContent(
            content_type=InternalMessageContent.CONTENT_TYPE_PEER_CONNECTED,
            peer_infos=peer_infos,
        )
        msg = InternalMessage(
            message_type=InternalMessage.MESSAGE_TYPE_TOELECTRON,
            content=content,
        )
        self.message_queue.put(msg)

    def __on_peer_disconnected(self, peer_uuid):
        """
        Device is disconnected

        Args:
            peer_uuid (str): peer identifier
        """
        self.logger.info("Peer %s disconnected", peer_uuid)

        # update peer
        peer_infos = self.peers.get(peer_uuid)
        if peer_infos:
            peer_infos.online = False

        # queue message
        content = InternalMessageContent(
            content_type=InternalMessageContent.CONTENT_TYPE_PEER_DISCONNECTED,
            peer_infos=peer_infos,
        )
        msg = InternalMessage(
            message_type=InternalMessage.MESSAGE_TYPE_TOELECTRON,
            content=content,
        )
        self.message_queue.put(msg)

    def __decode_peer_infos(self, infos):
        """
        Decode peer infos

        It is used to transform peer connection infos to appropriate python type (all values in
        infos are string).

        Args:
            infos (dict): dict of decoded values

        Returns:
            PeerInfos: peer informations
        """
        self.logger.debug("Raw value to decode: %s", infos)
        peer_infos = PeerInfos()
        peer_infos.uuid = infos.get("uuid", None)
        peer_infos.hostname = infos.get("hostname", None)
        peer_infos.port = int(infos.get("port", peer_infos.port))
        peer_infos.ssl = bool(str2bool(infos.get("ssl", f"{peer_infos.ssl}")))
        peer_infos.auth = bool(str2bool(infos.get("auth", f"{peer_infos.auth}")))
        peer_infos.cleepdesktop = bool(
            str2bool(infos.get("cleepdesktop", f"{peer_infos.cleepdesktop}"))
        )
        peer_infos.macs = json.loads(infos.get("macs", "[]"))
        peer_infos.extra = {
            key: self.decode_header_value(key, value)
            for key, value in infos.items()
            if key not in ["uuid", "hostname", "port", "ssl", "cleepdesktop", "macs"]
        }

        return peer_infos

    @staticmethod
    def decode_header_value(key, value):
        """
        Json decode value from header

        Args:
            key (string): header keys
            value (string): header value to decode

        Returns:
            decoded value
        """
        # handle legacy apps header value
        if key == "apps" and not value.startswith("["):
            value = json.dumps(value.split(","))

        # decode value
        try:
            return json.loads(value)
        except Exception:
            return value
