import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_patrol_bot = get_package_share_directory('patrol_guard_bot')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_yaml_file = os.path.join(pkg_patrol_bot, 'maps', 'patrol_map.yaml')
    nav2_params_file = os.path.join(pkg_patrol_bot, 'config', 'nav2_params.yaml')

    # Static transform for LiDAR frame
    static_tf_pub = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_base_scan',
        arguments=['-0.064', '0', '0.122', '0', '0', '0', 'base_footprint', 'base_scan'],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # RTAB-Map in Pure Localization Mode (Read-Only)
    rtabmap_parameters = [{
        'frame_id': 'base_footprint',
        'odom_frame_id': 'odom',
        'map_frame_id': 'map',
        'use_sim_time': use_sim_time,
        'subscribe_depth': False,
        'subscribe_rgb': False,
        'subscribe_scan': True,
        'approx_sync': True,
        'sync_queue_size': 20,
        'publish_tf': True,
        'wait_for_transform': 0.5,
        'Mem/IncrementalMemory': 'false',
        'Mem/InitWMWithAllNodes': 'true',
        'Reg/Strategy': '1',
        'Reg/Force3DoF': 'true',
        'RGBD/NeighborLinkRefining': 'true',
        'RGBD/ProximityBySpace': 'true',
    }]

    rtabmap_remappings = [
        ('scan', '/scan'),
        ('odom', '/odom'),
        ('grid_map', '/map')
    ]

    rtabmap_localization_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=rtabmap_parameters,
        remappings=rtabmap_remappings,
        arguments=[]
    )

    rtabmap_viz_node = Node(
        package='rtabmap_viz',
        executable='rtabmap_viz',
        name='rtabmap_viz',
        output='screen',
        parameters=rtabmap_parameters,
        remappings=rtabmap_remappings
    )

    # Map Server & Lifecycle Manager for Map
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'yaml_filename': map_yaml_file
        }]
    )

    lifecycle_nodes = ['map_server', 'planner_server', 'controller_server', 'recoveries_server', 'bt_navigator']

    # Nav2 Navigation (Path Planning, Controller, Costmaps, Recoveries)
    nav2_navigation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
            'autostart': 'true'
        }.items()
    )

    # Lifecycle Manager to activate Map Server along with Navigation nodes
    map_lifecycle_mgr = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map_server',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server']
        }]
    )

    # RViz2 with Nav2 configuration
    rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'rviz_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    ld = LaunchDescription()
    ld.add_action(DeclareLaunchArgument('use_sim_time', default_value='true'))
    ld.add_action(static_tf_pub)
    ld.add_action(rtabmap_localization_node)
    ld.add_action(rtabmap_viz_node)
    ld.add_action(map_server_node)
    ld.add_action(map_lifecycle_mgr)
    ld.add_action(nav2_navigation_cmd)
    ld.add_action(rviz_cmd)

    return ld
