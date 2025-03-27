+++
title = "Setting up SWUpdate with Yocto"
description = "Guide for integrating firmware updates with the SWUpdate layer into a Yocto project using a Raspberry Pi as an example device."
authors = ["Adrian Winterstein" ]
date = "2025-02-06"
updated = "2025-03-27"

[taxonomies]
blog-tags=["Yocto"]

[extra]
comments.host = "mastodon.social"
comments.username = "awinterstein"
comments.id = 113956898144351499
+++

*This guide is based on the Raspberry Pi example of the [meta-swupdate-boards](https://github.com/sbabic/meta-swupdate-boards) repository. If you don't need the description on how the different part like the bootloader, the SWUpdate configuration and the SD card layout work together for the software updates, you can just head over to that repository and start from there.*

The resulting project repository of this guide is also available in the branch [examples/yocto-swupdate-local](https://github.com/awinterstein/yocto-example-raspberrypi/tree/examples/yocto-swupdate-local) of my [Yocto examples repository](https://github.com/awinterstein/yocto-example-raspberrypi).

A Yocto layer with the following file and directory structure is needed and will be created and explained in this guide:

```bash
meta-swupdate-raspberrypi
├─ conf
|  └─ layer.conf
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
|     |  └─ sw-description
|     ├─ fragment.cfg
|     ├─ swupdate_2024.%.bbappend
|     └─ update-image.bb
└─ wic
   └─ sd-card-layout.wks
```

## Preconditions

You need a working Yocto image build, for example, like I described in my previous post [Creating a Yocto Project](/blog/yocto-project-create). Additionally, a Raspberry Pi is needed for deployment and testing. In this guide, I'm using a Raspberry Pi Zero 2W, but other variants would work as well, as long as you change the hardware definition from `raspberrypi0-2w-64` to your variant whenever it is used in the guide. Other devices should work as well, but need their own board-support layer and probably other adaptions.

This guide assumes that you are using [kas](https://github.com/siemens/kas) as I also described in the previous post. You can still follow the guide, if you are not using it, but you need to replace the `kas` calls with the usual `bitbake` calls then.

The `meta-swupdate` layer needs to be present in your project. With kas you can just add it to your `project.yml` under the `repos` property:

```bash
  # The SWUpdate deploy tool.
  meta-swupdate:
    url: https://github.com/sbabic/meta-swupdate.git
    commit: d598d4e675b541301ea1dfc8f0c8931983b4dcd0
```

A Yocto layer for the SWUpdate configuration and adaptions needs to be present in your project. This can, for example, be done with:

```bash
source poky/oe-init-build-env
bitbake-layers create-layer ../meta-swupdate-raspberrypi
```

If you followed my previous post, make sure to also add an exception for this layer to the `.gitignore` file.

## SD Card Layout

For the update strategy [Double Copy with Fallback](https://sbabic.github.io/swupdate/overview.html#double-copy) that is used in this guide, at least three partitions are needed on the SD card: a boot partition two root partitions and optionally a data partition. Software updates will always be installed into the root partition that is not currently active / booted and the bootloader will boot that partition than after the installation of an update. The data partition can be used to store persistent data that should also survive software updates.

*Check out the [Update Strategies](https://sbabic.github.io/swupdate/scenarios.html) in the SWUpdate documentation for other possible strategies.*

Create the file `wic/sd-card-layout.wks` in your Yocto layer and insert the following content to create the partitions:

```bash
part /boot --size 100M --source bootimg-partition --ondisk mmcblk0 --fstype=vfat --label boot --active --align 4096
part / --size 200M --source rootfs --ondisk mmcblk0 --fstype=ext4 --label root --align 4096
part --size 200M --source rootfs --ondisk mmcblk0 --fstype=ext4 --label root2 --align 4096
part /media --size 1G --ondisk mmcblk0 --fstype=ext4 --label data --align 4096
```

The size of primary and secondary root partition must be large enough to accommodate potential future growth of your update images. The size of the last partition can be adapted to your needs or the partition can be left out completely. In this guide the last partition is used to store the update image for testing the local update.

The partitioning will be used when creating an SD card image via Yocto, if you add the following to your `layer.conf`:

```bash
# Definition of the partitions on the SD card
WKS_FILE = "sd-card-layout.wks"
```

[Wic](https://docs.yoctoproject.org/next/dev-manual/wic.html) would automatically create an `fstab` according to the defined partitions. However, this would only be generated into the SD card image, but not into the update image of SWUdate. Hence, you need to manually define your own `fstab` in `meta-swupdate-raspberrypi/recipes-core/base-files/base-files/fstab`:

```bash
/dev/root            /                    auto       defaults                           1  1
proc                 /proc                proc       defaults                           0  0
devpts               /dev/pts             devpts     mode=0620,ptmxmode=0666,gid=5      0  0
tmpfs                /run                 tmpfs      mode=0755,nodev,nosuid,strictatime 0  0
tmpfs                /var/volatile        tmpfs      defaults                           0  0

/dev/mmcblk0p1       /boot                vfat       defaults                           0  0
/dev/mmcblk0p4       /media               ext4       defaults                           0  0
```

To install the custom `fstab` into your image, the append file `meta-swupdate-raspberrypi/recipes-core/base-files/base-files_%.bbappend` needs to be added with the following content:

```bash
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"
```

The automatic `fstab` creation by Wic needs to be disabled then as follows in your `layer.conf`:

```bash
# Do not update the fstab file according to the SD card layout; a specific fstab
# file is provided instead, because it is also needed within the update image
WIC_CREATE_EXTRA_ARGS = "--no-fstab-update"
```

## Update Image Creation

As the next step, you need a recipe to create the update image - the image that will be installed by SWUpdate and contains the necessary metadata for the SWUpdate application to verify the update before installation.

Create the file `recipes-core/swupdate/update-image.bb` in your layer:

```bash
DESCRIPTION = "Generating the update image for SWUpdate"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

# local files to be added to the update image
SRC_URI = " \
    file://sw-description \
    "

# images to build before building update image
IMAGE_DEPENDS = "core-image-base"

# images and files that will be included in the .swu image
SWUPDATE_IMAGES = "core-image-base"

# the chosen format for the deployable image
SWUPDATE_IMAGES_FSTYPES[core-image-base] = ".rootfs.ext4.gz"
SWUPDATE_IMAGES_FSTYPES[uImage] = ".bin"

inherit swupdate
```

This recipe inherits from the `swupdate` recipe from the `meta-swupdate` layer. It mainly defines on which image the update image will be based on and which filesystem type SWUpdate should look for when creating the update image on top of it.

The `sw-description` file that is referenced in the recipe needs to be created then as well under `recipes-core/swupdate/files`:

```bash
software =
{
    version = "@@DISTRO_VERSION@@";

    @@MACHINE@@ = {
        hardware-compatibility: [ "1.0"];
        stable : {
            copy1 : {
                images: (
                    {
                        filename = "core-image-base-@@MACHINE@@.rootfs.ext4.gz";
                        type = "raw";
                        compressed = "zlib";
                        device = "/dev/mmcblk0p2";
                        sha256 = "$swupdate_get_sha256(core-image-base-@@MACHINE@@.rootfs.ext4.gz)";
                    }
                );
                bootenv: (
                    {
                        name = "partition";
                        value = "2";
                    },
                    {
                        name = "ustate";
                        value = "1";
                    }
                );
            };
            copy2 : {
                images: (
                    {
                        filename = "core-image-base-@@MACHINE@@.rootfs.ext4.gz";
                        type = "raw";
                        compressed = "zlib";
                        device = "/dev/mmcblk0p3";
                        sha256 = "$swupdate_get_sha256(core-image-base-@@MACHINE@@.rootfs.ext4.gz)";
                    }
                );
                bootenv: (
                    {
                        name = "partition";
                        value = "3";
                    },
                    {
                        name = "ustate";
                        value = "1";
                    }
                );
            };
        };
    }
}
```

This file will be included in the package of the update image. It is used by SWUpdate during the installation of an update to check the compatibility (`hardware-compatibility`, `version`), to verify the integrity (`sha256`), to select the device to write the update to (`device`) and to set the bootloader environment (`bootenv`).

As we defined the `SWUPDATE_IMAGES_FSTYPES` in the `update-image.bb` to be of `ext4.gz`, it needs to be ensured that an image with the corresponding filesystem type is actually created. Hence, add the following to the `layer.conf`:

```bash
# The filesystem types for the baked images;
# the ext4.gz will be used for the update image
IMAGE_FSTYPES = "wic.bz2 wic.bmap ext4.gz"
```

From now on, you should usually bake the `update-image` in your project instead of the `core-image-base`. This will always first create the `core-image-base` and then the `update-image` based on it. If you are using [kas](https://github.com/siemens/kas), then just change the `target` property in your `project.yml` to `update-image`. Afterwards, the update image can be build already:

```bash
kas build project.yml
```

The image will afterwards be located at something like `build/tmp/deploy/images/raspberrypi0-2w-64/update-image-raspberrypi0-2w-64.rootfs.swu`, depending on your Raspberry Pi variant.

## Include SWUpdate Tools in the Image

It will, however, not be possible yet to actually perform an update, because SWUpdate itself is not included in the `core-image-base`, yet. To change this, add the following to the `layer.conf`:

```bash
CORE_IMAGE_EXTRA_INSTALL += "swupdate u-boot-fw-utils"
```

### Configuration Fragment

The bootloader support needs to be enabled for SWUpdate, because we configured a `bootenv` within the `sw-description` file. Additionally the image has verification needs to be enabled, because we set a hash value `sha256` there as well.  This can be done by adding a configuration fragment to the SWUpdate build. Create the file `recipes-core/swupdate/fragment.cfg` with at least the following content:

```config
CONFIG_BOOTLOADERHANDLER=y # enable bootloader support
CONFIG_HASH_VERIFY=y # enable image hash verification
```

And add the recipe append file `recipes-core/swupdate/swupdate_2024.%.bbappend` with the following:

```bash
# add current file path so that the interfaces file from here is used
FILESEXTRAPATHS:prepend := "${THISDIR}:"

# append the configuration fragment to the source files
SRC_URI:append = "file://fragment.cfg"
```

### Configure SWUpdate

In case, that you want to change more configuration values of the SWUpdate build, you can open the menuconfig as follows:

```bash
source poky/oe-init-build-env
bitbake -c menuconfig swupdate
```

Update the configuration as needed, save it and exit the `menuconfig`. The config file will be saved at something like: \
`build/tmp/work/cortexa53-poky-linux/swupdate/2024.12/build/.config`

Generate a configuration fragment containing the differences of your changes and the original config file:

```bash
bitbake -c diffconfig swupdate
```

The location of the generated configuration fragment will be shown in the command output. Copy the file into the directory, where your `swupdate` recipes are located (e.g., `recipes-core/swupdate`). Be aware: If you already have a `fragment.cfg` there, you should not overwrite this file, but integrate the new changes there. The `diffconfig` command always generates the differences compared to the configuration that was generated via Yocto recipes before.

## Connection with Bootloader (U-Boot)

SWUpdate needs to work together with the bootloader for the switching between the primary and the secondary boot partition after the installation of an update. In this example U-Boot is used, which is the default for SWUpdate.

### Libubootenv

In addition, `libubootenv` must be enabled via the `layer.conf`, so that the tools for setting and reading the bootloader environment are available in the image:

```bash
PREFERRED_PROVIDER_u-boot-fw-utils = "libubootenv"
```

Create the file `recipes-bsp/libubootenv/files/fw_env.config` with the following content to tell the bootloader tools of SWUpdate where the bootloader environment is stored:

```bash
# Environment on the VFAT boot partition
/boot/uboot.env    0x0000    0x4000
```

Check the [fw_env.config](https://github.com/sbabic/meta-swupdate-boards/blob/scarthgap/recipes-bsp/libubootenv/files/rpi/fw_env.config) from the [meta-swupdate-boards](https://github.com/sbabic/meta-swupdate-boards) repository for additional configuration options of this file.

Append the file to the `libubootenv` recipe by adding the file `recipes-bsp/libubootenv/libubootenv_%.bbappend` with the following content:

```bash
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " file://fw_env.config"

do_install:append() {
    install -d ${D}${sysconfdir}
    install -m 644 ${WORKDIR}/fw_env.config ${D}${sysconfdir}
}

FILES:${PN}:append = " ${sysconfdir}"
```

### Bootloader Command

When using `meta-raspberrypi` on a Raspberry Pi, make sure to have the following set in the `layer.conf`, so that the bootloader gets actually enabled in the image:

```bash
RPI_USE_U_BOOT = "1"
```

The bootloader command must be adapted then as well to add the partition switching after an update was installed onto the secondary root partition. Hence, add the file `recipes-bsp/rpi-u-boot-scr/files/boot.cmd.in` to your layer:

```bash
saveenv
fdt addr ${fdt_addr} && fdt get value bootargs /chosen bootargs
if env exists partition; then echo Booting from mmcblk0p${partition}; else setenv partition 2; echo partition not set, default to ${partition}; fi
load mmc 0:${partition} ${kernel_addr_r} boot/@@KERNEL_IMAGETYPE@@
setenv bootargs "${bootargs} root=/dev/mmcblk0p${partition}"
@@KERNEL_BOOTCMD@@ ${kernel_addr_r} - ${fdt_addr}
```

Add the append file `recipes-bsp/rpi-u-boot-scr/rpi-u-boot-scr.bbappend` to include this into the bootloader build:

```bash
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
```

You'd need to check the documentation of your board-support package, in case that you are not using a Raspberry Pi.

## Manual Update via SD Card

To verify, that SWUpdate is configured and integrated correctly with the Yocto image a manual update can be done with an image provided on the data partition of the SD card.

As this is done manually on the device, you might want to temporarily add a known password to the `root` account by adding the following to your `layer.conf`:

```bash
# Set the root password to 'root'
PASSWD = "\$5\$AHKXXGqVAzuB2vF6\$SyaXXyZDul0E.KeQ9tKktErUXoAsx2wQ72M0YwBwKzA"
INHERIT += "extrausers"
EXTRA_USERS_PARAMS = "\
    usermod -p '${PASSWD}' root; \
    "
```

After baking the `upate-image`, flash the `core-image-base` onto a SD card and copy the `update-image-*.swu` onto the data partition of the same card. This data partition only exists, if you added it to the `sd-card-layout.wks` as described at the beginning of this guide.

Boot the device, login as the root user and execute the following:

```bash
swupdate -e stable,copy2 -H raspberrypi0-2w-64:1.0 -p 'reboot' -i /media/update-image-* -v
```

The hardware variant and version given for the parameter `-H` must match the configuration in the `sw-description` file. With the paremeter `-e`, a configuration section for the given hardware is selected in the `sw-description` file. In the case of the configuration used in this guide, it will lead to the update image being copied to `/dev/mmcblk0p3`.

After the reboot completed, check that actually the second root partition (the third partition on the SD card) was booted:

```bash
$ swupdate -g
/dev/mmcblk0p3
```

## Next Steps

The local update could be extended to automatically install updates from an USB stick, as soon as it gets connected.
An alternative would be the downloading of update images from an HTTP server. I'm showing this in the follow-up post [Setting up Remote SWUpdate with Yocto](/blog/yocto-swupdate-remote-server).
