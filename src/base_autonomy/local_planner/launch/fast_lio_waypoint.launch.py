import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


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
  useTerrainAnalysis = LaunchConfiguration('useTerrainAnalysis')
  fastLioBodyFrame = LaunchConfiguration('fastLioBodyFrame')

  declare_world_name = DeclareLaunchArgument('world_name', default_value='real_world', description='')
  declare_fast_lio_odom_topic = DeclareLaunchArgument('fast_lio_odom_topic', default_value='/Odometry', description='')
  declare_fast_lio_cloud_topic = DeclareLaunchArgument('fast_lio_cloud_topic', default_value='/cloud_registered', description='')
  declare_cameraOffsetZ = DeclareLaunchArgument('cameraOffsetZ', default_value='0.25', description='')
  declare_sensorOffsetX = DeclareLaunchArgument('sensorOffsetX', default_value='0.0', description='')
  declare_sensorOffsetY = DeclareLaunchArgument('sensorOffsetY', default_value='0.0', description='')
  declare_checkTerrainConn = DeclareLaunchArgument('checkTerrainConn', default_value='true', description='')
  declare_realRobot = DeclareLaunchArgument('realRobot', default_value='false', description='')
  declare_useJoy = DeclareLaunchArgument('useJoy', default_value='false', description='')
  declare_useTerrainAnalysis = DeclareLaunchArgument('useTerrainAnalysis', default_value='false', description='')
  declare_fastLioBodyFrame = DeclareLaunchArgument('fastLioBodyFrame', default_value='body', description='FAST-LIO body frame that coincides with the stack sensor frame')

  start_local_planner = IncludeLaunchDescription(
    FrontendLaunchDescriptionSource(os.path.join(
      get_package_share_directory('local_planner'), 'launch', 'local_planner.launch')
    ),
    launch_arguments={
      'realRobot': realRobot,
      'sensorOffsetX': sensorOffsetX,
      'sensorOffsetY': sensorOffsetY,
      'cameraOffsetZ': cameraOffsetZ,
      'useTerrainAnalysis': useTerrainAnalysis,
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

  start_fast_lio_topic_bridge = Node(
    package='local_planner',
    executable='fastLioTopicBridge',
    name='fastLioTopicBridge',
    output='screen',
    parameters=[{
      'input_odom_topic': fast_lio_odom_topic,
      'input_cloud_topic': fast_lio_cloud_topic,
      'output_odom_topic': '/state_estimation',
      'output_cloud_topic': '/registered_scan',
    }]
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

  # FAST-LIO publishes map -> camera_init -> body, while the autonomy stack keeps
  # sensor -> vehicle / camera. The stack's sensor frame coincides with FAST-LIO's
  # body frame (both are the pose reported on /Odometry), so this identity link
  # joins the two TF trees and lets vehicle-frame topics (e.g. /free_paths, /path)
  # be displayed and planned against.
  start_body_to_sensor_tf = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='fastLioBodyToSensorTransPublisher',
    output='screen',
    arguments=[
      '--x', '0', '--y', '0', '--z', '0',
      '--roll', '0', '--pitch', '0', '--yaw', '0',
      '--frame-id', fastLioBodyFrame, '--child-frame-id', 'sensor',
    ],
  )

  waypoint_stack = GroupAction([
    start_fast_lio_topic_bridge,
    start_body_to_sensor_tf,
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
    declare_useTerrainAnalysis,
    declare_fastLioBodyFrame,
    waypoint_stack,
  ])
