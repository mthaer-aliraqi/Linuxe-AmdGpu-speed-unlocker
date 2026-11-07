#!/bin/bash

# Dynamically find the PCI bus address of the discrete AMD GPU managed by amdgpu
# (Matches entries like 0000:03:00.0 from /sys/bus/pci/drivers/amdgpu)
AMD_PCI_BUS=$(basename $(readlink -f /sys/bus/pci/drivers/amdgpu/0000:* 2>/dev/null | head -n 1))

# Check if an AMD GPU was successfully detected
if [ -z "$AMD_PCI_BUS" ]; then
echo "Error: Could not automatically detect an active AMD GPU bound to 'amdgpu'."
exit 1
fi

echo "Found AMD GPU at PCI Address: ${AMD_PCI_BUS}"

# Prevent runtime auto-suspend / sleep mode
echo "on" |sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power/control"

# Block D3cold deep power-saving state (power cutoff)
echo "0" |sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/d3cold_allowed"

# Lock driver DPM performance level to maximum
echo "high" |sudo tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power_dpm_force_performance_level"

echo "AMD GPU at ${AMD_PCI_BUS} successfully locked to maximum performance!"
