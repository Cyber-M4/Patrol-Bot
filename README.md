# Patrol Bot – Autonomous ROS 2 Patrol Robot

A ROS 2-based autonomous patrol robot designed to navigate a simulated environment, avoid obstacles, build a map, and follow a predefined patrol route. The project combines laser-based perception, odometry, waypoint navigation, and reactive obstacle avoidance to give the robot the ability to move around the environment with minimal manual control.

The robot first explores the environment using LiDAR and odometry data while following a set of waypoints. It continuously checks the surrounding area for obstacles and adjusts its velocity and direction when something gets too close. Once the mapping loop is completed, the generated 2D occupancy map is automatically saved and can be used for the next stage of navigation and patrol.

The project was built as a hands-on exercise in ROS 2, focusing on robot movement, sensor integration, navigation logic, mapping, and autonomous behavior.

# Key Features

* Autonomous waypoint-based navigation
* LiDAR-based obstacle detection and avoidance
* Odometry-based position and orientation tracking
* Automatic 2D map generation and saving
* ROS 2 nodes for mapping and patrol control
* Gazebo-based robot simulation
* Configurable maps, worlds, and navigation parameters

# Guide 
Step 1 — Clone and build

Terminal 1

cd ~

git clone https://github.com/Cyber-M4/Patrol-Bot.git

cd ~/Patrol-Bot/patrol_ws

source /opt/ros/humble/setup.bash

colcon build --symlink-install

source install/setup.bash

ros2 pkg list | grep patrol_guard_bot


Step 2 — Start the simulation

Terminal 1

ros2 launch patrol_guard_bot patrol_simulation.launch.py

Keep Terminal 1 running. Do not close it.


Step 3 — Start RTAB-Map

Terminal 2

source /opt/ros/humble/setup.bash

source ~/Patrol-Bot/patrol_ws/install/setup.bash

ros2 launch patrol_guard_bot patrol_rtabmap.launch.py

Keep Terminal 2 running.


Step 4 — Start the autonomous mapper/patrol

Terminal 3

source /opt/ros/humble/setup.bash

source ~/Patrol-Bot/patrol_ws/install/setup.bash

ros2 run patrol_guard_bot auto_mapper
