"""
Level 7: Lab. A simulated terminal that walks through the real ESP-IDF flow:
find the board, identify the chip, build, flash, and watch it generate an
ML-KEM key. No ESP32 or FPGA is needed; outputs come from lab_outputs.py and
the final step runs the real ML-KEM-768 (app/services/mlkem.py).

Commands are matched with re.fullmatch on the whitespace-normalised input.
"""
from app.content.schema import L, card, term

S_FIND = L("Find the board", "Εύρεση πλακέτας")
S_TOOLS = L("Toolchain", "Εργαλεία")
S_FLASH = L("Build and flash", "Build και flash")
S_RUN = L("Run on the device", "Εκτέλεση στη συσκευή")

PORT = r"/dev/ttyUSB0"
HOME = r"(\$HOME|~|/home/student)"
ESPTOOL = r"(esptool(\.py)?|python3? -m esptool)"
ESPTOOL_OPTS = r"(( (-p|--port)[ =]/dev/ttyUSB0)|( (-b|--baud)[ =]\d+)|( (-c|--chip)[ =](esp32|auto)))*"
IDF_PORT = r"( (-p|--port)[ =]/dev/ttyUSB0)?( (-b|--baud)[ =]\d+)?( (-p|--port)[ =]/dev/ttyUSB0)?"

NOT_FOUND = "bash: {cmd}: command not found"
# Diagnostics are expanded with Match.expand, so \g<port> is the port the student typed.
BUILTIN_UART = r"(-p|--port)[ =](?P<port>/dev/ttyS\d+)(?= |$)"
NO_DEVICE = ("Serial port \\g<port>\nConnecting......................................\n\n"
             "A fatal error occurred: Failed to connect to Espressif device: No serial data received.\n"
             "For troubleshooting steps visit: https://docs.espressif.com/projects/esptool/en/latest/troubleshooting.html\n"
             "[lab] \\g<port> is a built-in UART of the PC; nothing answers on it.")
BAD_PORT = r"(-p|--port)[ =](?P<port>/dev/\S+)(?<!/dev/ttyUSB0)(?= |$)"
WRONG_PORT = ("A fatal error occurred: Could not open \\g<port>, the port is busy or doesn't exist.\n"
              "([Errno 2] could not open port \\g<port>: [Errno 2] No such file or directory: '\\g<port>')\n\n"
              "Hint: Check if the port is correct and ESP connected")

# Virtual project the terminal can ls / cat / tree. Public: contains no answers.
FILES = {
    "CMakeLists.txt": (
        "cmake_minimum_required(VERSION 3.16)\n"
        "include($ENV{IDF_PATH}/tools/cmake/project.cmake)\n"
        "project(mlkem_demo)\n"),
    "sdkconfig.defaults": (
        "# The ML-KEM task keeps several 256-coefficient polynomials on its stack.\n"
        "CONFIG_ESP_MAIN_TASK_STACK_SIZE=4096\n"
        "CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y\n"
        "CONFIG_ESP_CONSOLE_UART_BAUDRATE=115200\n"
        "# Keep RF entropy available so esp_fill_random() is a true RNG.\n"
        "CONFIG_BT_ENABLED=y\n"),
    "main/CMakeLists.txt": (
        "idf_component_register(SRCS \"mlkem_demo.c\"\n"
        "                       INCLUDE_DIRS \".\")\n"),
    "main/kyber_fips203_hardened.c": (
        "/* The platform's hardened FIPS 203 reference (full_code/), copied in with two edits:\n"
        " *   #define KYBER_K 3                       (ML-KEM-768)\n"
        " *   randombytes() returns esp_fill_random(out, n); return 0;\n"
        " * The full file is about 700 lines; see the Insane level for its internals. */\n"),
    "main/mlkem_demo.c": (
        "#include <stdio.h>\n"
        "#include <string.h>\n"
        "#include \"esp_log.h\"\n"
        "#include \"esp_random.h\"\n"
        "#include \"freertos/FreeRTOS.h\"\n"
        "#include \"freertos/task.h\"\n"
        "\n"
        "/* Unity build: pulls in mlkem_keygen_rand / mlkem_encaps_rand / mlkem_decaps. */\n"
        "#include \"kyber_fips203_hardened.c\"\n"
        "\n"
        "static const char *TAG = \"mlkem_demo\";\n"
        "\n"
        "static void mlkem_task(void *arg)\n"
        "{\n"
        "    /* static: ek/dk/ct are several KB and must not live on the task stack */\n"
        "    static uint8_t ek[PKE_PK_BYTES], dk[DK_BYTES], ct[CT_BYTES];\n"
        "    uint8_t K[SS_BYTES], K2[SS_BYTES];\n"
        "\n"
        "    if (mlkem_keygen_rand(ek, dk) != 0) { ESP_LOGE(TAG, \"RNG failed\"); vTaskDelete(NULL); }\n"
        "    ESP_LOGI(TAG, \"KeyGen  ek = %d B   dk = %d B\", PKE_PK_BYTES, DK_BYTES);\n"
        "    ESP_LOG_BUFFER_HEX(TAG, ek, 48);\n"
        "\n"
        "    mlkem_encaps_rand(ek, sizeof ek, K, ct);\n"
        "    mlkem_decaps(dk, sizeof dk, ct, sizeof ct, K2);\n"
        "    ESP_LOGI(TAG, \"K == K' : %s\", memcmp(K, K2, SS_BYTES) == 0 ? \"YES\" : \"NO\");\n"
        "    vTaskDelete(NULL);\n"
        "}\n"
        "\n"
        "void app_main(void)\n"
        "{\n"
        "    /* ML-KEM needs far more than the default main-task stack. */\n"
        "    xTaskCreate(mlkem_task, \"mlkem\", 32 * 1024, NULL, 5, NULL);\n"
        "}\n"),
}

SIM = L("This is a simulation: no board is attached, but the commands are the real ones.",
        "Είναι προσομοίωση: δεν υπάρχει συνδεδεμένη πλακέτα, αλλά οι εντολές είναι οι πραγματικές.")

QUESTIONS = [
term("lab-ls-port", S_FIND,
     L("A dev board is plugged in by USB. Find the serial port Linux created for it.",
       "Μια πλακέτα συνδέθηκε με USB. Βρες τη σειριακή θύρα που δημιούργησε το Linux γι' αυτή."),
     card(L("Serial ports on Linux", "Σειριακές θύρες στο Linux"),
          L("ESP32 boards talk over a USB-to-UART bridge; Linux exposes it as /dev/ttyUSB* (CP210x, CH340) or /dev/ttyACM* (native USB).",
            "Οι πλακέτες ESP32 μιλούν μέσω γέφυρας USB-UART· το Linux την εμφανίζει ως /dev/ttyUSB* (CP210x, CH340) ή /dev/ttyACM* (native USB)."),
          "/dev/ttyUSB*  (CP210x, CH340)      /dev/ttyACM*  (native USB)",
          "plug the board in → a new ttyUSB node appears; unplug → it disappears",
          SIM),
     [L("Device files live under /dev; serial adapters start with tty.", "Τα αρχεία συσκευών βρίσκονται στο /dev· οι σειριακοί προσαρμογείς ξεκινούν με tty."),
      L("List them with ls and a wildcard, e.g. the USB ones: ttyUSB followed by *.", "Απαρίθμησέ τα με ls και wildcard, π.χ. τα USB: ttyUSB ακολουθούμενο από *.")],
     accept=[r"ls( -[a-zA-Z]+)* /dev/tty(\*|USB\*|USB0)", r"ls( -[a-zA-Z]+)* /dev/serial/by-id/?"],
     examples_ok=["ls /dev/ttyUSB*", "ls /dev/tty*", "ls -l /dev/ttyUSB*", "ls /dev/ttyUSB0", "ls -l /dev/serial/by-id/"],
     examples_bad=["ls", "ls /dev/ttyS0", "dmesg", "ls /home"],
     diagnostics=[(r"^ls /dev/ttyACM", "ls: cannot access '/dev/ttyACM*': No such file or directory"),
                  (r"^ls /dev/ttyS", "/dev/ttyS0  /dev/ttyS1  /dev/ttyS2  /dev/ttyS3\n[lab] These are the PC's built-in UARTs, not the USB board.")],
     output="ls_ports", concept="serial",
     explain=L("/dev/ttyUSB0 appeared when the board was plugged in. /dev/serial/by-id/ gives a stable name that survives re-plugging.",
               "Το /dev/ttyUSB0 εμφανίστηκε όταν συνδέθηκε η πλακέτα. Το /dev/serial/by-id/ δίνει σταθερό όνομα που μένει ίδιο μετά από αποσύνδεση και επανασύνδεση.")),

term("lab-lsusb", S_FIND,
     L("Confirm which USB-to-UART chip the board uses.", "Επιβεβαίωσε ποιο chip USB-UART χρησιμοποιεί η πλακέτα."),
     card(L("USB vendor and product IDs", "Αναγνωριστικά USB vendor και product"),
          L("Every USB device reports a vendor:product ID; 10c4:ea60 is the Silicon Labs CP210x bridge used on many ESP32 DevKits.",
            "Κάθε συσκευή USB δηλώνει ένα vendor:product ID· το 10c4:ea60 είναι η γέφυρα CP210x της Silicon Labs, που έχουν πολλά ESP32 DevKit."),
          "one line per device:  Bus … Device …: ID vendor:product  Description",
          "Bus 001 Device 006: ID 10c4:ea60 Silicon Labs CP210x UART Bridge",
          L("Knowing the bridge tells you which driver (cp210x, ch341) and which udev rule you need.",
            "Αν ξέρεις τη γέφυρα, ξέρεις ποιον driver (cp210x, ch341) και ποιον κανόνα udev χρειάζεσαι.")),
     [L("There is a command that lists every device on the USB bus.", "Υπάρχει εντολή που απαριθμεί όλες τις συσκευές του διαύλου USB."),
      L("It is 'ls' for USB.", "Είναι το «ls» για το USB.")],
     accept=[r"(sudo )?lsusb( -v| -t)?"],
     examples_ok=["lsusb", "sudo lsusb", "lsusb -t"],
     examples_bad=["usb", "ls usb", "lspci"],
     diagnostics=[(r"^lspci", "00:00.0 Host bridge: Intel Corporation Device 4621\n00:14.0 USB controller: Intel Corporation Alder Lake PCH USB 3.2 xHCI Host Controller\n[lab] lspci lists the PCI bus, not the devices on it.")],
     output="lsusb", concept="serial",
     explain=L("10c4:ea60 is the CP210x bridge. The ESP32 itself is behind it, reached through the UART.",
               "Το 10c4:ea60 είναι η γέφυρα CP210x. Το ίδιο το ESP32 βρίσκεται πίσω της και το φτάνουμε μέσω του UART.")),

term("lab-dmesg", S_FIND,
     L("Check the kernel log to see which tty the driver attached the board to.", "Δες το log του kernel για να μάθεις σε ποιο tty συνέδεσε ο driver την πλακέτα."),
     card(L("The kernel log", "Το log του kernel"),
          L("When a USB device appears, the driver logs what it did; dmesg shows that ring buffer.",
            "Όταν εμφανίζεται συσκευή USB, ο driver καταγράφει τι έκανε· το dmesg δείχνει αυτό τον buffer."),
          "kernel ring buffer → filter for the driver or the tty",
          "cp210x converter now attached to ttyUSB0",
          L("If no ttyUSB line appears, the cable is power-only or the driver is missing.",
            "Αν δεν εμφανιστεί γραμμή ttyUSB, το καλώδιο είναι μόνο τροφοδοσίας ή λείπει ο driver.")),
     [L("The kernel message buffer has its own command; filter it for tty.", "Ο buffer μηνυμάτων του kernel έχει δική του εντολή· φίλτραρέ τον για tty."),
      L("Pipe it into grep, or look at the last lines with tail. Some systems need sudo.", "Στείλε το σε grep με pipe, ή δες τις τελευταίες γραμμές με tail. Κάποια συστήματα θέλουν sudo.")],
     accept=[r"(sudo )?dmesg( -[a-zA-Z]+)*( \| ?(grep( -i)? ['\"]?(tty|ttyUSB|cp210x?|usb)\w*['\"]?|tail( -n ?\d+| -\d+)?))?"],
     examples_ok=["dmesg | grep tty", "sudo dmesg | grep -i tty", "dmesg | tail", "sudo dmesg | tail -n 20", "dmesg | grep cp210x", "sudo dmesg"],
     examples_bad=["dmesg | grep wifi", "journalctl", "cat /var/log/syslog"],
     diagnostics=[(r"^journalctl", "[lab] journalctl -k would show it too; this step wants dmesg."),
                  (r"dmesg \| grep (?!(-i )?['\"]?(tty|ttyUSB|cp210|usb))", "[lab] No lines matched. Look for the tty or the driver name.")],
     output="dmesg", concept="serial",
     explain=L("The cp210x driver attached the bridge to ttyUSB0, which matches what ls and lsusb showed.",
               "Ο driver cp210x συνέδεσε τη γέφυρα στο ttyUSB0, όπως έδειξαν και τα ls και lsusb.")),

term("lab-dialout", S_FIND,
     L("/dev/ttyUSB0 belongs to root:dialout. Give your user access to it.", "Το /dev/ttyUSB0 ανήκει στο root:dialout. Δώσε πρόσβαση στον χρήστη σου."),
     card(L("Permission to use the port", "Δικαίωμα χρήσης της θύρας"),
          L("Serial devices are group-owned by dialout (uucp on Arch); a user outside that group gets 'Permission denied'.",
            "Οι σειριακές συσκευές ανήκουν στην ομάδα dialout (uucp στο Arch)· χρήστης εκτός ομάδας παίρνει «Permission denied»."),
          "crw-rw---- 1 root dialout 188, 0 … /dev/ttyUSB0",
          "add yourself to the group once, log in again, done",
          L("Running every flash as root also works, but it is the classic way to break file ownership in your project.",
            "Το flash ως root επίσης δουλεύει, αλλά είναι ο κλασικός τρόπος να χαλάσουν τα δικαιώματα των αρχείων του project.")),
     [L("Add your user to a supplementary group; it needs root.", "Πρόσθεσε τον χρήστη σου σε δευτερεύουσα ομάδα· χρειάζεται root."),
      L("usermod with -a (append) and -G (groups), the group name, then your user ($USER).", "usermod με -a (append) και -G (groups), το όνομα της ομάδας, και μετά τον χρήστη ($USER).")],
     accept=[r"sudo usermod (-aG|-a -G|-G -a|--append --groups) dialout (\$USER|student|\$\(whoami\))",
             r"sudo (adduser|gpasswd -a) (\$USER|student) dialout"],
     examples_ok=["sudo usermod -aG dialout $USER", "sudo usermod -a -G dialout student", "sudo adduser $USER dialout", "sudo gpasswd -a student dialout"],
     examples_bad=["usermod -aG dialout $USER", "sudo usermod -G dialout $USER", "sudo chmod 777 /dev/ttyUSB0", "sudo usermod -aG tty $USER"],
     diagnostics=[(r"^usermod", "usermod: Permission denied.\nusermod: cannot lock /etc/passwd; try again later."),
                  (r"usermod -G dialout", "[lab] Without -a, -G REPLACES all your groups (you would lose sudo). Append instead."),
                  (r"chmod", "[lab] That works until the next re-plug; udev recreates the node with root:dialout. Fix the group instead."),
                  (r"-aG tty|-a -G tty", "[lab] tty is for virtual consoles; USB serial ports belong to another group.")],
     output="usermod", concept="serial",
     explain=L("-a appends; without it -G would replace your groups. The change applies at the next login.",
               "Το -a προσθέτει· χωρίς αυτό το -G θα αντικαθιστούσε τις ομάδες σου. Η αλλαγή ισχύει από την επόμενη σύνδεση.")),

term("lab-export", S_TOOLS,
     L("ESP-IDF is installed in ~/esp/esp-idf. Load its environment into this shell.", "Το ESP-IDF είναι εγκατεστημένο στο ~/esp/esp-idf. Φόρτωσε το περιβάλλον του σε αυτό το shell."),
     card(L("Activating ESP-IDF", "Ενεργοποίηση του ESP-IDF"),
          L("export.sh puts the Xtensa compiler, esptool and idf.py on PATH and activates IDF's Python environment, for this shell only.",
            "Το export.sh βάζει στο PATH τον compiler Xtensa, το esptool και το idf.py, και ενεργοποιεί το Python περιβάλλον του IDF, μόνο για αυτό το shell."),
          "source <script>  runs it in THIS shell;  ./<script>  runs it in a child shell",
          "after it: idf.py --version → ESP-IDF v5.3.1",
          L("It must be sourced, not executed: a child process cannot change the parent shell's PATH.",
            "Πρέπει να γίνει source, όχι εκτέλεση: μια θυγατρική διεργασία δεν μπορεί να αλλάξει το PATH του γονικού shell.")),
     [L("The script is export.sh in the ESP-IDF folder.", "Το script είναι το export.sh στον φάκελο του ESP-IDF."),
      L("Source it with '.' or 'source', not ./ (that would run it in a child shell).", "Κάνε source με «.» ή «source», όχι ./ (αυτό το τρέχει σε θυγατρικό shell).")],
     accept=[rf"(\.|source) {HOME}/esp/esp-idf/export\.sh", r"get_idf"],
     examples_ok=[". $HOME/esp/esp-idf/export.sh", "source ~/esp/esp-idf/export.sh", ". /home/student/esp/esp-idf/export.sh", "get_idf"],
     examples_bad=["~/esp/esp-idf/export.sh", "bash ~/esp/esp-idf/export.sh", "idf.py build", "./export.sh"],
     diagnostics=[(r"^idf\.py", NOT_FOUND.format(cmd="idf.py")),
                  (r"^(bash |sh |\./|~/|\$HOME/|/home)", "[lab] The script ran in a child shell and its PATH changes were lost. Source it instead."),
                  (r"^(\.|source) \./export\.sh", "bash: ./export.sh: No such file or directory")],
     output="export_idf", concept="toolchain",
     explain=L("Sourcing runs the script inside the current shell, so the PATH it sets stays. get_idf is the alias the install guide suggests.",
               "Το source τρέχει το script μέσα στο τρέχον shell, οπότε το PATH που ορίζει μένει. Το get_idf είναι το alias που προτείνει ο οδηγός εγκατάστασης.")),

term("lab-chip-id", S_TOOLS,
     L("Use esptool to talk to the board on /dev/ttyUSB0 and identify the chip.", "Χρησιμοποίησε το esptool για να μιλήσεις στην πλακέτα στο /dev/ttyUSB0 και να αναγνωρίσεις το chip."),
     card(L("esptool and the ROM bootloader", "Το esptool και ο ROM bootloader"),
          L("esptool pulses DTR/RTS to reset the ESP32 into its ROM download mode, then speaks the serial bootloader protocol.",
            "Το esptool δίνει παλμούς στα DTR/RTS για να κάνει reset το ESP32 σε ROM download mode, και μετά μιλά το πρωτόκολλο του σειριακού bootloader."),
          "esptool.py -p PORT <command>      e.g. read_mac, flash_id, write_flash",
          "Detecting chip type... ESP32 / Chip is ESP32-D0WD-V3",
          L("If auto-reset fails, hold BOOT while tapping EN; that is the same strapping the tool does electrically.",
            "Αν αποτύχει το auto-reset, κράτα το BOOT πατώντας στιγμιαία το EN· είναι η ίδια ρύθμιση strapping που κάνει το εργαλείο ηλεκτρικά.")),
     [L("The tool is esptool.py; give it the port and the command that reads the chip identity.", "Το εργαλείο είναι το esptool.py· δώσ' του τη θύρα και την εντολή που διαβάζει την ταυτότητα του chip."),
      L("Port flag is -p (or --port). The command name has 'chip' and 'id' in it.", "Η σημαία θύρας είναι -p (ή --port). Το όνομα της εντολής περιέχει «chip» και «id».")],
     accept=[rf"{ESPTOOL}{ESPTOOL_OPTS} chip[_-]id"],
     examples_ok=["esptool.py -p /dev/ttyUSB0 chip_id", "esptool.py --port /dev/ttyUSB0 chip_id", "esptool -p /dev/ttyUSB0 chip-id",
                  "python -m esptool --chip esp32 -p /dev/ttyUSB0 chip_id", "esptool.py chip_id"],
     examples_bad=["esptool.py -p /dev/ttyS0 chip_id", "esptool.py -p /dev/ttyUSB0 read_mac", "idf.py chip_id", "esptool.py -p /dev/ttyUSB1 chip_id"],
     diagnostics=[(BUILTIN_UART, NO_DEVICE), (BAD_PORT, WRONG_PORT),
                  (r"^esptool(\.py)?.* read[_-]mac", "[lab] read_mac only prints the MAC. This step wants the command that detects the chip."),
                  (r"^idf\.py", "idf.py: error: unrecognised command; chip identification is esptool's job.")],
     output="chip_id", concept="flashing",
     explain=L("esptool reset the board into the ROM bootloader and identified an ESP32-D0WD-V3. The ESP32 has no separate chip ID, so it prints the MAC.",
               "Το esptool έκανε reset την πλακέτα στον ROM bootloader και αναγνώρισε ένα ESP32-D0WD-V3. Το ESP32 δεν έχει ξεχωριστό chip ID, οπότε τυπώνει τη MAC.")),

term("lab-flash-id", S_TOOLS,
     L("How big is the external SPI flash? Ask esptool.", "Πόσο μεγάλη είναι η εξωτερική SPI flash; Ρώτα το esptool."),
     card(L("External flash", "Εξωτερική flash"),
          L("The ESP32 runs code from an external SPI flash; its JEDEC ID tells the size, which the build must match.",
            "Το ESP32 τρέχει κώδικα από εξωτερική SPI flash· το JEDEC ID της δείχνει το μέγεθος, με το οποίο πρέπει να συμφωνεί το build."),
          "JEDEC ID = Manufacturer (1 byte) + Device (2 bytes); last byte = log2(size)",
          "Device 4016 → 2^0x16 bytes = 4 MB",
          L("The ML-KEM firmware is about 240 KB, far below the 1 MB app partition; sdkconfig.defaults sets 4MB to match.",
            "Το firmware ML-KEM είναι περίπου 240 KB, πολύ κάτω από το partition εφαρμογής του 1 MB· το sdkconfig.defaults ορίζει 4MB για να ταιριάζει.")),
     [L("Same tool and port as before, a different command.", "Ίδιο εργαλείο και θύρα με πριν, διαφορετική εντολή."),
      L("The command asks the flash chip for its ID.", "Η εντολή ζητά από το chip της flash το ID του.")],
     accept=[rf"{ESPTOOL}{ESPTOOL_OPTS} flash[_-]id"],
     examples_ok=["esptool.py -p /dev/ttyUSB0 flash_id", "esptool -p /dev/ttyUSB0 flash-id", "esptool.py --port /dev/ttyUSB0 -b 460800 flash_id"],
     examples_bad=["esptool.py -p /dev/ttyUSB0 chip_id", "esptool.py -p /dev/ttyS0 flash_id", "idf.py size"],
     diagnostics=[(BUILTIN_UART, NO_DEVICE), (BAD_PORT, WRONG_PORT),
                  (r"chip[_-]id", "[lab] Already done. This time ask the flash memory, not the chip."),
                  (r"^idf\.py size", "[lab] idf.py size reports the firmware size; there is nothing built yet.")],
     output="flash_id", concept="flashing",
     explain=L("Device 0x4016: capacity code 0x16 = 2²² bytes = 4 MB.", "Device 0x4016: κωδικός χωρητικότητας 0x16 = 2²² bytes = 4 MB.")),

term("lab-set-target", S_FLASH,
     L("In ~/mlkem-esp32, configure the project for the chip you just detected.", "Στο ~/mlkem-esp32, ρύθμισε το project για το chip που μόλις αναγνώρισες."),
     card(L("Choosing the target", "Επιλογή στόχου"),
          L("ESP-IDF builds for one chip family at a time; set-target picks the compiler and a fresh sdkconfig.",
            "Το ESP-IDF κάνει build για μία οικογένεια chip τη φορά· το set-target διαλέγει τον compiler και φτιάχνει νέο sdkconfig."),
          "idf.py set-target <chip family>",
          "ESP32 (Xtensa LX6) ≠ ESP32-C3 (RISC-V): different compilers",
          L("ML-KEM itself is portable C; only the toolchain and the RNG driver differ per target.",
            "Το ίδιο το ML-KEM είναι portable C· ανά στόχο αλλάζουν μόνο τα εργαλεία και ο driver του RNG.")),
     [L("idf.py has a sub-command for choosing the chip.", "Το idf.py έχει υπο-εντολή για την επιλογή chip."),
      L("set-target followed by the chip family esptool reported.", "set-target ακολουθούμενο από την οικογένεια chip που ανέφερε το esptool.")],
     accept=[r"idf\.py set-target esp32"],
     examples_ok=["idf.py set-target esp32"],
     examples_bad=["idf.py set-target esp32s3", "idf.py set-target", "idf.py menuconfig", "idf.py build"],
     diagnostics=[(r"set-target esp32(s2|s3|c\d|h\d|p4)", "[lab] That is a different chip family. esptool reported a plain ESP32."),
                  (r"^idf\.py build", "[lab] Set the target first, so the build uses the right compiler."),
                  (r"^idf\.py menuconfig", "[lab] menuconfig works, but the defaults in sdkconfig.defaults already fit. Set the target first.")],
     output="set_target", concept="toolchain",
     explain=L("The project is now configured for the Xtensa ESP32 and sdkconfig.defaults was applied.",
               "Το project ρυθμίστηκε για το Xtensa ESP32 και εφαρμόστηκε το sdkconfig.defaults.")),

term("lab-build", S_FLASH,
     L("Build the firmware (it compiles the hardened ML-KEM C reference for the ESP32).", "Κάνε build το firmware (κάνει compile την hardened C αναφορά του ML-KEM για το ESP32)."),
     card(L("Building the firmware", "Build του firmware"),
          L("idf.py runs CMake and Ninja and produces three images: the bootloader, the partition table, and the app.",
            "Το idf.py τρέχει CMake και Ninja και παράγει τρεις εικόνες: τον bootloader, τον πίνακα partitions και την εφαρμογή."),
          "bootloader @ 0x1000   partition table @ 0x8000   app @ 0x10000",
          "mlkem_demo.bin 0x3b2c0 bytes (77% of the 1 MB app partition free)",
          L("Try 'cat main/mlkem_demo.c': the RNG comes from esp_fill_random(), and the task gets a 32 KB stack because ML-KEM keeps several polynomials on it.",
            "Δοκίμασε «cat main/mlkem_demo.c»: το RNG έρχεται από το esp_fill_random(), και το task παίρνει stack 32 KB επειδή το ML-KEM κρατά εκεί αρκετά πολυώνυμα.")),
     [L("One idf.py sub-command compiles everything.", "Μία υπο-εντολή του idf.py κάνει compile τα πάντα."),
      L("It is the word that means 'compile and link'.", "Είναι η λέξη που σημαίνει «compile και link».")],
     accept=[r"idf\.py( -v)? (build|all)"],
     examples_ok=["idf.py build", "idf.py all", "idf.py -v build"],
     examples_bad=["make", "idf.py flash", "cmake ..", "gcc main/mlkem_demo.c"],
     diagnostics=[(r"^make", "make: *** No targets specified and no makefile found.  Stop.\n[lab] ESP-IDF v5 uses CMake through idf.py."),
                  (r"^(gcc|cc) ", "[lab] The host gcc builds for your PC, not for the Xtensa ESP32."),
                  (r"^idf\.py.* flash", "[lab] flash would build first anyway, but check the build on its own before touching the board.")],
     output="build", concept="toolchain",
     explain=L("Three images were produced. The app is about 237 KB, comfortably inside the 1 MB factory partition.",
               "Παράχθηκαν τρεις εικόνες. Η εφαρμογή είναι περίπου 237 KB, άνετα μέσα στο factory partition του 1 MB.")),

term("lab-flash", S_FLASH,
     L("Write the firmware to the board on /dev/ttyUSB0.", "Γράψε το firmware στην πλακέτα στο /dev/ttyUSB0."),
     card(L("Flashing", "Flash"),
          L("The flashing action of idf.py calls esptool write_flash with the three images at their offsets, verifying a hash of each.",
            "Η ενέργεια flash του idf.py καλεί το esptool write_flash με τις τρεις εικόνες στα offsets τους, επαληθεύοντας hash για κάθε μία."),
          "idf.py -p PORT [-b BAUD] <action>",
          "0x1000 bootloader, 0x8000 partition table, 0x10000 app → 'Hash of data verified.'",
          L("A higher baud (-b 460800) only speeds up the transfer; the console later runs at 115200.",
            "Μεγαλύτερο baud (-b 460800) απλώς επιταχύνει τη μεταφορά· η κονσόλα μετά τρέχει στα 115200.")),
     [L("idf.py again, with the port and the action that writes to flash.", "Πάλι idf.py, με τη θύρα και την ενέργεια που γράφει στη flash."),
      L("-p for the port, then the action named after the memory.", "-p για τη θύρα, και μετά η ενέργεια με το όνομα της μνήμης.")],
     accept=[rf"idf\.py{IDF_PORT} flash"],
     examples_ok=["idf.py -p /dev/ttyUSB0 flash", "idf.py -p /dev/ttyUSB0 -b 460800 flash", "idf.py --port /dev/ttyUSB0 flash", "idf.py flash"],
     examples_bad=["idf.py -p /dev/ttyS0 flash", "idf.py -p /dev/ttyUSB0 monitor", "esptool.py -p /dev/ttyUSB0 erase_flash", "idf.py -p /dev/ttyUSB0 flash monitor"],
     diagnostics=[(BUILTIN_UART, NO_DEVICE), (BAD_PORT, WRONG_PORT),
                  (r"erase[_-]flash", "[lab] erase_flash wipes everything, including NVS. Not needed for this step."),
                  (r"flash monitor", "[lab] That works in real life; here, do the two steps separately to see each one."),
                  (r"^idf\.py.* monitor", "[lab] There is nothing on the board yet. Flash first.")],
     output="flash", concept="flashing",
     explain=L("All three regions were written and their hashes verified; esptool then reset the chip into the new app.",
               "Γράφτηκαν και οι τρεις περιοχές και επαληθεύτηκαν τα hash τους· μετά το esptool έκανε reset το chip στη νέα εφαρμογή.")),

term("lab-monitor", S_RUN,
     L("Open the serial console and watch the board generate an ML-KEM-768 key pair.", "Άνοιξε τη σειριακή κονσόλα και δες την πλακέτα να παράγει ζεύγος κλειδιών ML-KEM-768."),
     card(L("The serial monitor", "Η σειριακή κονσόλα"),
          L("ESP-IDF's serial console resets the board and prints its UART at 115200 baud, decoding addresses in panics. Ctrl+] quits.",
            "Η σειριακή κονσόλα του ESP-IDF κάνει reset την πλακέτα και τυπώνει το UART της στα 115200 baud, αποκωδικοποιώντας διευθύνσεις σε panic. Το Ctrl+] βγαίνει."),
          "KeyGen → Encaps → Decaps → K == K'; flipped bit → K̄ = J(z ‖ c')",
          "ML-KEM-768: ek 1184 B, dk 2400 B, ct 1088 B, K 32 B",
          L("The key material printed is computed by a real FIPS 203 implementation on the server; only the board and its timings are simulated.",
            "Τα κλειδιά που τυπώνονται υπολογίζονται από πραγματική υλοποίηση FIPS 203 στον server· προσομοιώνονται μόνο η πλακέτα και οι χρόνοι της.")),
     [L("idf.py, the port, and the action that opens the console.", "idf.py, η θύρα, και η ενέργεια που ανοίγει την κονσόλα."),
      L("The action is the word for watching serial output.", "Η ενέργεια είναι η λέξη για την παρακολούθηση της σειριακής εξόδου.")],
     accept=[rf"idf\.py{IDF_PORT}( flash)? monitor"],
     examples_ok=["idf.py -p /dev/ttyUSB0 monitor", "idf.py monitor", "idf.py -p /dev/ttyUSB0 flash monitor"],
     examples_bad=["screen /dev/ttyUSB0", "idf.py -p /dev/ttyS0 monitor", "cat /dev/ttyUSB0", "minicom"],
     diagnostics=[(BUILTIN_UART, NO_DEVICE), (BAD_PORT, WRONG_PORT),
                  (r"^(screen|minicom|picocom|cat) ", "[lab] That would show the text, but at the wrong baud and without address decoding. Use the IDF monitor.")],
     output="monitor", concept="rng",
     explain=L("A real ML-KEM-768 key pair: K matches K', and the tampered ciphertext produced the implicit-rejection key instead of an error.",
               "Ένα πραγματικό ζεύγος κλειδιών ML-KEM-768: το K ταιριάζει με το K′, και το αλλοιωμένο κρυπτογράφημα έδωσε το κλειδί της implicit rejection αντί για σφάλμα.")),
]
