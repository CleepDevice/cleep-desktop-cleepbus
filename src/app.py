import logging
import getopt
import sys
from queue import Queue, Empty
from electron import Electron
from gevent import sleep as gsleep
from common import InternalMessage
from version import VERSION
from cleepbus import CleepBus
import sentry_sdk
from platform import platform, processor

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

SENTRY_DSN = "https://47efccd983f44af9b37dd98c8d643ece@o97410.ingest.sentry.io/6704013"
SENTRY_IGNORED_EXCEPTIONS = [KeyboardInterrupt]
QUEUE_TIMEOUT = 10 # seconds


def send_message_to_bus(message):
    logger.info("Message received from electron: %r", message)


def process_queue():
    """
    Process messages queue

    Returns:
        bool: False if application received stop order, True otherwise
    """
    try:
        msg = shared_queue.get(block=True, timeout=QUEUE_TIMEOUT)
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
    print(" -t|--test:    lauch app and stop")
    print(" -h|--help:    this help")


# command line arguments
CONFIG = {"websocket": True, "uuid": None, "debug": False}
RUN_AND_STOP = False
try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "nu:vdp:ht",
        ["debug", "no-ws", "uuid=", "version", "ws-port=", "help", "test"],
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
        logging.basicConfig(level=logging.INFO)
    if opt in ("-t", "--test"):
        RUN_AND_STOP = True
    if opt in ("-v", "--version"):
        show_version()
        sys.exit(0)
    if opt in ("-h", "--help"):
        show_usage()
        sys.exit(1)

logger = logging.getLogger("App")
logger.debug("Config: %s", CONFIG)

if not CONFIG.get("debug", False):
    sentry_sdk.init(dsn=SENTRY_DSN, release=f"cleepbus@{VERSION}", ignore_errors=SENTRY_IGNORED_EXCEPTIONS)
    sentry_sdk.set_tag("platform", platform())
    sentry_sdk.set_tag("processor", processor())
    logger.info("Crash report enabled")
else:
    logger.info("Crash report disabled")

logger.info("========== cleep-desktop-cleepbus v%s started ==========", VERSION)
exit_code = 0
try:
    shared_queue = Queue(maxsize=100)
    cleepbus = CleepBus(shared_queue, CONFIG)
    cleepbus.start()
    electron = Electron(shared_queue, CONFIG)

    if RUN_AND_STOP:
        logger.info('********** wait and see')
        gsleep(10.0)
    else:
        while True:
            electron.read_message()
            cleepbus.read_messages()
            if electron.is_connected():
                running = process_queue()
                if not running:
                    logger.info("Received quit command from electron")
                    break
            else:
                gsleep(1.0)

except KeyboardInterrupt:
    pass

except Exception as error:
    logger.exception("Main exception")
    if not CONFIG.get("debug", False):
        sentry_sdk.capture_exception(error)
    exit_code = 1

try:
    cleepbus.stop()
    electron.stop()
except Exception:
    pass

logger.info("cleep-desktop-cleepbus stopped")
sys.exit(exit_code)
