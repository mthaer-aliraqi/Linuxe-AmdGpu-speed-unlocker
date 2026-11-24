#!/bin/sh

option="$1"
app="corectrl"
corectrl_folder="${XDG_CONFIG_HOME:-$HOME/.config}/corectrl"
gpu_optimizer_path="$(dirname "$0")"
assets_dir="$(dirname "$gpu_optimizer_path")/assets"

is_installed(){
    command -v "$1" >/dev/null
}

install_pkg(){
    
    if ! is_installed "$app";then
        echo "Installing ${app}..."

        if is_installed "pacman" ; then
            sudo pacman -S --needed --noconfirm "$app"
        elif is_installed "apt-get" ;then
            sudo apt-get update && sudo apt-get install -y "$app"
        elif is_installed "dnf";then
            sudo dnf install -y "$app"
        elif is_installed "zypper"; then
            sudo zypper --non-interactive install "$app"
        else
            echo "Unsupported package manager !"
            return 1
        fi
    else
        echo "$app is already installed."
        return 0
    fi

}

create_profile(){

    if [ ! -f "$assets_dir/_manual_GameMode.ccpro" ];then
        echo "Source file not found !"
        return 1
    fi

    echo "creating profile..."
    mkdir -p "${corectrl_folder}/profiles/"
    cp "$assets_dir/_manual_GameMode.ccpro" "$corectrl_folder/profiles/"
    
    if [ -f "$corectrl_folder/profiles/_manual_GameMode.ccpro" ] >/dev/null;then
        echo "Profile Created."
        return 0
    else
        echo "Failed to create GameMode profile !"
        return 1
    fi
}

case "$option" in
    "install")
        install_pkg
        exit $?
        ;;
    "profile")
        create_profile
        exit $?
        ;;
    *)
        echo "Error: Option '${option}' does not exist! Use: install | profile | shortcut" >&2
        exit 1
        ;;
esac