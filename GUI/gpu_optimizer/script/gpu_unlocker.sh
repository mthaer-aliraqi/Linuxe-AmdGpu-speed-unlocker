#!/bin/bash

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
    # && \ added to block next operations if this operation failed , it des the same as in lock_gpu function if [ $? -en 0 ]...
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

# 3. State management file

active="$1"
cache_dir="$2"

case "$active" in
    on|off) ;;
    *) echo "err: invalid state '$active' (use on|off)" >&2; exit 1 ;;
esac

if [ -z "$cache_dir" ]; then
    echo "err: cache directory argument missing" >&2
    exit 1
fi
cache_data="$cache_dir/unlocker_switch"

if [ "$active" = "off" ]; then
    if ! lock_gpu; then
        echo "err: failed to lock gpu !"
        exit 1
    fi
    echo "gpu unlocker is off"
else
    if ! unlock_gpu; then
        echo "err: failed to unlock gpu !"
        exit 1
    fi
    echo "gpu unlocker is on"
fi

# save state, then give the files back to the real user (script runs as root via pkexec)
mkdir -p "$cache_dir" || exit 1
echo "$active" > "$cache_data" || exit 1

if [ -n "$PKEXEC_UID" ]; then
    chown "$PKEXEC_UID" "$cache_dir" "$cache_data" \
        || echo "warn: could not change owner of state file" >&2
fi