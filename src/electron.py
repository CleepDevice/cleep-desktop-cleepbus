import logging
import websocket
from common import InternalMessage


class Electron:
    """
    Electron class to handle communication with CleepDesktop (Electron application)
    """

    def __init__(self, message_queue, websocket_enabled):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_queue = message_queue
        self.websocket = None

        if websocket_enabled:
            self.websocket = websocket.WebSocket()
            self.websocket.connect("ws://127.0.0.1:9000", timeout=0.25)
            self.logger.info("Connected to cleep-desktop websocket")
            # TODO self.websocket.send("pouet")
        else:
            self.logger.info("Websocket disabled")

    def __del__(self):
        if self.websocket:
            self.logger.info("Disconnected from cleep-desktop")
            self.websocket.close()

    def read_message(self):
        """
        Read message from websocket and put it in message queue
        """
        if not self.websocket:
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

    def send_message(self, message):
        """
        Send message to electron application

        Args:
            message (InternalMessage): message to send
        """
        if not self.websocket:
            return

        try:
            self.logger.debug("Send message to electron %s", message)
            self.websocket.send(message.content)
        except websocket.WebSocketTimeoutException:
            pass
