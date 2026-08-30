import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_patrol_bot = get_package_share_directory('patrol_guard_bot')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_tb3_desc = get_package_share_directory('turtlebot3_description')

    world = os.path.join(pkg_patrol_bot, 'worlds', 'patrol_world.world')

    urdf_path = os.path.join(pkg_tb3_desc, 'urdf', 'turtlebot3_waffle.urdf')
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # Paths for Gazebo resources
    gazebo_model_path = os.path.join(pkg_tb3_gazebo, 'models')

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world, 'verbose': 'true'}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': robot_desc
        }]
    )

    spawn_turtlebot_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'turtlebot3_waffle',
            '-file', os.path.join(pkg_tb3_gazebo, 'models', 'turtlebot3_waffle', 'model.sdf'),
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.01'
        ],
        output='screen'
    )

    ld = LaunchDescription()

    # Essential Gazebo & rendering environment variables
    ld.add_action(SetEnvironmentVariable(name='TURTLEBOT3_MODEL', value='waffle'))
    ld.add_action(SetEnvironmentVariable(name='QT_QPA_PLATFORM', value='xcb'))
    ld.add_action(SetEnvironmentVariable(name='GAZEBO_RESOURCE_PATH', value='/usr/share/gazebo-11:/usr/share/gazebo'))
    ld.add_action(AppendEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=gazebo_model_path))

    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_turtlebot_cmd)

    return ld
