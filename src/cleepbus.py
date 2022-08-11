import json
import time
from distutils.util import strtobool
import logging
import platform
import uuid
from pyrebus import PyreBus
from common import MessageRequest, PeerInfos, InternalMessage
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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_queue = message_queue
        self.uuid = config.get("uuid") or str(uuid.uuid4())

        self.pyrebus = PyreBus(
            self.__on_message_received,
            self.__on_peer_connected,
            self.__on_peer_disconnected,
            self.__decode_peer_infos,
            config.get("debug", False),
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
        # TODO handle port and ssl when security implemented
        headers = {
            "uuid": self.uuid,
            "version": VERSION,
            "hostname": platform.node(),
            "port": "80",
            "macs": json.dumps(macs),
            "ssl": "0",
            "cleepdesktop": "1",
            "apps": json.dumps({}),
        }
        self.logger.debug("headers: %s", headers)

        return headers

    def __on_message_received(self, peer_id, message):
        """
        Handle received message from external bus

        Args:
            peer_id (string): peer identifier
            message (MessageRequest): message from external bus

        Returns:
            MessageResponse if message is a command
        """
        msg = InternalMessage(
            message_type=InternalMessage.MESSAGE_TYPE_TOELECTRON,
            content={peer_id: peer_id, message: message},
        )
        self.message_queue.put(msg)

    def __on_peer_connected(self, peer_id, peer_infos):
        """
        Device is connected

        Args:
            peer_id (string): peer identifier
            peer_infos (PeerInfos): peer informations (ip, port, ssl...)
        """
        self.logger.debug("Peer connected with %s", peer_infos.to_dict())

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
        self.logger.debug("Peer %s connected: %s", peer_id, peer_infos)

    def __on_peer_disconnected(self, peer_id):
        """
        Device is disconnected

        Args:
            peer_id (str): peer identifier
        """
        self.logger.debug("Peer %s disconnected", peer_id)

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
        peer_infos.ssl = bool(strtobool(infos.get("ssl", f"{peer_infos.ssl}")))
        peer_infos.cleepdesktop = bool(
            strtobool(infos.get("cleepdesktop", f"{peer_infos.cleepdesktop}"))
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
