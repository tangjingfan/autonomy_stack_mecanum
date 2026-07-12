#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"
source /opt/ros/humble/setup.bash
source /home/nvidia/Desktop/sdk/install/setup.bash
source ./install/setup.bash

# Record everything needed to replay the GO2 / FAST-LIO waypoint stack offline:
# raw Mid360 sensor, FAST-LIO outputs, autonomy I/O and TF. This only records --
# run FAST-LIO and the waypoint stack (e.g. ./system_fast_lio_waypoint.sh) in
# another terminal first. Pass an output path as $1, otherwise a timestamped
# folder under ./bags is used.

BAG_DIR="${1:-bags/go2_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$(dirname "$BAG_DIR")"

ros2 bag record -o "$BAG_DIR" \
  /livox/lidar \
  /livox/imu \
  /Odometry \
  /cloud_registered \
  /state_estimation \
  /registered_scan \
  /terrain_map \
  /way_point \
  /free_paths \
  /path \
  /tf \
  /tf_static
