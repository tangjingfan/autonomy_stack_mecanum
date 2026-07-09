#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"
source /opt/ros/humble/setup.bash
source /home/nvidia/Desktop/sdk/install/setup.bash

ros2 launch local_planner fast_lio_waypoint.launch.py &
sleep 1

export QT_X11_NO_MITSHM=1
if [ "${RVIZ_SOFTWARE_RENDERING:-false}" = "true" ]; then
  export LIBGL_ALWAYS_SOFTWARE=1
fi

ros2 run rviz2 rviz2 -d src/base_autonomy/vehicle_simulator/rviz/vehicle_simulator.rviz
