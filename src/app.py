from electron import Electron
from queue import Queue, Empty
from common import InternalMessage
import logging
from version import VERSION
from cleepbus import CleepBus

logging.basicConfig(level=logging.DEBUG)


def send_message_to_bus(message):
    logging.info("Message to send to bus: %r", message)


logging.info("========== Cleep-desktop-cleepbus v%s started ==========", VERSION)
shared_queue = Queue(maxsize=100)
cleepbus = CleepBus(shared_queue)
cleepbus.start()
#electron = Electron(shared_queue)
while True:
    logging.info('=> tick 1')
    #electron.read_message()
    logging.info('=> tick 2')
    cleepbus.read_messages()

    try:
        logging.info('=> tick 3')
        message = shared_queue.get_nowait()
        if message:
            if message.message_type == InternalMessage.MESSAGE_TYPE_FROMELECTRON:
                if message.content == "$$STOP$$":
                    break
                send_message_to_bus(message.content)
            if message.message_type == InternalMessage.MESSAGE_TYPE_TOELECTRON:
                electron.send_message(message.content)
    except Empty:
        pass

logging.info("Cleep-desktop-cleepbus stopped")
