import websocket
import logging
from common import InternalMessage


class Electron:
    def __init__(self, message_queue):
        self.message_queue = message_queue

        self.ws = websocket.WebSocket()
        self.ws.connect("ws://127.0.0.1:9000", timeout=0.25)
        logging.info("Connected to cleep-desktop")
        self.ws.send("pouet")

    def __del__(self):
        if self.ws:
            logging.info("Disconnected from cleep-desktop")
            self.ws.close()

    def read_message(self):
        try:
            message = self.ws.recv()
            logging.debug("Received from electron: %r", message)
            self.message_queue.put(
                InternalMessage(
                    message_type=InternalMessage.MESSAGE_TYPE_FROMELECTRON,
                    content=message,
                )
            )
        except websocket._exceptions.WebSocketTimeoutException:
            pass

    def send_message(self, message):
        self.logging.info("Send message to electron %s", message)
