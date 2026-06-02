# Installing Ubuntu 24.04.2 on PicoCalc using Luckfox Lyra B

<span><img src="https://img.shields.io/badge/PicoCalc-LuckFox%20%2B%20Linux-5E81AC?style=for-the-badge&logo=linux&logoColor=white"/></span>
<span><img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/></span>
<span><img src="https://img.shields.io/badge/Ubuntu-24.04.2-E95420?style=for-the-badge&logo=ubuntu&logoColor=white"/></span>

This guide documents the actual procedure used to install the community image `ubuntu-24.04.2-picocalc` on a **PicoCalc** using a **[Luckfox Lyra B](https://www.luckfox.com/Luckfox-Lyra)**. The Lyra B has onboard SPI NAND memory, but for this Ubuntu image a **64 GB microSD card** was used as the main storage device.

The procedure was not completely linear: a few issues appeared related to `Maskrom` mode, storage selection, and a transfer failure at 19%. This version of the guide includes those problems and how they were solved.

---

## Starting point

Hardware used:

* New PicoCalc.
* New Luckfox Lyra B.
* SanDisk Ultra 64 GB microSDXC Class 10 microSD card.
* PC with Linux.
* USB-C data cable.
* Community image `ubuntu-24.04.2-picocalc`.

The 64 GB card proved suitable for permanent use. The image requires at least 16 GB, but for a comfortable installation it is better to use 32 GB or more.

---

## Preparing the image on the PC

First, clone the repository:

```bash
git clone https://github.com/markbirss/ubuntu-24.04.2-picocalc.git
```

Enter the directory:

```bash
cd ubuntu-24.04.2-picocalc
```

Optionally, the `.git` folder can be deleted to save space:

```bash
rm -fr .git/
```

Then enter the image directory:

```bash
cd image
```

Extract the compressed file:

```bash
7z x image.7z.001
```

After extracting, enter the version folder:

```bash
cd [18Jun2025]
```

Inside that folder, files like these should appear:

```text
boot.img
MiniLoaderAll.bin
parameter.txt
rootfs.img
sha256sums.txt
uboot.img
update.img
upgrade_tool
upgrade_tool_v2.17.zip
```

In our case, the output was:

```text
total 20G
-rw-r--r-- 1 ariel ariel 9,9M jun 18  2025 boot.img
-rw-r--r-- 1 ariel ariel 263K jun 18  2025 MiniLoaderAll.bin
-rw-r--r-- 1 ariel ariel  344 jun 18  2025 parameter.txt
-rw-r--r-- 1 ariel ariel 9,8G jun 18  2025 rootfs.img
-rw-rw-r-- 1 ariel ariel  481 jun 18  2025 sha256sums.txt
-rw-r--r-- 1 ariel ariel 4,0M jun 18  2025 uboot.img
-rw-r--r-- 1 ariel ariel 9,8G jun 18  2025 update.img
-rwxrwxr-x 1 ariel ariel 3,2M sep 19  2022 upgrade_tool
-rw-rw-r-- 1 ariel ariel 1,4M jul 21  2023 upgrade_tool_v2.17.zip
```

The integrity of the files can be checked with:

```bash
sha256sum *
```

The expected hashes published in the README are:

```text
a4fbadbe374f01a6c86708eb9615fa679bf3db03fb8176f4933f6f2243ee464c  boot.img
3f43aecc1b5a43689586fe400226610ec03410308f5ce34349c9ae10c20ff82d  MiniLoaderAll.bin
05a8ebd2cc7627722af8b8c8007985989632d5ed6fafa38c2688ca70d7645e7b  parameter.txt
1f0ae484e717d80ab11fe3dc74cad10f5f374a93222b84357c59048a2819cb15  rootfs.img
143ce7fd34449b2ded2a1ac39b342652240115305c47690f8c9f590d90330b16  uboot.img
d84683d1443e6d3a046259f39e25541484a4a71f3f5582d266af0f62f7367ef2  update.img
```

---

## Identifying the microSD

Before doing anything destructive, the microSD was connected to the PC and the following command was run:

```bash
lsblk
```

The relevant output was:

```text
sdd           8:48   1  59,5G  0 disk 
└─sdd1        8:49   1  59,5G  0 part /media/ariel/0123-4567
```

This confirmed that the microSD was:

```text
/dev/sdd
```

In any case, this procedure ultimately did not use `dd`, because the extracted files were not a raw image of the entire card, but a package to be flashed with `upgrade_tool`.

---
## Downloading `upgrade_tool`

From the same folder where `update.img` was located, download the flashing tool used by the community:

```bash
wget https://files.luckfox.com/wiki/Core3566/upgrade_tool_v2.17.zip
unzip -j upgrade_tool_v2.17.zip upgrade_tool_v2.17_for_linux/upgrade_tool
chmod +x upgrade_tool
```

The output at this stage was the following:

```text
LuckFox/ubuntu-24.04.2-picocalc/image/[18Jun2025]$ wget https://files.luckfox.com/wiki/Core3566/upgrade_tool_v2.17.zip
unzip -j upgrade_tool_v2.17.zip upgrade_tool_v2.17_for_linux/upgrade_tool
chmod +x upgrade_tool
--2026-06-01 17:59:27--  https://files.luckfox.com/wiki/Core3566/upgrade_tool_v2.17.zip
Resolviendo files.luckfox.com (files.luckfox.com)... 47.79.64.227
Conectando con files.luckfox.com (files.luckfox.com)[47.79.64.227]:443... conectado.
Petición HTTP enviada, esperando respuesta... 200 OK
Longitud: 1423018 (1,4M) [application/zip]
Guardando como: ‘upgrade_tool_v2.17.zip’

upgrade_tool_v2.17. 100%[===================>]   1,36M   820KB/s    en 1,7s    

2026-06-01 17:59:31 (820 KB/s) - ‘upgrade_tool_v2.17.zip’ guardado [1423018/1423018]

Archive:  upgrade_tool_v2.17.zip
  inflating: upgrade_tool     
```

The official Luckfox wiki also documents the use of Rockchip/Luckfox tools to put the board into LOADER or MASKROM mode and flash images. For the Lyra, LOADER mode is activated by holding down `BOOT` while connecting the board via USB.

---
## Preparing the Luckfox Lyra B

The microSD must be inserted in the Luckfox Lyra B during the process.

To enter flashing mode:

1. Disconnect the Lyra from USB.
2. Insert the microSD.
3. Hold down the `BOOT` button.
4. Connect the Lyra to the PC via USB-C.
5. Release `BOOT`.
6. Check the mode with:

```bash
sudo ./upgrade_tool LD
```

At first, the board appeared like this:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Maskrom	SerialNo=
```

This indicates that the Lyra is detected, but in `Maskrom` mode.

---

## Erasing the internal SPI NAND

Since the Lyra B has onboard SPI NAND, it is advisable to erase it to prevent the board from trying to boot from the internal NAND instead of from the microSD.

The following command was run:

```bash
sudo ./upgrade_tool EF MiniLoaderAll.bin
```

The output was long, but it finished correctly:

```text
Loading loader...
Start to erase flash...
Download Boot Start
Download Boot Success
Wait For Maskrom Start
Wait For Maskrom Success
Test Device Start
Test Device Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Erase IDB Start
Erase IDB Success
Reset Device Start
Reset Device Success
Wait For Maskrom Start
Wait For Maskrom Success
Download Boot Start
Download Boot Success
Wait For Maskrom Start
Wait For Maskrom Success
Test Device Start
Test Device Success
Get FlashInfo Start
Get FlashInfo Success
Erase Flash Start
Erase Flash... (100%)
Erase Flash Success
Reset Device Start
Erase flash ok.
```

This step was successful.

---

## First problem: `SSD` does not work yet

After erasing the NAND, this command was attempted:

```bash
sudo ./upgrade_tool SSD
```

but the following error appeared:

```text
device doesn't have the feature,please do rcb command firstly
```

Then this command was attempted:

```bash
sudo ./upgrade_tool RCB
```

but it failed:

```text
Read capability Fail!
```

This happened because the board was still in `Maskrom` and did not yet have a functional loader loaded to enable commands such as `RCB` or `SSD`.

---

## Temporarily loading the loader

This was tested:

```bash
sudo ./upgrade_tool DB MiniLoaderAll.bin
```

The first time, it responded correctly:

```text
Download boot ok.
```

Then the mode was checked:

```bash
sudo ./upgrade_tool LD
```

At one stage it still appeared as `Maskrom`:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Maskrom	SerialNo=rockchip
```

Later, after disconnecting and reconnecting correctly, it appeared as `Loader`:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Loader	SerialNo=2a9dfd2363bcabd0
```

Once the board is already in `Loader`, `DB MiniLoaderAll.bin` should not be run again. If it is, this may appear:

```text
The  Device did not support this operation!
```

That error is normal in this context: `DB` was necessary to move from `Maskrom`, but it no longer applies once the board is in `Loader`.

---

## Second problem: the image tries to write to SPI NAND

A direct flash was attempted:

```bash
sudo ./upgrade_tool uf update.img
```

This time the process started, but failed:

```text
Loading firmware...
Support Type:350F	FW Ver:8.1.00	FW Time:2025-06-18 18:36:43
Loader ver:1.01	Loader Time:2025-06-18 18:34:32
Start to upgrade firmware...
Test Device Start
Test Device Success
Check Chip Start
Check Chip Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Download IDB Start
Download IDB Success
Download Firmware Start
Download Firmware Fail
Note:Image is larger than partition size in the firmware
```

This error was key. It means that `upgrade_tool` was trying to write the Ubuntu image to the internal SPI NAND, which is too small for an image of almost 10 GB.

The solution was to change the target storage device.

---

## Reading capabilities with `RCB`

In `Loader` mode, this command was run:

```bash
sudo ./upgrade_tool RCB
```

When it worked correctly, it returned:

```text
Capability:15 6F 00 00 00 00 00 00 
Direct LBA:	enabled
First 4m Access:	enabled
Read Com Log:	enabled
Read Secure Mode:	enabled
New IDB:	enabled
Switch Storage:	enabled
```

The important line is:

```text
Switch Storage:	enabled
```

This confirms that the target storage can now be changed.

---

## Viewing the available storage devices

This command was run:

```bash
sudo ./upgrade_tool SSD
```

The tool showed:

```text
List of supported storage
No=1	FLASH
No=2	EMMC
No=3	SD
No=4	SD1
No=5	SPINOR
No=6	SPINAND(*)
No=7	RAM
No=8	USB
No=9	SATA
No=10	PCIE
```

The asterisk indicated that the internal SPI NAND was selected:

```text
No=6	SPINAND(*)
```

This explained the previous error.

---

## Failed attempt: selecting `SD`

It seemed logical to choose option `3`, because it said `SD`.

This was tested:

```bash
sudo ./upgrade_tool SSD 3
```

but it failed:

```text
Error:Switch Storage failed!
```

Then it was tested in interactive mode:

```bash
sudo ./upgrade_tool SSD
```

When it asked:

```text
Input No to switch,Quit press <Q>:
```

this was entered:

```text
3
```

and it failed again:

```text
Error:Switch Storage failed!
```

Conclusion: although `SD` appeared in the list, in this loader/board combination it was not the functional target for this installation.

---

## Solution: selecting `EMMC`, option 2

A forum thread mentioned using option 2. Although it appeared as `EMMC`, in this case it was the correct option.

This command was run:

```bash
sudo ./upgrade_tool SSD
```

and when it asked:

```text
Input No to switch,Quit press <Q>:
```

this was entered:

```text
2
```

The tool responded:

```text
Switch EMMC ok.
```

Then it was verified by running this again:

```bash
sudo ./upgrade_tool SSD
```

The output showed:

```text
List of supported storage
No=1	FLASH
No=2	EMMC(*)
No=3	SD
No=4	SD1
No=5	SPINOR
No=6	SPINAND
No=7	RAM
No=8	USB
No=9	SATA
No=10	PCIE
Input No to switch,Quit press <Q>:
```

Now the asterisk was on:

```text
No=2	EMMC(*)
```

This confirmed that the correct target had been selected.

To exit without changing anything, this was entered:

```text
Q
```

---

## Successful flashing

With the board in `Loader`, `RCB` working, and `EMMC(*)` selected, this command was run:

```bash
sudo ./upgrade_tool uf update.img
```

The flashing process finished correctly:

```text
Loading firmware...
Support Type:350F	FW Ver:8.1.00	FW Time:2025-06-18 18:36:43
Loader ver:1.01	Loader Time:2025-06-18 18:34:32
Start to upgrade firmware...
Test Device Start
Test Device Success
Check Chip Start
Check Chip Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Download IDB Start
Download IDB Success
Download Firmware Start
Download Image... (100%)
Download Firmware Success
Upgrade firmware ok.
```

That is the expected result.

---

## Reboot attempt

After the successful flashing process, a reboot was attempted with:

```bash
sudo ./upgrade_tool RD
```

but the tool responded:

```text
No found any rockusb device,please plug device in!
```

This is not a problem. After `Upgrade firmware ok.`, the board may reboot on its own or stop exposing itself as a RockUSB device.

---

## Physical installation in the PicoCalc

After the successful flashing process:

1. Disconnect the Luckfox Lyra B from USB.
2. Leave the microSD inserted in the Lyra.
3. Turn off the PicoCalc.
4. Remove the batteries or power supply.
5. Open the PicoCalc.
6. Remove the original Raspberry Pi Pico.
7. Insert the Luckfox Lyra B into the socket, respecting the correct orientation.
8. Power the PicoCalc again.
9. Turn it on.

Result:

```text
Booteo OK
```

The PicoCalc booted correctly with Ubuntu 24.04.2 from the Luckfox Lyra B.

---


# Important note about option 2

Although the tool shows:

```text
No=2	EMMC
No=3	SD
```

in this specific installation the correct option was:

```text
No=2	EMMC(*)
```

The `3 SD` option appeared in the list, but could not be selected. The `2 EMMC` option was the one that allowed the large image to be flashed correctly and then allowed the Lyra B to boot in the PicoCalc.

Therefore, for this combination of **Luckfox Lyra B + Ubuntu 24.04.2 PicoCalc image + upgrade_tool**, the critical step is:

```text
Seleccionar storage 2 / EMMC
```

not `SD`.

---

# Final status

The installation finished correctly.

The final flashing output was:

```text
Download Image... (100%)
Download Firmware Success
Upgrade firmware ok.
```

After installing the Luckfox Lyra B in the PicoCalc, the system booted correctly.

<p align="center">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/img/picocalc_1.jpg" width="300">
  <img src="https://github.com/VintaBytes/LuckFox-Lyra-B-Picocalc/blob/main/img/picocalc_2.jpg" width="300">
</p>

