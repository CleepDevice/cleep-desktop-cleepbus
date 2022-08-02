import logging
import getopt
import sys
from queue import Queue, Empty
from electron import Electron
from common import InternalMessage
from version import VERSION
from cleepbus import CleepBus

logging.basicConfig(level=logging.DEBUG)


def send_message_to_bus(message):
    logging.info("Message to send to bus: %r", message)


def show_version():
    print(VERSION)


# command line arguments
CONFIG = {"websocket": True, "uuid": None}
try:
    opts, args = getopt.getopt(sys.argv[1:], "nu:v", ["no-ws", "uuid", "version"])
except Exception:
    logging.exception("Invalid command arguments")
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-n", "--no-ws"):
        CONFIG["websocket"] = False
    if opt in ("-u", "--uuid"):
        CONFIG["uuid"] = arg
    if opt in ("-v", "--version"):
        show_version()
        sys.exit(0)
logging.debug("Config: %s", CONFIG)

logging.info("========== cleep-desktop-cleepbus v%s started ==========", VERSION)
shared_queue = Queue(maxsize=100)
cleepbus = CleepBus(shared_queue)
cleepbus.start()
electron = Electron(shared_queue, CONFIG["websocket"])
while True:
    electron.read_message()
    cleepbus.read_messages()

    try:
        msg = shared_queue.get_nowait()
        if msg:
            if msg.message_type == InternalMessage.MESSAGE_TYPE_FROMELECTRON:
                if msg.content == "$$STOP$$":
                    break
                send_message_to_bus(msg.content)
            if msg.message_type == InternalMessage.MESSAGE_TYPE_TOELECTRON:
                electron.send_message(msg.content)
    except Empty:
        pass

logging.info("Cleep-desktop-cleepbus stopped")
