import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_senti = get_package_share_directory('senti_v')
    pkg_rtabmap = get_package_share_directory('rtabmap_launch')

    world_path = os.path.join(pkg_senti, 'worlds', 'warehouse_light.world')
    urdf_path = os.path.join(pkg_senti, 'urdf', 'senti_v_waffle.urdf')

    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        # --- Rendering fixes: Nvidia GPU on 'nouveau' driver causes SIGABRT
        # crashes in Gazebo's OGRE renderer. Software rendering + explicit
        # GL version overrides are both required together. ---
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        SetEnvironmentVariable('MESA_GL_VERSION_OVERRIDE', '3.3'),
        SetEnvironmentVariable('MESA_GLSL_VERSION_OVERRIDE', '330'),
        SetEnvironmentVariable('QT_X11_NO_MITSHM', '1'),

        # --- Offline-first: never attempt to fetch models from Gazebo's
        # online Fuel database (avoids indefinite hangs). ---
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        SetEnvironmentVariable(
            'GAZEBO_MODEL_PATH',
            os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'models')
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={'world': world_path, 'gui': 'true'}.items(),
        ),

        # --- Publishes our MODIFIED urdf (with camera sensor plugin added -
        # stock TurtleBot3 Waffle has NO camera sensor, only cosmetic mesh
        # geometry, which is why /camera/image_raw never published on the
        # stock file no matter what rendering fixes were applied). ---
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': True, 'robot_description': robot_description}],
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'senti_v', '-topic', 'robot_description',
                       '-x', '-2.0', '-y', '-0.5', '-z', '0.01'],
            output='screen',
        ),

        Node(
            package='senti_v',
            executable='senti_perception_executable',
            output='screen',
        ),

        # --- Visual-Inertial odometry: mono camera + IMU, NOT RGB-D.
        # TurtleBot3 Waffle has no reliable depth topic, so subscribe_depth
        # must stay false. imu_topic + wait_imu_to_init give genuine VIO. ---
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_rtabmap, 'launch', 'rtabmap.launch.py')
            ),
            launch_arguments={
                'rtabmap_args': '--delete_db_on_start',
                'rgb_topic': '/camera/image_raw',
                'camera_info_topic': '/camera/camera_info',
                'subscribe_depth': 'false',
                'subscribe_rgbd': 'false',
                'imu_topic': '/imu',
                'wait_imu_to_init': 'true',
                'frame_id': 'base_footprint',
                'approx_sync': 'true',
                'use_sim_time': 'true',
                'rviz': 'true',
                'Grid/FromDepth': 'false',
            }.items(),
        ),
    ])
