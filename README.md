# GO2 Waypoint Follower Stack

This branch is a cleaned Humble-compatible waypoint follower setup. The original SLAM module, route planner, and exploration planner have been removed. Use FAST_LIO_GPU as the external SLAM/odometry source, and run this stack for terrain analysis, collision-aware local planning, waypoint following, RViz waypoint control, and `/cmd_vel` output.

## Expected FAST_LIO_GPU Topics

By default, the launch file expects FAST_LIO_GPU to publish:

```bash
/Odometry
/cloud_registered
```

The stack republishes those into the original autonomy-stack topic names:

```bash
/state_estimation
/registered_scan
```

If your FAST_LIO_GPU topics are different, pass them as launch arguments.

## Build

Source ROS 2 Humble, then build only the packages needed for waypoint following:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release \
  --packages-up-to local_planner terrain_analysis terrain_analysis_ext \
  sensor_scan_generation visualization_tools waypoint_rviz_plugin teleop_rviz_plugin
```

## Run With FAST_LIO_GPU

Start FAST_LIO_GPU first. Then run:

```bash
./system_fast_lio_waypoint.sh
```

Or launch directly:

```bash
source install/setup.bash
ros2 launch local_planner fast_lio_waypoint.launch.py
```

With custom FAST_LIO_GPU topic names:

```bash
ros2 launch local_planner fast_lio_waypoint.launch.py \
  fast_lio_odom_topic:=/your_odom_topic \
  fast_lio_cloud_topic:=/your_cloud_topic
```

## Outputs

The path follower publishes:

```bash
/cmd_vel
```

The default FAST_LIO launch keeps `realRobot:=false`, so it does not open the original serial motor-controller interface. This is usually what you want when another GO2/base controller consumes `/cmd_vel`.

To enable the original serial output path:

```bash
ros2 launch local_planner fast_lio_waypoint.launch.py realRobot:=true
```

## Main Packages Kept

- `local_planner`: local planning and path following
- `terrain_analysis`, `terrain_analysis_ext`: terrain/collision map generation
- `sensor_scan_generation`: converts registered map cloud into the sensor frame
- `visualization_tools`: RViz visualization helpers
- `waypoint_rviz_plugin`: RViz waypoint tool
- `teleop_rviz_plugin`: RViz control panel

## Removed From This Branch

- `src/slam`
- `src/route_planner`
- `src/exploration_planner`
- `vehicle_simulator` and the Unity simulation
- `ros_tcp_endpoint` (Unity TCP bridge)
- `waypoint_example` (preset waypoint sender)
- `teleop_joy_controller` (mecanum serial base teleop)
- route/exploration startup scripts and desktop launchers
- route planner goalpoint RViz plugin
