+++
title = "Setting up Remote SWUpdate with Yocto"
description = "Guide for extending an SWUpdate Yocto layer configuration for automatic installation of update images provided by an HTTP server."
authors = ["Adrian Winterstein"]
date = "2025-03-27"

[taxonomies]
blog-tags=["Yocto"]

[extra]
comments.host = "mastodon.social"
comments.username = "awinterstein"
comments.id = "114233470426280464"
+++

This guide shows how to setup simple remote updates with SWUpdate for Yocto, based on my previously posted guide on [setting up local updates](/blog/yocto-swupdate-local). The file and directory structure created as part of that post, will be extended and adapted as follows:

```bash
meta-swupdate-raspberrypi
├─ conf
|  └─ layer.conf                     # 🡨 extended
├─ recipes-bsp
|  ├─ libubootenv
|  |  ├─ files
|  |  |  └─ fw_env.config
|  |  └─ libubootenv_%.bbappend
|  └─ rpi-u-boot-scr
|     ├─ files
|     |  └─ boot.cmd.in
|     └─ rpi-u-boot-scr.bbappend
├─ recipes-core
|  └─ swupdate
|     ├─ files
|     |  ├─ general-server.cfg       # 🡨 new
|     |  ├─ main.cfg                 # 🡨 new
|     |  └─ sw-description           # 🡨 adapted
|     ├─ fragment.cfg                # 🡨 extended
|     ├─ swupdate_2024.%.bbappend    # 🡨 extended
|     └─ update-image.bb
└─ wic
   └─ sd-card-layout.wks
```

The resulting project repository of this guide is also available in the branch [examples/yocto-swupdate-httpd](https://github.com/awinterstein/yocto-example-raspberrypi/tree/examples/yocto-swupdate-httpd) of my [Yocto examples repository](https://github.com/awinterstein/yocto-example-raspberrypi).

## Preconditions

This guide assumes that you followed my [previous post](/blog/yocto-swupdate-local) on SWUpdate with Yocto and hence, that you are already able to create update images and install them locally.

You need a webserver that can provide update images according to the [SWUpdate documentation](https://sbabic.github.io/swupdate/suricatta.html#support-for-general-purpose-http-server) on general purpose HTTP servers. This can be the simple [SWUpdate HTTPd](https://github.com/awinterstein/swupdate-httpd) that I created in Rust for this purpose (just get the binaries at [Github](https://github.com/awinterstein/swupdate-httpd/releases/tag/latest)). Alternatively, there is also an example available in the [SWUpdate repository](https://github.com/sbabic/swupdate/blob/master/examples/suricatta/server_general.py).

Your Yocto-based device also needs a working network connection to reach the webserver. This is not covered in this guide, but you could, for example, install a `wpa_supplicant.conf` file into a Poky-based image to connect to a wifi network (if you have working wifi hardware):

```bash
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1

network={
        ssid="<my-ssid>"
        psk=<my-psk>
        priority=1
}
```

## Extend SWUpdate Build Configuration

As the first step, the [Suricatta daemon mode](https://sbabic.github.io/swupdate/suricatta.html) of SWUpdate needs to be enabled, for being able to download update images from an HTTP server. Hence, extend the file `recipes-core/swupdate/fragment.cfg` to contain at least the following content:

```bash
CONFIG_BOOTLOADERHANDLER=y # enable bootloader support
CONFIG_HASH_VERIFY=y # enable image hash verification
# CONFIG_LUA is not set

# enable support for image downloading from an HTTP server
CONFIG_CURL=y
CONFIG_CHANNEL_CURL=y
CONFIG_SURICATTA=y

#
# Server
#
# CONFIG_SURICATTA_HAWKBIT is not set
# CONFIG_SURICATTA_LUA is not set
CONFIG_SURICATTA_GENERAL=y
# CONFIG_WEBSERVER is not set
# CONFIG_MONGOOSE is not set
```

In this guide, a general HTTP server is used, which is why the option `CONFIG_SURICATTA_GENERAL` is enabled, while `CONFIG_SURICATTA_HAWKBIT` is disabled. The first configuration options were introduced in the previous guide for local updates and are needed the same way for remote updates.

## Configure the SWUpdate Daemon

For automatically downloading and applying the firmware updates, a daemon needs to run on the device that regularly polls the HTTP server providing the update images. The SWUpdate layer provides init scripts to run `swupdate` as a daemon that just needs to be configured as follows.

The `general-server.cfg` with the following content will be placed in `/etc/swupdate/conf.d` so that it will be sourced by the init script of the SWUpdate daemon:

```bash
# select the other partition to update at the sw-description later on during the update process
if [[ $(swupdate -g) == "/dev/mmcblk0p2" ]]; then COPY=copy2; else COPY=copy1; fi

SWUPDATE_ARGS="-v --syslog -l 5 -e stable,$COPY -p 'reboot' -f /etc/swupdate/main.cfg"
SWUPDATE_SURICATTA_ARGS="-t default -i 25 -u @@SWUPDATE_SERVER_ADDRESS@@"
```

It provides the command line parameters for the SWUpdate daemon for automatic downloading of updates from a general HTTP server.

In addition the `main.cfg` that is referenced in the `general-server.cfg` should be created with the following content:

```bash
globals : {
    verbose = true;
    loglevel = 5;
    syslog = true;
};

logcolors : {
    error   = "red:blink";
    warning = "yellow:underline";
    info    = "white:bright";
    debug   = "white:normal";
    trace   = "white:dim";
};

identify : (
    { name = "image"; value = "@@IMAGE@@"; },
    { name = "device"; value = "@@DEVICE@@"; },
    { name = "current_version"; value = "@@CURRENT_VERSION@@"; },
);
```

Of importance in this file, is the `identify` section. The SWUpdate daemon will send all key value pairs from this section as URL parameters to the HTTP server when checking for available updates. The keys in this example match the expected URL parameters of my [SWUpdate HTTPd](https://github.com/awinterstein/swupdate-httpd?tab=readme-ov-file#update-request). If you are using a different HTTP server to provide your update images, you can adapt them to your needs.

To make the new configuration files available in the Yocto image,
the `recipes-core/swupdate/swupdate_2024.%.bbappend` should then be adapted to contain the following:

```bash
# add current file path so that the interfaces file from here is used
FILESEXTRAPATHS:prepend := "${THISDIR}:"

# append the configuration fragment to the source files
SRC_URI:append = "file://fragment.cfg file://files/general-server.cfg file://files/main.cfg"

do_install:append() {
        # install the general configuration file for swupdate
        install -d ${D}${sysconfdir}/swupdate/
        install -m 0644 ${WORKDIR}/files/main.cfg ${D}${sysconfdir}/swupdate/

        # and replace the placeholders with the actual values
        sed -i 's|@@IMAGE@@|${IMAGE_IDENTIFIER}|g' ${D}${sysconfdir}/swupdate/main.cfg
        sed -i 's|@@DEVICE@@|${MACHINE}|g' ${D}${sysconfdir}/swupdate/main.cfg
        sed -i 's|@@CURRENT_VERSION@@|${IMAGE_VERSION}|g' ${D}${sysconfdir}/swupdate/main.cfg

        # install the configuration file for the swupdate daemon
        install -d ${D}${sysconfdir}/swupdate/conf.d
        install -m 0644 ${WORKDIR}/files/general-server.cfg ${D}${sysconfdir}/swupdate/conf.d
        sed -i -e "s|/etc/|${sysconfdir}/|" ${D}${sysconfdir}/swupdate/conf.d/general-server.cfg

        # and replace the placeholders with the actual values
        if [ -z "${SWUPDATE_SERVER_ADDRESS}" ]; then echo -e "\nVariable SWUPDATE_SERVER_ADDRESS is not set." >&2; exit 1; fi
        sed -i "s|@@SWUPDATE_SERVER_ADDRESS@@|${SWUPDATE_SERVER_ADDRESS}|g" ${D}${sysconfdir}/swupdate/conf.d/general-server.cfg

        # write the hardware revision to the default hwrevision file; this would need to be adapted
        # for a real use case, to retrieve the hardware revision from a pin configuration for example
        install -d ${D}${sysconfdir}
        echo "${MACHINE} 1.0" > ${D}${sysconfdir}/hwrevision
}
```

The variables that are used in the `swupdate_2024.%.bbappend` file need to be added to the `layer.conf`:

```bash
# Configuration for SWUpdate via the general HTTP server
IMAGE_IDENTIFIER = "swupdate-example"
IMAGE_VERSION = "0.1.0"
SWUPDATE_SERVER_ADDRESS = "http://192.168.1.101:8080"

# The image name is composed of the image identifier, the machine name,
# and the image version; with identifier and version set above
IMAGE_NAME = "${IMAGE_IDENTIFIER}_${MACHINE}_${IMAGE_VERSION}"
```

Of course, the values need to be adapted to match your configuration. Especially regarding the `SWUPDATE_SERVER_ADDRESS`. The `IMAGE_NAME` is configured to match the format expected by my [SWUpdate HTTPd](https://github.com/awinterstein/swupdate-httpd?tab=readme-ov-file#image-serving). It can be different, if you use another HTTP server to provide the update images.

For consistency, the new `IMAGE_VERSION` variable should be used now in the `sw-description` for update images as well, instead of the `DISTRO_VERSION`:

```diff
-    version = "@@DISTRO_VERSION@@";
+    version = "@@IMAGE_VERSION@@";
```

## Automatic Reboot after Image Installation

We configured SWUpdate to automatically reboot, after the download and installation of an update image by providing the `reboot` command as a post-update command to the `swupdate` daemon in the `general-server.cfg` above. There is, however, an issue in SWUpdate currently, that the post-update command is not actually executed when downloading update images from HTTP servers. See also my [bug report](https://groups.google.com/g/swupdate/c/sXqH-6H272I).

Hence, until this is fixed, it is necessary to add the patch file `recipes-core/swupdate/0001-Add-call-for-post-update-script.patch`:

```patch
From 0627ee8cc31b1f0bb74446da1e44dc51df49de69 Mon Sep 17 00:00:00 2001
From: Adrian Winterstein <mail@int.winterstein.biz>
Date: Wed, 26 Mar 2025 16:29:16 +0100
Subject: [PATCH] Add call for post update script

---
 core/stream_interface.c | 5 +++++
 1 file changed, 5 insertions(+)

diff --git a/core/stream_interface.c b/core/stream_interface.c
index f5cba496..5b048584 100644
--- a/core/stream_interface.c
+++ b/core/stream_interface.c
@@ -745,6 +745,11 @@ void *network_initializer(void *data)
 				} else {
 					notify(SUCCESS, RECOVERY_NO_ERROR, INFOLEVEL, "SWUPDATE successful !");
 					inst.last_install = SUCCESS;
+
+					if (postupdate(software, NULL))
+					{
+						return -1;
+					}
 				}
 			}
 		} else {
```

And apply it by extending the `swupdate_2024.%.bbappend` file like this:

```diff
-SRC_URI:append = "file://fragment.cfg file://files/general-server.cfg file://files/main.cfg"
+SRC_URI:append = "file://fragment.cfg file://files/general-server.cfg file://files/main.cfg \
+        file://0001-Add-call-for-post-update-script.patch"

```

## Trying the Remote Update

After building (`kas build project.yml`) and flashing the image `swupdate-example_raspberrypi0-2w-64_0.1.0.wic.bz2`, there should be an SWUpdate daemon running on your device. It regularly polls the configured HTTP server and will automatically download and install an update image, that you provide via this server.

Change the version number in the `layer.conf` and trigger another Yocto build with `kas build project.yml` afterwards:

```diff
-IMAGE_VERSION = "0.1.0"
+IMAGE_VERSION = "0.1.1"
```

Make the resulting update image `swupdate-example_raspberrypi0-2w-64_0.1.1.swu` available in the images directory of the [SWUpdate HTTPd](https://github.com/awinterstein/swupdate-httpd?tab=readme-ov-file#image-serving) or your HTTP server.

If you configured your device for being able to login (either with keyboard and screen on the device) or by also installing an SSH server into your image, you can check the log messages of the SWUpdate daemon in `/var/log/messages`.

## Next Steps

SWUpdate is configured to use the [double copy with fall-back strategy](https://sbabic.github.io/swupdate/overview.html#double-copy), which means that an update is always written in a secondary partition that is booted then, with leaving the previous partition intact. This allows for falling back to the last working image, in case that there would be any issue with the installed update image. Testing the freshly booted image and falling back in case of error is, however, not implemented as part of this guide, but could be extended.

For being able to do additional updates after the first one, it is at least needed to set the bootlader evironment variable `ustate` back to `0`, because SWUpdate does not do another update, as long as this variable indicates an image being in the testing state. It can be reset with `fw_setenv ustate 0`.