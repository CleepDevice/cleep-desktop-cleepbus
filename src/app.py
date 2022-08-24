import logging
import getopt
import sys
from queue import Queue, Empty
from electron import Electron
from common import InternalMessage
from version import VERSION
from cleepbus import CleepBus

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def send_message_to_bus(message):
    logger.info("Message received from electron: %r", message)


def process_queue():
    """
    Process messages queue

    Returns:
        bool: False if application received stop order, True otherwise
    """
    try:
        msg = shared_queue.get_nowait()
        if msg:
            if msg.message_type == InternalMessage.MESSAGE_TYPE_FROMELECTRON:
                if msg.content == "$$STOP$$":
                    return False
                send_message_to_bus(msg.content)
            if msg.message_type == InternalMessage.MESSAGE_TYPE_TOELECTRON:
                electron.send_message(msg.content)
    except Empty:
        pass

    return True


def show_version():
    print(VERSION)


def show_usage():
    print(
        "Usage: ./cleepbus [-n|--no-ws] [-u|--uuid] [-p|--ws-port] [-d|--debug] [-v|--version] [-h|--help]"
    )
    print("options:")
    print(" -n|--no-ws:   disable websocket feature")
    print(" -u|--uuid:    specify Cleep network uuid")
    print(" -p|--ws-port: websocket port (if not disabled)")
    print(" -v|--version: show cleepbus version")
    print(" -h|--help:    this help")


# command line arguments
CONFIG = {"websocket": True, "uuid": None, "debug": False}
try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "nu:vdp:h",
        ["debug", "no-ws", "uuid=", "version", "ws-port=", "help"],
    )
except Exception:
    logging.exception("Invalid command arguments")
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-n", "--no-ws"):
        CONFIG["websocket"] = False
    if opt in ("-u", "--uuid"):
        CONFIG["uuid"] = arg
    if opt in ("-p", "--ws-port"):
        CONFIG["websocketport"] = int(arg)
    if opt in ("-d", "--debug"):
        CONFIG["debug"] = True
        logging.basicConfig(level=logging.DEBUG)
    if opt in ("-v", "--version"):
        show_version()
        sys.exit(0)
    if opt in ("-h", "--help"):
        show_usage()
        sys.exit(1)

logger = logging.getLogger("App")
logger.debug("Config: %s", CONFIG)

logger.info("========== cleep-desktop-cleepbus v%s started ==========", VERSION)
shared_queue = Queue(maxsize=100)
cleepbus = CleepBus(shared_queue, CONFIG)
cleepbus.start()
electron = Electron(shared_queue, CONFIG)
try:
    while True:
        electron.read_message()
        cleepbus.read_messages()
        if electron.is_connected():
            running = process_queue()
            if not running:
                break

except Exception:
    logger.exception("App failed")
except KeyboardInterrupt:
    pass

try:
    cleepbus.stop()
    electron.stop()
except Exception:
    pass

logger.info("cleep-desktop-cleepbus stopped")
