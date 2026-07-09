import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap


def generate_launch_description():
  world_name = LaunchConfiguration('world_name')
  fast_lio_odom_topic = LaunchConfiguration('fast_lio_odom_topic')
  fast_lio_cloud_topic = LaunchConfiguration('fast_lio_cloud_topic')
  cameraOffsetZ = LaunchConfiguration('cameraOffsetZ')
  sensorOffsetX = LaunchConfiguration('sensorOffsetX')
  sensorOffsetY = LaunchConfiguration('sensorOffsetY')
  checkTerrainConn = LaunchConfiguration('checkTerrainConn')
  realRobot = LaunchConfiguration('realRobot')
  useJoy = LaunchConfiguration('useJoy')

  declare_world_name = DeclareLaunchArgument('world_name', default_value='real_world', description='')
  declare_fast_lio_odom_topic = DeclareLaunchArgument('fast_lio_odom_topic', default_value='/Odometry', description='')
  declare_fast_lio_cloud_topic = DeclareLaunchArgument('fast_lio_cloud_topic', default_value='/cloud_registered', description='')
  declare_cameraOffsetZ = DeclareLaunchArgument('cameraOffsetZ', default_value='0.25', description='')
  declare_sensorOffsetX = DeclareLaunchArgument('sensorOffsetX', default_value='0.0', description='')
  declare_sensorOffsetY = DeclareLaunchArgument('sensorOffsetY', default_value='0.0', description='')
  declare_checkTerrainConn = DeclareLaunchArgument('checkTerrainConn', default_value='true', description='')
  declare_realRobot = DeclareLaunchArgument('realRobot', default_value='false', description='')
  declare_useJoy = DeclareLaunchArgument('useJoy', default_value='false', description='')

  start_local_planner = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('local_planner'), 'launch', 'local_planner.launch')
    ),
    launch_arguments={
      'realRobot': realRobot,
      'sensorOffsetX': sensorOffsetX,
      'sensorOffsetY': sensorOffsetY,
      'cameraOffsetZ': cameraOffsetZ,
      'goalX': '0.0',
      'goalY': '0.0',
    }.items()
  )

  start_terrain_analysis = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('terrain_analysis'), 'launch', 'terrain_analysis.launch')
    )
  )

  start_terrain_analysis_ext = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('terrain_analysis_ext'), 'launch', 'terrain_analysis_ext.launch')
    ),
    launch_arguments={
      'checkTerrainConn': checkTerrainConn,
    }.items()
  )

  start_sensor_scan_generation = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('sensor_scan_generation'), 'launch', 'sensor_scan_generation.launch')
    )
  )

  start_visualization_tools = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('visualization_tools'), 'launch', 'visualization_tools.launch')
    ),
    launch_arguments={
      'world_name': world_name,
    }.items()
  )

  start_joy = Node(
    package='joy',
    executable='joy_node',
    name='ps3_joy',
    output='screen',
    condition=IfCondition(useJoy),
    parameters=[{
      'dev': '/dev/input/js0',
      'deadzone': 0.12,
      'autorepeat_rate': 0.0,
    }]
  )

  waypoint_stack = GroupAction([
    SetRemap(src='/state_estimation', dst=fast_lio_odom_topic),
    SetRemap(src='/registered_scan', dst=fast_lio_cloud_topic),
    start_local_planner,
    start_terrain_analysis,
    start_terrain_analysis_ext,
    start_sensor_scan_generation,
    start_visualization_tools,
    start_joy,
  ])

  return LaunchDescription([
    declare_world_name,
    declare_fast_lio_odom_topic,
    declare_fast_lio_cloud_topic,
    declare_cameraOffsetZ,
    declare_sensorOffsetX,
    declare_sensorOffsetY,
    declare_checkTerrainConn,
    declare_realRobot,
    declare_useJoy,
    waypoint_stack,
  ])
