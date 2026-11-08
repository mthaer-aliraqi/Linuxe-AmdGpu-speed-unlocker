# 🚀 Linuxe-AmdGpu-force-high-performance for Hybrid Linux Laptops 

## usage (summary) the thing u need in simple words
-
-   you need to download 'gpu-speed-unlocker.sh' and then make it excutable then go to desktop > R Click Mouse > create_new > link_to_application
-   in application tab > program > Browse , then select your file make sure to activate run_in_terminal  
-   and that's run it your gpu speed unlocked.
-   to restore normal state just run the script again it will be disable
-   and if u did reboot your laptop the default settings 'd be restored  

### this method is safe and it runs on my laptop without issues.
### However in case your device [laptop,pc,etc...] get corrupted or crashed or damaged i am not responsible at all
## you do it at your own risk.

## 📌 Executive Summary

On hybrid graphics laptops (e.g., **Intel iGPU + AMD dGPU** such as Radeon R7 M365X / Opal XT / GCN architectures), the Linux kernel's default power management aggressively downclocks or completely powers off discrete GPUs when not rendering active desktop displays.

This automated Bash script dynamically locates your discrete AMD GPU on the PCIe bus and overrides kernel power throttling. It prevents forced $D3_{cold}$ **deep sleep** states and locks core/memory clocks to maximum performance during gaming sessions.

## 💡 The Problem vs. The Solution

### ⚠️ The Problem (Default Kernel Behavior)

```
┌─────────────────┐       Idle Detect       ┌──────────────────────┐
│  Intel iGPU     │ ──────────────────────> │ AMD dGPU (Disabling) │
│ (Active Display)│                         └──────────┬───────────┘
└─────────────────┘                                    │
                                                       ▼
                                            ┌──────────────────────┐
                                            │ Forced D3cold Sleep  │
                                            │ Clocks locked at:    │
                                            │ 300MHz / 400MHz      │
                                            └──────────────────────┘

```

1. **Aggressive Runtime PM:** The kernel detects no direct display connected to the AMD card and marks it as suspended.

2. **PCIe** $D3_{cold}$ **Sleep:** Power is physically cut off from the PCIe slot to conserve battery.

3. **Throttling Lockup:** When games start, the card fails to ramp up frequencies, leaving it trapped at **300MHz - 400MHz**.

4. **CoreCtrl Limits:** Manual software sliders (like CoreCtrl) fail because the underlying sysfs power states override user preferences.

### ✅ The Solution (Our Kernel Bypass Script)

```
┌───────────────────────────┐      Disable PM       ┌───────────────────────────────┐
│     amd-autohigh Script   │ ────────────────────> │  sysfs Kernel Controls        │
└───────────────────────────┘                       └──────────────┬────────────────┘
                                                                   │
                                                                   ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  [1] power/control -> "on"         (Prevents Runtime Suspend)                    │
│  [2] d3cold_allowed -> "0"        (Blocks D3cold Deep Power Cutoff)             │
│  [3] force_performance -> "high"  (Locks Clocks to Max Factory Frequencies)      │
└──────────────────────────────────────────────────────────────────────────────────┘
                                                                   │
                                                                   ▼
                                                    ┌───────────────────────────────┐
                                                    │ AMD dGPU Maximum Performance  │
                                                    │ Full Clocks (e.g. 900MHz+)    │
                                                    └───────────────────────────────┘

```

## 🔬 How Each Command Works (Detailed Breakdown)

The script executes three critical kernel-level interventions dynamically:

### 1️⃣ Dynamic Bus Identification

```
AMD_PCI_BUS=$(basename $(readlink -f /sys/bus/pci/drivers/amdgpu/0000:* 2>/dev/null | head -n 1))

```

> **What it does:** Automatically queries the `/sys/bus/pci/drivers/amdgpu` driver path to discover the GPU's hardware address (e.g., `0000:03:00.0`). **Why it matters:** Removes the need to hardcode bus IDs, ensuring portability across different laptops, kernel updates, or PCI reconfigurations.

### 2️⃣ Disabling Kernel Runtime Suspend

```
echo "on" | tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power/control"

```

> **What it does:** Changes the power mode from `auto` to `on`. **Why it matters:** Disables **PCI Runtime Power Management**, preventing the Linux kernel from marking the dGPU as "idle" during game loading screens or brief rendering pauses.

### 3️⃣ Blocking $D3_{cold}$ Deep Sleep States

```
echo "0" | tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/d3cold_allowed"

```

> **What it does:** Writes `0` (disabled) to the ACPI power state policy. **Why it matters:** Completely stops the motherboard from cutting voltage to the PCIe slot. The hardware remains energized and instantly responsive.

### 4️⃣ Forcing Peak Factory Clocks

```
echo "high" | tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power_dpm_force_performance_level"

```

> **What it does:** Overrides default **Dynamic Power Management (DPM)** to force the `high` profile. **Why it matters:** Instructs the `amdgpu` driver to lock core clock (GCLK) and memory clock (MCLK) to maximum limits.

## ⚙️ Installation & Usage Guide

### Step 1: Install the Script

Run the following block in your terminal to automatically generate the script in system binaries:

```
sudo tee /usr/local/bin/amd-autohigh > /dev/null << 'EOF'
#!/bin/bash
# Automatically locate the discrete AMD GPU
AMD_PCI_BUS=$(basename $(readlink -f /sys/bus/pci/drivers/amdgpu/0000:* 2>/dev/null | head -n 1))

if [ -z "$AMD_PCI_BUS" ]; then
    echo "❌ Error: Could not detect an active AMD GPU bound to 'amdgpu'."
    exit 1
fi

echo "🔍 Found AMD GPU at PCI Address: ${AMD_PCI_BUS}"

# Apply power management overrides
echo "on" | tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power/control" > /dev/null
echo "0" | tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/d3cold_allowed" > /dev/null
echo "high" | tee "/sys/bus/pci/devices/${AMD_PCI_BUS}/power_dpm_force_performance_level" > /dev/null

echo "🚀 AMD GPU (${AMD_PCI_BUS}) locked to MAXIMUM performance!"
EOF

# Make executable
sudo chmod +x /usr/local/bin/amd-autohigh

```

### Step 2: Run Before Gaming

Whenever you plan to play games, simply run:

```
sudo amd-autohigh

```

### Step 3: Steam Game Launch Options

To ensure your games are offloaded to the AMD dGPU instead of running on the Intel iGPU, set your **Steam Launch Options** (Right-Click Game ➔ Properties ➔ General ➔ Launch Options):

#### Standard OpenGL / Generic Offloading:

```
DRI_PRIME=1 %command%

```

#### Vulkan Games (Forcing Radeon ICD):

```
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json DRI_PRIME=1 %command%

```

## ⏱️ When Do Settings Reset?

> ℹ️ **Kernel Memory Behavior:** All modifications performed by this script are applied directly to **volatile kernel interfaces (`sysfs` in RAM)**.

| Event | Status | Explanation | 
| ----- | ----- | ----- | 
| **System Reboot / Shutdown** | 🔄 **Resets to Default** | The kernel restores default energy-saving modes (`auto` and `D3cold allowed`) to preserve battery life. | 
| **Suspending / Sleep** | 🔄 **Resets to Default** | Power management re-initializes PCI states upon waking up. | 
| **Closing a Game** | 🔒 **Stays High** | Settings remain locked until a reboot or manual reset. | 

*(To revert back to power-saving mode manually without rebooting, run: `echo "auto" | sudo tee /sys/bus/pci/devices/0000:03:00.0/power_dpm_force_performance_level`)*

## 🐧 Linux Distribution Compatibility

This script is **100% universal** and works out-of-the-box on virtually all desktop Linux distributions:

* 🟢 **Arch Linux / CachyOS / Manjaro**

* 🟠 **Ubuntu / Linux Mint / Pop!\_OS**

* 🔴 **Fedora / Nobara**

* 🔵 **Debian / openSUSE**

### Prerequisites:

1. Kernel `sysfs` tree support (standard in all modern Linux kernels).

2. The open-source `amdgpu` driver enabled for your graphics card.
