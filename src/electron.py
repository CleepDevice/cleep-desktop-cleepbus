import logging
import websocket
import time
import json
from common import InternalMessage


class Electron:
    """
    Electron class to handle communication with CleepDesktop (Electron application)
    """

    def __init__(self, message_queue, config):
        """
        Args:
            message_queue (Queue): message queue instance
            config (dict): app configuration
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if config.get("debug", False):
            self.logger.setLevel(logging.DEBUG)
        self.message_queue = message_queue
        self.websocket = None
        self.config = config
        if not self.config.get("websocketport", None) or not self.config.get(
            "websocket", False
        ):
            self.logger.info("Websocket disabled")

    def __del__(self):
        """
        Close websocket
        """
        self.stop()

    def stop(self):
        """
        Stop websocket connection
        """
        if self.websocket:
            self.logger.info("Disconnected from cleep-desktop")
            self.websocket.close()

    def is_connected(self):
        """
        Return websocket connection state
        Returns:
            bool: True if connected to electron
        """
        return bool(self.websocket)

    def __connectToWebsocket(self):
        """
        Connect to Electron websocket
        """
        try:
            websocketPort = self.config.get("websocketport")
            if websocketPort and self.config.get("websocket", False):
                self.websocket = websocket.WebSocket()
                self.websocket.connect(f"ws://127.0.0.1:{websocketPort}", timeout=0.25)
                self.logger.info("Connected to cleep-desktop websocket")
        except ConnectionRefusedError:
            self.logger.info(
                "Websocket server is not available. Retrying in few seconds"
            )
            time.sleep(1)

    def read_message(self):
        """
        Read message from websocket and put it in message queue
        """
        if not self.config.get("websocket", False):
            return

        if not self.websocket:
            self.__connectToWebsocket()
            return

        try:
            message = self.websocket.recv()
            self.logger.debug("Received from electron: %r", message)
            self.message_queue.put(
                InternalMessage(
                    message_type=InternalMessage.MESSAGE_TYPE_FROMELECTRON,
                    content=message,
                )
            )
        except websocket.WebSocketTimeoutException:
            pass
        except websocket.WebSocketConnectionClosedException:
            self.logger.warning("Websocket disconnected")
            self.websocket = None

    def send_message(self, message):
        """
        Send message to electron application

        Args:
            message (InternalMessage): message to send
        """
        if not self.config.get("websocket", False):
            return

        if not self.websocket:
            # do not try to connect to websocket here, read_message does it regularly
            return

        try:
            self.logger.debug("Send message to electron: %s", message.to_dict())
            self.websocket.send(json.dumps(message.to_dict()))
        except websocket.WebSocketTimeoutException:
            pass
        except websocket.WebSocketConnectionClosedException:
            self.logger.warning("Websocket disconnected")
            self.websocket = None
