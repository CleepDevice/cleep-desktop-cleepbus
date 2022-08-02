# cleep-desktop-cleepbus

Cleep-desktop binary to connect to Cleep network.

Written in Python to keep compatibility with 0MQ pyre bus python implementation used in Cleep devices.

It dialogs with cleep-desktop via websocket.

## Build

Binary is generated using excellent pyinstaller software under all platform (macos, linux and windows).

Zipped archive is generated in `dist` directory

Build scripts will publish new release on Github according to cleepbus version.

### linux

Execute command from root directory

>> scripts/build-linux.sh


