#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd $SCRIPT_DIR
source ./install/setup.bash
ros2 launch local_planner fast_lio_waypoint.launch.py &
sleep 1
ros2 run rviz2 rviz2 -d src/base_autonomy/local_planner/rviz/real_robot.rviz
