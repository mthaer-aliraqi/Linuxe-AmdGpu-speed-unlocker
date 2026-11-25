import shutil
import sys , os
from pathlib import Path
from PySide6.QtCore import QSettings , Qt , QProcess
from PySide6.QtWidgets import (
    QApplication,QWidget,QLabel,QPushButton,QHBoxLayout,
    QFileDialog,QRadioButton,QVBoxLayout,
    QTextEdit,
    )

# main class
class Gui(QWidget):
    def __init__(self):
        super().__init__()

        #consant , variables
        APP_FOLDER:str = str(Path(__file__).resolve().parent)
        self.ASSETS_FOLDER = APP_FOLDER+"/assets"
        self.SCRIPT_FOLDER = APP_FOLDER+"/script"

        self.lang_dict = {
            "en":{
                "lang_label":"Language",
                "gpu_unlocker_label":"GPU Unlocker",
                "bt_unlocker_on":"turn on",
                "bt_unlocker_off":"turn off",
                "bt_unlocker_shortcut":"create shortcut",
                "alert_label":"* Alert",
                "alert_text":"""* This tool is designed to improve GPU performance during gaming.
* it has been tested on [AMD Radeon R7 M350].
* the system was cachy-os , KDE-Wayland
* The developer is not responsible for any hardware or software damage caused by this tool.
* Use this tool at your own risk.
""",
                "cp_label":"GPU Control Panel",
                "bt_install_cp":"install",
                "bt_profile_cp":"create gamemode profile",
                "bt_shortcut_cp":"create shortcut",
                },
            "ar":{
                "lang_label":"اللغة",
                "gpu_unlocker_label":"فتح قفل الكرت",
                "bt_unlocker_on":"تفعيل",
                "bt_unlocker_off":"ايقاف",
                "bt_unlocker_shortcut":"انشاء اختصار",
                "alert_label":"* تنبيه",
                "alert_text":"""• هذه الأداة صُممت للحصول على أفضل أداء من الكرت الخارجي
• تم تجربتها على كرت AMD Radeon R7 M350
• بتوزيعة كاشي أو إس (CachyOS) بواجهة كي دي إي وايلاند (KDE Wayland)
• مطوّر هذه الأداة لا يتحمل أي مسؤولية عن تلف أو ضرر في أي قطعة أو نظام
• استخدمها على مسؤوليتك الخاصة
""",
                "cp_label":"لوحة تحكم GPU",
                "bt_install_cp":"تثبيت",
                "bt_profile_cp":"انشاء اعداد للالعاب",
                "bt_shortcut_cp":"انشاء اختصار",
                }
            }

        self.is_running = False

        # lang , create local saved var
        self.setting = QSettings("gpu_optimizer","language")

        # Runs Bash Command
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_output_ready)
        self.process.finished.connect(self.on_finished)
        self.process.errorOccurred.connect(self.on_process_error)
        
        # on create
        self.setup_ui()
        self.apply_language()

        # connections
        # language radio
        self.rd_bt_en.toggled.connect(self.switch_lang)
        self.rd_bt_ar.toggled.connect(self.switch_lang)
        # buttons of gpu unlocker
        self.bt_unlocker_on.clicked.connect(self.on_activate_unlocker)
        self.bt_unlocker_off.clicked.connect(self.on_de_activate_unlocker)
        self.bt_unlocker_shortcut.clicked.connect(self.create_shortcut_unlocker)
        # buttons of control panel (corectrl)
        self.bt_install_cp.clicked.connect(self.on_install_cp)
        self.bt_profile_cp.clicked.connect(self.create_profile)
        self.bt_shortcut_cp.clicked.connect(self.create_shortcut_cp)


    def setup_ui(self):
        # main layout
        self.main_layout = QVBoxLayout()
        
        # language-section
        self.lang_label = QLabel()
        self.rd_bt_en = QRadioButton("English")
        self.rd_bt_ar = QRadioButton("العربية")

        # alert-long-text
        self.alert_label = QLabel()
        self.alert_label.setStyleSheet("color: rgb(255, 196, 0)")
        self.alert_text = QTextEdit(readOnly=True)
        self.alert_text.setMaximumHeight(120)
        
        # gpu-unlocker-section
        self.gpu_unlocker_label = QLabel()
        self.gpu_unlocker_container = QHBoxLayout()
        self.bt_unlocker_on = QPushButton()
        self.bt_unlocker_off = QPushButton()
        self.bt_unlocker_shortcut = QPushButton()
        # adds-to-Hlayout
        self.gpu_unlocker_container.addWidget(self.bt_unlocker_on)
        self.gpu_unlocker_container.addWidget(self.bt_unlocker_off)
        self.gpu_unlocker_container.addWidget(self.bt_unlocker_shortcut)

        # corectrl-gpu-controller
        self.cp_label = QLabel()
        self.cp_container = QHBoxLayout()
        self.bt_install_cp = QPushButton()
        self.bt_profile_cp = QPushButton()
        self.bt_shortcut_cp = QPushButton()
        # adds-to-Hlayout
        self.cp_container.addWidget(self.bt_install_cp)
        self.cp_container.addWidget(self.bt_profile_cp)
        self.cp_container.addWidget(self.bt_shortcut_cp)

        # terminal
        self.term_text = QTextEdit(readOnly=True)
        self.term_text.setMaximumHeight(200)
        self.term_text.setPlainText("~ >")
        self.term_text.setStyleSheet("color : rgb(0, 255, 21)")

        # show-on-screen
        self.main_layout.addWidget(self.lang_label)
        self.main_layout.addWidget(self.rd_bt_en)
        self.main_layout.addWidget(self.rd_bt_ar)
        self.main_layout.addWidget(self.alert_label)
        self.main_layout.addWidget(self.alert_text)
        self.main_layout.addWidget(self.gpu_unlocker_label)
        self.main_layout.addLayout(self.gpu_unlocker_container)
        self.main_layout.addWidget(self.cp_label)
        self.main_layout.addLayout(self.cp_container)
        self.main_layout.addWidget(self.term_text)
        # adds the main_layout to screen
        self.setLayout(self.main_layout)


    def apply_language(self):
        # read value lang default is en
        self.lang:str = str(self.setting.value("lang","en",type=str))

        if (self.lang == "en"):
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.rd_bt_en.setChecked(True)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.rd_bt_ar.setChecked(True)

        # short way get dict
        txt_ui = self.lang_dict.get(self.lang,self.lang_dict["en"])

        # update text with language
        # lang
        self.lang_label.setText(txt_ui["lang_label"])
        # gpu-unlocker
        self.gpu_unlocker_label.setText(txt_ui["gpu_unlocker_label"])
        self.bt_unlocker_on.setText(txt_ui["bt_unlocker_on"])
        self.bt_unlocker_off.setText(txt_ui["bt_unlocker_off"])
        self.bt_unlocker_shortcut.setText(txt_ui["bt_unlocker_shortcut"])
        # alert-section
        self.alert_text.setPlainText(txt_ui["alert_text"])
        self.alert_label.setText(txt_ui["alert_label"])
        # control panel gpu (corectrl)
        self.cp_label.setText(txt_ui["cp_label"])
        self.bt_install_cp.setText(txt_ui["bt_install_cp"])
        self.bt_profile_cp.setText(txt_ui["bt_profile_cp"])
        self.bt_shortcut_cp.setText(txt_ui["bt_shortcut_cp"])


    def switch_lang(self):
        if (self.rd_bt_en.isChecked()):
            self.lang_new = "en"
        elif(self.rd_bt_ar.isChecked()):
            self.lang_new = "ar"

        # save data locally
        self.setting.setValue("lang",self.lang_new)

        # update ui
        self.apply_language()


    def on_output_ready(self):
        if (not self.is_running):
            self.is_running=True
        
        raw_byte = bytes(self.process.readAllStandardOutput().data())
        text = raw_byte.decode("utf-8",errors="replace")
        self.term_text.insertPlainText(text)
        self.term_text.ensureCursorVisible()


    def on_finished(self,exit_code,exit_state):
        if (self.is_running):
            self.is_running = False
            
        self.term_text.append(f"\n--- Done (Code : {exit_code}) ---\nResult : {'Success' if (exit_code == 0) else 'Failed !'}")


    def on_process_error(self,_error):
        self.is_running=False
        self.term_text.append(f"\nProcess error : {self.process.errorString()}\n--- Done (Code : 1) ---\nResult : Failed !")


    def on_activate_unlocker(self):
        if (self.is_running):
            return

        if (not self.is_running):
            self.is_running = True
            self.term_text.setPlainText("~ >")

        cache_dir = str(Path(os.getenv("XDG_CACHE_HOME") or Path.home()/".cache") /"gpu_optimizer")
        self.process.start("pkexec",["bash",self.SCRIPT_FOLDER+"/gpu_unlocker.sh" , "on",cache_dir])


    def on_de_activate_unlocker(self):
        if (self.is_running):
            return

        if (not self.is_running):
            self.is_running = True
            self.term_text.setPlainText("~ >")

        cache_dir = str(Path(os.getenv("XDG_CACHE_HOME") or Path.home() / ".cache") / "gpu_optimizer")
        self.process.start("pkexec",["bash",self.SCRIPT_FOLDER+"/gpu_unlocker.sh" , "off",cache_dir])


    def create_shortcut_unlocker(self):
        if (self.is_running):
            return

        if (not self.is_running):
            self.is_running=True
            self.term_text.setPlainText("~ >")

        # u can use self.process.start("bash",["bash_file_path"])
        # or u can use python script
        file_path:str = QFileDialog.getExistingDirectory(
            self,"Select Folder",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
            )
        # if canceled
        if (not file_path):
            self.is_running = False
            self.term_text.insertPlainText(f"\nCreating ShortCut Canceled.")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return
        
        Path(file_path).mkdir(parents=True,exist_ok=True)

        scr_path = Path(file_path) / "gpu_unlocker.sh"
        scr_code = """#!/bin/bash

# 1. Dynamically find PCI bus address for AMD GPU
AMD_PCI_BUS=$(basename "$(readlink -f /sys/bus/pci/drivers/amdgpu/0000:* 2>/dev/null | head -n 1)")

# Check if detected
if [ -z "$AMD_PCI_BUS" ]; then
    notify-send "GPU Unlocker Error:" "Could not automatically detect an active AMD GPU bound to 'amdgpu'."
    exit 1
fi

echo "Found AMD GPU at PCI Address: ${AMD_PCI_BUS}"

# 2. Functions for GPU power management
unlock_gpu() {
    # Prevent runtime auto-suspend / sleep mode
    # && added to block next operations if this operation failed , it des the same as in lock_gpu function if [ $? -en 0 ]...
    echo "on" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power/control" &>/dev/null && \

    # Block D3cold deep power-saving state
    echo "0" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/d3cold_allowed" &>/dev/null && \

    # Lock driver DPM performance level to maximum
    echo "high" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power_dpm_force_performance_level" &>/dev/null

    # read function success or fail due to wrong password or something else
    # Passes 0 if all three commands succeeded, or non-zero (1) if sudo failed
    return $?
}

lock_gpu() {

    # Restore automatic power management
    echo "auto" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power_dpm_force_performance_level" &>/dev/null

    # another way to check if operation 's successed or no 
    if [ ! $? -eq 0 ]; then
        return 1
    fi

    # another way but more easier
    if ! echo "1" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/d3cold_allowed" &>/dev/null; then
        return 1
    fi

    # if all succesed then the last one is 1 or 0 however return the value
    echo "auto" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power/control" &>/dev/null
    return $?

}

dir_data="${XDG_CACHE_HOME:-$HOME/.cache}/gpu_optimizer"
cache_data="$dir_data/unlocker_switch"

if [ -f "$cache_data" ] >/dev/null;then
    active=$(cat "$cache_data")
else
    active="off"
fi

if [ "$active" = "on" ];then
   if ! lock_gpu ;then
        echo "err: failed to lock gpu !"
        exit 1
   fi
   active="off"
   echo "gpu unlocker is off"
else
    if ! unlock_gpu;then
        echo "err: failed to unlock gpu !"
        exit 1
    fi
    active="on"
    echo "gpu unlocker is on"
fi

echo "$active" > "$cache_data"

notify-send "GPU Unlocker" "gpu unlocker is $active"
"""
        scr_path.write_text(data=scr_code , encoding="utf-8")
        
        if (not scr_path.exists()):
            self.is_running=False
            self.term_text.insertPlainText(f"script creation failed !\nfile not exist")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return
        
        scr_path.chmod(0o755)
        self.term_text.insertPlainText(f"script created.\n")

        short_path = Path(file_path) / "gpu_unlocker_shortcut.desktop"
        short_code = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=GPU Unlocker
GenericName=GPU Unlocker Toggle
Comment=GPU Unlocker Toggle Switch
Exec="{scr_path.resolve()}"
Icon=preferences-system
Terminal=true
Categories=Utility;System;
StartupNotify=false
"""
        short_path.write_text(data=short_code,encoding="utf-8")

        if not short_path.exists():
            self.is_running = False
            self.term_text.insertPlainText(f"shortcut creation failed !\nfile not exist")            
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return

        short_path.chmod(0o755)
        self.term_text.insertPlainText("shortcut created.")
        self.term_text.insertPlainText(f"\n--- Done (Code : 0) ---\nResult : Success")
        self.is_running=False    


    def on_install_cp(self):
        if (self.is_running):
            return
        
        if (not self.is_running):
            self.is_running = True
            self.term_text.setPlainText("~ >")

        self.process.start("pkexec",["bash",self.SCRIPT_FOLDER+"/corectrl.sh","install"])


    def create_profile(self):
        if (self.is_running):
                    return
                
        if (not self.is_running):
            self.is_running = True
            self.term_text.setPlainText("~ >")

        self.process.start("bash",[self.SCRIPT_FOLDER+"/corectrl.sh","profile"])

    def create_shortcut_cp(self):
        if (self.is_running):
            return
                        
        if (not self.is_running):
            self.is_running = True
            self.term_text.setPlainText(f"~ >\n")

        # if corectrl not installed
        if (not shutil.which("corectrl")):
            self.is_running=False
            self.term_text.insertPlainText(f"[corectrl] not installed !")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return

        # if profile-not-created
        config_dir = Path(os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config")
        profile_path = config_dir / "corectrl" / "profiles" / "_manual_GameMode.ccpro"
        if (not profile_path.exists()):
            self.is_running=False
            self.term_text.insertPlainText(f"profile [GameMode] not exist !")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return

        self.term_text.insertPlainText(f"Waiting for folder path...\n")

        # pick-folder
        file_path = QFileDialog.getExistingDirectory(
            self,"Select Folder",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
            )
        # not-null
        if (not file_path):
            self.is_running=False
            self.term_text.setPlainText(f"\nUser canceled.")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return

        # create-files
        scr_path = Path(file_path)/"cp_switch.sh"
        scr_code = """#!/bin/sh

app="corectrl"

if ! command -v "$app" >/dev/null 2>&1; then
    printf "%s is not installed!\n" "$app"
    exit 1
fi

profile_path="${XDG_CONFIG_HOME:-$HOME/.config}/corectrl/profiles/_manual_GameMode.ccpro"

if [ ! -f "$profile_path" ]; then
    printf "Profile does not exist!\nCreate one, then try again.\n"
    exit 1
fi

data_dir="${XDG_CACHE_HOME:-$HOME/.cache}/gpu_optimizer"
data_path="$data_dir/data"

#launch coectrl if it is closed
if ! pgrep -x "corectrl";then
    corectrl &

    counter=0
    while ! pgrep -x "corectrl" ;do

        sleep 1
        counter=$((counter+1))
        if [ "$counter" -gt 10 ];then
            notify-send "CoreCtrl Error !" "$app launch timed out !"
            exit 1
        fi

    done

    sleep 1

    if [ -f "$data_path" ];then
        rm -f "$data_path"
    fi

    exit 0

fi

if [ -f "$data_path" ]; then
    active=$(cat "$data_path")
else
    active="false"
fi

# Toggle state: if currently inactive ("false"), activate it; otherwise deactivate it
if [ "$active" = "false" ]; then
    corectrl --activate-manual-profile "GameMode"
    next_state="true"
    msg="on"
elif [ "$active" = "true" ]; then
    corectrl --deactivate-manual-profile "GameMode"
    next_state="false"
    msg="off"
else
    printf "Unknown state in %s!\n" "$data_path"
    next_state="false"
    msg="ignored!"
fi

# Persist the new state for the next toggle
mkdir -p "$data_dir"
printf "%s" "$next_state" > "$data_path"

# Send desktop notification if notify-send is available
if command -v notify-send >/dev/null 2>&1; then
    notify-send "GPU CP" "GameMode is $msg"
fi
"""

        scr_path.parent.mkdir(parents=True, exist_ok=True)
        scr_path.write_text(scr_code, encoding="utf-8")
        
        if (not scr_path.exists()):
            self.is_running=False
            self.term_text.insertPlainText("Failed to create Script !")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return
        
        scr_path.chmod(0o755)
        self.term_text.insertPlainText(f"\nScript created.")

        short_path= Path(file_path)/"Profile_Shortcut.desktop"
        short_code = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=GPU CP
GenericName=GPU Profile Toggle
Comment=Toggle CoreCtrl GameMode GPU profile
Exec="{scr_path.resolve()}"
Icon=preferences-system
Terminal=false
Categories=Utility;System;
StartupNotify=false
"""
        short_path.write_text(data=short_code,encoding="utf-8")
        
        if (not short_path.exists()):
            self.is_running = False
            self.term_text.insertPlainText("Failed to create shortcut !")
            self.term_text.insertPlainText(f"\n--- Done (Code : 1) ---\nResult : Failed")
            return
        
        short_path.chmod(0o755)
        self.term_text.insertPlainText(f"\nShortCut created.")
        self.term_text.insertPlainText(f"\n--- Done (Code : 0) ---\nResult : Success")
        self.is_running=False





# main function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Gui()
    window.setWindowTitle("GPU Optimizer")
    window.resize(600,420)
    window.show()
    sys.exit(app.exec())