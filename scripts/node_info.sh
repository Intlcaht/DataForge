#!/bin/bash
###############################################################################
# Example Bash Script for Server Diagnostics
###############################################################################
#
# DESCRIPTION:
#   This script collects system information and diagnostic data from the server
#
# USAGE:
#   ./node_info.sh [output_dir] [collection_level]
#
#   Parameters:
#     output_dir      - Optional: Directory to save output files (default: current dir)
#     collection_level- Optional: Level of data to collect (basic, standard, detailed)
#                       default: standard
#
# EXAMPLES:
#   ./node_info.sh 
#   ./node_info.sh /tmp/diagnostics
#   ./node_info.sh /tmp/diagnostics detailed
#
###############################################################################

# Set strict error handling
set -e

# Handle script parameters
OUTPUT_DIR="${1:-$(pwd)}"
COLLECTION_LEVEL="${2:-standard}"

# Validate collection level
case "$COLLECTION_LEVEL" in
  basic|standard|detailed)
    echo "Collection level: $COLLECTION_LEVEL"
    ;;
  *)
    echo "Invalid collection level: $COLLECTION_LEVEL. Using 'standard'"
    COLLECTION_LEVEL="standard"
    ;;
esac

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"
echo "Output will be saved to: $OUTPUT_DIR"

# Add timestamp to filenames
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_PREFIX="${OUTPUT_DIR}/diag_${TIMESTAMP}"

# Print header
echo "======================================================="
echo "Server Diagnostic Collection"
echo "Started at: $(date)"
echo "Hostname: $(hostname)"
echo "Collection Level: $COLLECTION_LEVEL"
echo "======================================================="

# Basic system information - collected at all levels
collect_basic_info() {
  echo "Collecting basic system information..."
  
  # OS details
  echo "Operating System Information:" > "${OUTPUT_PREFIX}_os_info.txt"
  uname -a >> "${OUTPUT_PREFIX}_os_info.txt"
  cat /etc/os-release >> "${OUTPUT_PREFIX}_os_info.txt" 2>/dev/null || echo "No OS release file found" >> "${OUTPUT_PREFIX}_os_info.txt"
  
  # CPU information
  echo "CPU Information:" > "${OUTPUT_PREFIX}_cpu_info.txt"
  lscpu >> "${OUTPUT_PREFIX}_cpu_info.txt" 2>/dev/null || echo "lscpu not available" >> "${OUTPUT_PREFIX}_cpu_info.txt"
  
  # Memory information
  echo "Memory Information:" > "${OUTPUT_PREFIX}_memory_info.txt"
  free -h >> "${OUTPUT_PREFIX}_memory_info.txt"
  
  # Disk usage
  echo "Disk Usage:" > "${OUTPUT_PREFIX}_disk_usage.txt"
  df -h >> "${OUTPUT_PREFIX}_disk_usage.txt"
  
  echo "Basic information collection complete."
}

# Standard system details - collected at standard and detailed levels
collect_standard_info() {
  echo "Collecting standard system information..."
  
  # Network configuration
  echo "Network Configuration:" > "${OUTPUT_PREFIX}_network_config.txt"
  ip addr >> "${OUTPUT_PREFIX}_network_config.txt" 2>/dev/null || ifconfig >> "${OUTPUT_PREFIX}_network_config.txt" 2>/dev/null || echo "No network tools available" >> "${OUTPUT_PREFIX}_network_config.txt"
  
  # Routing table
  echo "Routing Table:" > "${OUTPUT_PREFIX}_routing.txt"
  ip route >> "${OUTPUT_PREFIX}_routing.txt" 2>/dev/null || route -n >> "${OUTPUT_PREFIX}_routing.txt" 2>/dev/null || echo "No routing tools available" >> "${OUTPUT_PREFIX}_routing.txt"
  
  # Process list
  echo "Running Processes:" > "${OUTPUT_PREFIX}_processes.txt"
  ps aux >> "${OUTPUT_PREFIX}_processes.txt"
  
  # Service status
  echo "Service Status:" > "${OUTPUT_PREFIX}_services.txt"
  systemctl list-units --type=service >> "${OUTPUT_PREFIX}_services.txt" 2>/dev/null || service --status-all >> "${OUTPUT_PREFIX}_services.txt" 2>/dev/null || echo "No service manager found" >> "${OUTPUT_PREFIX}_services.txt"
  
  # Check for Docker
  echo "Docker Information:" > "${OUTPUT_PREFIX}_docker.txt"
  if command -v docker &> /dev/null; then
    docker info >> "${OUTPUT_PREFIX}_docker.txt"
    docker ps -a >> "${OUTPUT_PREFIX}_docker.txt"
  else
    echo "Docker not installed" >> "${OUTPUT_PREFIX}_docker.txt"
  fi
  
  echo "Standard information collection complete."
}

# Detailed system analysis - collected only at detailed level
collect_detailed_info() {
  echo "Collecting detailed system information..."
  
  # System logs
  echo "System Logs (last 100 lines):" > "${OUTPUT_PREFIX}_syslog.txt"
  tail -n 100 /var/log/syslog >> "${OUTPUT_PREFIX}_syslog.txt" 2>/dev/null || tail -n 100 /var/log/messages >> "${OUTPUT_PREFIX}_syslog.txt" 2>/dev/null || echo "No system logs accessible" >> "${OUTPUT_PREFIX}_syslog.txt"
  
  # Find largest files
  echo "Top 20 Largest Files in /var:" > "${OUTPUT_PREFIX}_large_files.txt"
  find /var -type f -exec du -Sh {} \; 2>/dev/null | sort -rh | head -n 20 >> "${OUTPUT_PREFIX}_large_files.txt" || echo "Error finding large files" >> "${OUTPUT_PREFIX}_large_files.txt"
  
  # Installed packages
  echo "Installed Packages:" > "${OUTPUT_PREFIX}_packages.txt"
  if command -v dpkg &> /dev/null; then
    dpkg -l >> "${OUTPUT_PREFIX}_packages.txt"
  elif command -v rpm &> /dev/null; then
    rpm -qa >> "${OUTPUT_PREFIX}_packages.txt"
  else
    echo "No package manager found" >> "${OUTPUT_PREFIX}_packages.txt"
  fi
  
  # Real-time stats for 5 seconds
  echo "Collecting real-time statistics for 5 seconds..."
  echo "Top Processes by CPU/Memory:" > "${OUTPUT_PREFIX}_top.txt"
  top -b -n 5 -d 1 >> "${OUTPUT_PREFIX}_top.txt"
  
  # Check for K3s if exists
  if command -v kubectl &> /dev/null; then
    echo "Kubernetes Information:" > "${OUTPUT_PREFIX}_kubernetes.txt"
    kubectl get nodes -o wide >> "${OUTPUT_PREFIX}_kubernetes.txt" 2>/dev/null || echo "Error accessing Kubernetes" >> "${OUTPUT_PREFIX}_kubernetes.txt"
    kubectl get pods --all-namespaces >> "${OUTPUT_PREFIX}_kubernetes.txt" 2>/dev/null
  fi
  
  echo "Detailed information collection complete."
}

# Execute collections based on the specified level
collect_basic_info

if [[ "$COLLECTION_LEVEL" == "standard" || "$COLLECTION_LEVEL" == "detailed" ]]; then
  collect_standard_info
fi

if [[ "$COLLECTION_LEVEL" == "detailed" ]]; then
  collect_detailed_info
fi

# Create archive of all output files
echo "Creating diagnostic archive..."
tar -czf "${OUTPUT_DIR}/node_info_${TIMESTAMP}.tar.gz" "${OUTPUT_PREFIX}"*

# Summary
echo "======================================================="
echo "Diagnostic collection completed successfully."
echo "Results saved to: ${OUTPUT_DIR}/node_info_${TIMESTAMP}.tar.gz"
echo "Completed at: $(date)"
echo "======================================================="

# Return success
exit 0