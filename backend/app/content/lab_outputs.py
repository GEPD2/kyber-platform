"""
Simulated tool output for the Lab level. Formats follow esptool.py v4.7 and
ESP-IDF v5.3. Nothing here talks to hardware. The monitor step runs the real
ML-KEM-768 from app/services/mlkem.py, so the key material it prints is genuine.

Every function takes (command, user_id) and returns the text to print.
Device identity (MAC) is derived from the user id, so each student keeps the
same simulated board across steps.
"""
import hashlib
import os

from app.services import mlkem

HOME = "/home/student"
PROJECT = f"{HOME}/mlkem-esp32"
ESPRESSIF_OUI = "24:0a:c4"


def _mac(user_id: int) -> str:
    h = hashlib.sha256(f"lab-mac:{user_id}".encode()).digest()
    return ESPRESSIF_OUI + "".join(f":{b:02x}" for b in h[:3])


def ls_ports(cmd: str, user_id: int) -> str:
    if "/dev/serial/by-id" in cmd:
        return ("total 0\nlrwxrwxrwx 1 root root 13 Oct 13 10:42 "
                "usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_0001-if00-port0 -> ../../ttyUSB0")
    if "ttyUSB" in cmd:
        return "/dev/ttyUSB0"
    return ("/dev/tty    /dev/tty12  /dev/tty2   /dev/tty30  /dev/tty40  /dev/tty50  /dev/tty60  /dev/ttyS0\n"
            "/dev/tty0   /dev/tty13  /dev/tty20  /dev/tty31  /dev/tty41  /dev/tty51  /dev/tty61  /dev/ttyS1\n"
            "/dev/tty1   /dev/tty14  /dev/tty21  /dev/tty32  /dev/tty42  /dev/tty52  /dev/tty62  /dev/ttyS2\n"
            "/dev/tty10  /dev/tty15  /dev/tty22  /dev/tty33  /dev/tty43  /dev/tty53  /dev/tty63  /dev/ttyS3\n"
            "/dev/tty11  /dev/tty16  /dev/tty23  /dev/tty34  /dev/tty44  /dev/tty54  /dev/tty7   /dev/ttyUSB0")


def lsusb(cmd: str, user_id: int) -> str:
    return ("Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub\n"
            "Bus 001 Device 006: ID 10c4:ea60 Silicon Labs CP210x UART Bridge\n"
            "Bus 001 Device 003: ID 046d:c52b Logitech, Inc. Unifying Receiver\n"
            "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub")


def dmesg(cmd: str, user_id: int) -> str:
    return ("[ 1519.982317] usb 1-2: new full-speed USB device number 6 using xhci_hcd\n"
            "[ 1520.131904] usb 1-2: New USB device found, idVendor=10c4, idProduct=ea60, bcdDevice= 1.00\n"
            "[ 1520.131911] usb 1-2: Product: CP2102N USB to UART Bridge Controller\n"
            "[ 1520.131914] usb 1-2: Manufacturer: Silicon Labs\n"
            "[ 1520.331502] usbcore: registered new interface driver cp210x\n"
            "[ 1520.331520] usbserial: USB Serial support registered for cp210x\n"
            "[ 1520.331567] cp210x 1-2:1.0: cp210x converter detected\n"
            "[ 1520.334211] usb 1-2: cp210x converter now attached to ttyUSB0")


def usermod(cmd: str, user_id: int) -> str:
    return ("[lab] student added to group 'dialout'. On a real machine log out and back in\n"
            "[lab] (or run 'newgrp dialout') before the new group applies. The lab applies it now.\n"
            "crw-rw---- 1 root dialout 188, 0 Oct 13 10:42 /dev/ttyUSB0")


def export_idf(cmd: str, user_id: int) -> str:
    return (f"Detecting the Python interpreter\n"
            f"Checking \"python3\" ...\nPython 3.11.2\n\"python3\" has been detected\n"
            f"Checking Python compatibility\nChecking other ESP-IDF version.\n"
            f"Adding ESP-IDF tools to PATH...\n"
            f"Checking if Python packages are up to date...\n"
            f"Constraint file: {HOME}/.espressif/espidf.constraints.v5.3.txt\n"
            f"Requirement files:\n - {HOME}/esp/esp-idf/tools/requirements/requirements.core.txt\n"
            f"Python being checked: {HOME}/.espressif/python_env/idf5.3_py3.11_env/bin/python\n"
            f"Python requirements are satisfied.\n"
            f"Added the following directories to PATH:\n"
            f"  {HOME}/esp/esp-idf/components/espcoredump\n"
            f"  {HOME}/esp/esp-idf/components/partition_table\n"
            f"  {HOME}/esp/esp-idf/components/app_update\n"
            f"  {HOME}/.espressif/tools/xtensa-esp-elf/esp-13.2.0_20240530/xtensa-esp-elf/bin\n"
            f"  {HOME}/esp/esp-idf/tools\n"
            f"Done! You can now compile ESP-IDF projects.\n"
            f"Go to the project directory and run:\n\n  idf.py build")


def _esptool_connect(user_id: int) -> str:
    mac = _mac(user_id)
    return ("esptool.py v4.7.0\nSerial port /dev/ttyUSB0\nConnecting....\n"
            "Detecting chip type... Unsupported detection protocol, switching and trying again...\n"
            "Connecting.....\nDetecting chip type... ESP32\n"
            "Chip is ESP32-D0WD-V3 (revision v3.1)\n"
            "Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None\n"
            f"Crystal is 40MHz\nMAC: {mac}\nUploading stub...\nRunning stub...\nStub running...\n")


def chip_id(cmd: str, user_id: int) -> str:
    return (_esptool_connect(user_id)
            + f"Warning: ESP32 has no Chip ID. Reading MAC instead.\nMAC: {_mac(user_id)}\n"
            + "Hard resetting via RTS pin...")


def flash_id(cmd: str, user_id: int) -> str:
    return (_esptool_connect(user_id)
            + "Manufacturer: 20\nDevice: 4016\nDetected flash size: 4MB\n"
            + "Flash voltage set by a strapping pin to 3.3V\nHard resetting via RTS pin...")


def set_target(cmd: str, user_id: int) -> str:
    return ("Adding \"set-target\"'s dependency \"fullclean\" to list of commands with default set of options.\n"
            "Executing action: fullclean\nBuild directory '" + PROJECT + "/build' not found. Nothing to clean.\n"
            "Executing action: set-target\nSet Target to: esp32, new sdkconfig will be created.\n"
            f"Running cmake in directory {PROJECT}/build\n"
            "Executing \"cmake -G Ninja -DPYTHON_DEPS_CHECKED=1 -DPYTHON=" + HOME
            + "/.espressif/python_env/idf5.3_py3.11_env/bin/python -DESP_PLATFORM=1 -DIDF_TARGET=esp32 "
            + f"-DCCACHE_ENABLE=0 {PROJECT}\"...\n"
            "-- Found Git: /usr/bin/git (found version \"2.39.2\")\n"
            "-- The C compiler identification is GNU 13.2.0\n"
            "-- The CXX compiler identification is GNU 13.2.0\n"
            "-- The ASM compiler identification is GNU\n"
            "-- Building ESP-IDF components for target esp32\n"
            "-- Project sdkconfig file " + PROJECT + "/sdkconfig\n"
            "-- Loading defaults file " + PROJECT + "/sdkconfig.defaults...\n"
            "-- App \"mlkem_demo\" version: 1.0.0\n"
            "-- Configuring done (4.1s)\n-- Generating done (0.6s)\n"
            f"-- Build files have been written to: {PROJECT}/build")


def build(cmd: str, user_id: int) -> str:
    return ("Executing action: all (aliases: build)\n"
            f"Running ninja in directory {PROJECT}/build\n"
            "Executing \"ninja all\"...\n"
            "[1/1047] Generating project_elf_src_esp32.c\n"
            "[212/1047] Building C object esp-idf/main/CMakeFiles/__idf_main.dir/mlkem_demo.c.obj\n"
            "[213/1047] Building C object esp-idf/main/CMakeFiles/__idf_main.dir/kyber_fips203_hardened.c.obj\n"
            "[1039/1047] Linking CXX executable mlkem_demo.elf\n"
            "[1040/1047] Generating binary image from built executable\n"
            "esptool.py v4.7.0\nCreating esp32 image...\nMerged 2 ELF sections\nSuccessfully created esp32 image.\n"
            f"Generated {PROJECT}/build/mlkem_demo.bin\n"
            "[1041/1047] cd " + PROJECT + "/build/esp-idf/esptool_py && python check_sizes.py --offset 0x8000 "
            "partition --type app " + PROJECT + "/build/partition_table/partition-table.bin " + PROJECT + "/build/mlkem_demo.bin\n"
            "mlkem_demo.bin binary size 0x3b2c0 bytes. Smallest app partition is 0x100000 bytes. "
            "0xc4d40 bytes (77%) free.\n"
            "[1047/1047] Generating binary image from built executable\n"
            "Bootloader binary size 0x6880 bytes. 0x780 bytes (7%) free.\n\n"
            "Project build complete. To flash, run:\n idf.py flash\nor\n idf.py -p PORT flash\nor\n"
            " python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash "
            "--flash_mode dio --flash_size 4MB --flash_freq 40m 0x1000 build/bootloader/bootloader.bin "
            "0x8000 build/partition_table/partition-table.bin 0x10000 build/mlkem_demo.bin")


def flash(cmd: str, user_id: int) -> str:
    regions = [
        ("0x00001000", 26752, 16816, 0.8, 268.4),
        ("0x00010000", 242368, 129843, 3.1, 621.7),
        ("0x00008000", 3072, 103, 0.1, 400.2),
    ]
    lines = ["Executing action: flash", "Serial port /dev/ttyUSB0", "Connecting....",
             "Detecting chip type... ESP32",
             f"Running ninja in directory {PROJECT}/build",
             "Executing \"ninja flash\"...",
             "esptool.py --chip esp32 -p /dev/ttyUSB0 -b 460800 --before=default_reset --after=hard_reset "
             "write_flash --flash_mode dio --flash_freq 40m --flash_size 4MB 0x1000 bootloader/bootloader.bin "
             "0x10000 mlkem_demo.bin 0x8000 partition_table/partition-table.bin",
             _esptool_connect(user_id).rstrip("\n"),
             "Changing baud rate to 460800\nChanged.\nConfiguring flash size...",
             "Flash will be erased from 0x00001000 to 0x00007fff...",
             "Flash will be erased from 0x00010000 to 0x0004bfff...",
             "Flash will be erased from 0x00008000 to 0x00008fff..."]
    for addr, raw, comp, secs, kbit in regions:
        lines.append(f"Compressed {raw} bytes to {comp}...")
        for pct in (0, 25, 50, 75, 100):
            lines.append(f"Writing at {addr}... ({pct} %)")
        lines.append(f"Wrote {raw} bytes ({comp} compressed) at {addr} in {secs} seconds "
                     f"(effective {kbit} kbit/s)...\nHash of data verified.")
    lines += ["\nLeaving...", "Hard resetting via RTS pin...", "Done"]
    return "\n".join(lines)


def _hex_rows(data: bytes, width: int = 16) -> list[str]:
    return [" ".join(f"{b:02x}" for b in data[i:i + width]) for i in range(0, len(data), width)]


def monitor(cmd: str, user_id: int) -> str:
    k = 3
    sz = mlkem.sizes(k)
    ek, dk = mlkem.keygen(k, os.urandom(32), os.urandom(32))
    K, ct = mlkem.encaps(k, ek, os.urandom(32))
    K2 = mlkem.decaps(k, dk, ct)
    bad = bytes([ct[0] ^ 0x01]) + ct[1:]
    Kbar = mlkem.decaps(k, dk, bad)
    fp = mlkem.H(ek).hex()
    t = "mlkem_demo"
    out = [
        "--- idf_monitor on /dev/ttyUSB0 115200 ---",
        "--- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---",
        "ets Jul 29 2019 12:21:46\n",
        "rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)",
        "configsip: 0, SPIWP:0xee",
        "mode:DIO, clock div:2",
        "entry 0x40080400",
        "I (31) boot: ESP-IDF v5.3.1 2nd stage bootloader",
        "I (31) boot: chip revision: v3.1",
        "I (38) boot: Partition Table:",
        "I (45) boot:  0 nvs              WiFi data        01 02 00009000 00006000",
        "I (52) boot:  1 phy_init         RF data          01 01 0000f000 00001000",
        "I (60) boot:  2 factory          factory app      00 00 00010000 00100000",
        "I (104) boot: Loaded app from partition at offset 0x10000",
        "I (277) cpu_start: Pro cpu start user code",
        "I (295) app_init: Project name:     mlkem_demo",
        "I (300) app_init: ESP-IDF:          v5.3.1",
        "I (380) main_task: Started on CPU0",
        "I (390) main_task: Calling app_main()",
        f"I (391) {t}: ML-KEM-{mlkem.NAMES[k]} (FIPS 203)  k={k} eta1={mlkem.PARAMS[k][0]} "
        f"eta2={mlkem.PARAMS[k][1]} du={mlkem.PARAMS[k][2]} dv={mlkem.PARAMS[k][3]}",
        f"I (392) {t}: d, z and m drawn from esp_fill_random() (hardware RNG, RF entropy on)",
        f"I (400) {t}: KeyGen  ek = {sz['ek']} B   dk = {sz['dk']} B",
        f"I (401) {t}: H(ek) = SHA3-256(ek) = {fp}",
        f"I (402) {t}: ek[0..47]:",
    ]
    out += [f"I (402) {t}:   {row}" for row in _hex_rows(ek[:48])]
    out += [
        f"I (420) {t}: Encaps  ct = {sz['ct']} B   K  = {K.hex()}",
        f"I (437) {t}: Decaps  K' = {K2.hex()}",
        f"I (437) {t}: K == K' : {'YES' if K == K2 else 'NO'}",
        f"I (455) {t}: tampered ct (1 bit flipped) -> implicit rejection",
        f"I (455) {t}: Kbar = J(z || c') = {Kbar.hex()}",
        f"I (455) {t}: Kbar == K : {'YES' if Kbar == K else 'NO'}  (rejection key, no error signalled)",
        f"I (456) {t}: [lab] timestamps above are illustrative, not measured",
        "I (457) main_task: Returned from app_main()",
    ]
    return "\n".join(out)
