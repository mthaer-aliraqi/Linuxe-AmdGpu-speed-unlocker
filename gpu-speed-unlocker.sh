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
    if [ $? -en 0 ]; then
        return 1
    fi

    # another way but more easier
    if ! echo "1" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/d3cold_allowed" &>/dev/null; then
        exit 1
    fi

    echo "auto" | sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power/control" &>/dev/null
    return $?

}

# 3. State management file
stateFile="/tmp/gpu-unlocker-state"

if [ -f "$stateFile" ]; then
    active=$(cat "$stateFile")
else
    active="off"
fi

# 4. Toggle state & apply settings , but if function catched errors close all
if [ "$active" = "on" ]; then
    if ! lock_gpu; then
        exit 1
    fi
        active="off"
else
    if ! unlock_gpu;then
        exit 1
    fi
    active="on"
fi

# Persist new state to disk
echo "$active" > "$stateFile"

# 5. Notify user of status
notify-send "GPU Unlocker" "GPU unlocker is now $active"
