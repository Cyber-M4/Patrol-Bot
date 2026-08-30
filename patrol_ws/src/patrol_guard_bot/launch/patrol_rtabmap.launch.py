import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    parameters = [{
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
        'Reg/Strategy': '1',             # ICP scan matching
        'Reg/Force3DoF': 'true',         # 2D plane
        'RGBD/ProximityBySpace': 'true',
        'RGBD/AngularUpdate': '0.05',
        'RGBD/LinearUpdate': '0.05',
        'Grid/RangeMax': '5.0',
        'Grid/RayTracing': 'true',
        'Grid/CellSize': '0.05',
    }]

    remappings = [
        ('scan', '/scan'),
        ('odom', '/odom'),
        ('grid_map', '/map')
    ]

    # Static transform to guarantee base_footprint -> base_scan lookup never fails
    static_tf_pub = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_base_scan',
        arguments=['-0.064', '0', '0.122', '0', '0', '0', 'base_footprint', 'base_scan'],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # RTAB-Map SLAM Node
    rtabmap_slam_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=parameters,
        remappings=remappings,
        arguments=['-d']
    )

    # RTAB-Map GUI visualizer
    rtabmap_viz_node = Node(
        package='rtabmap_viz',
        executable='rtabmap_viz',
        name='rtabmap_viz',
        output='screen',
        parameters=parameters,
        remappings=remappings
    )

    ld = LaunchDescription()
    ld.add_action(DeclareLaunchArgument('use_sim_time', default_value='true'))
    ld.add_action(static_tf_pub)
    ld.add_action(rtabmap_slam_node)
    ld.add_action(rtabmap_viz_node)

    return ld
