# Autonomous Patrol Bot | ROS 2 & Gazebo

An autonomous mobile robot simulation developed using ROS 2, designed to navigate an environment, avoid obstacles and perform predefined patrol routes with minimal manual intervention.

The project uses a TurtleBot3 Waffle model in Gazebo with a custom obstacle environment. It explores autonomous navigation, sensor integration, SLAM and waypoint-based patrol functionality.

## Project Overview

The Autonomous Patrol Bot demonstrates how a mobile robot can perform routine patrol operations in a simulated environment.

The robot uses sensor feedback and odometry to understand its surroundings, navigate through designated locations and respond to obstacles encountered during movement.

The project focuses on integrating robotics software, perception, navigation and control into a single autonomous system.

## Key Features

- **Autonomous Patrol:** Navigation through four predefined patrol waypoints.
- **Obstacle Avoidance:** Reactive obstacle avoidance using LiDAR feedback.
- **SLAM:** Mapping and localization using RTAB-Map.
- **Sensor Integration:** LiDAR, RGB-D camera, IMU and wheel odometry.
- **Navigation:** ROS 2 Nav2 integration for path planning and autonomous navigation.
- **Simulation Environment:** TurtleBot3 Waffle simulated in Gazebo with a custom obstacle world.
- **Map Generation:** Generation and saving of a 2D occupancy map.

## Technology Stack

| Component | Technology |
|---|---|
| Operating System | Ubuntu 22.04 |
| Robotics Middleware | ROS 2 Humble |
| Robot Platform | TurtleBot3 Waffle |
| Simulation | Gazebo Classic |
| Visualization | RViz2 |
| Navigation | Nav2 |
| SLAM | RTAB-Map |
| Programming | Python |
| Sensors | LiDAR, RGB-D Camera, IMU |
| Odometry | Wheel Odometry |

## System Architecture

The system combines simulation, sensor feedback, mapping and navigation to achieve autonomous patrol functionality.

1. **Simulation:** Gazebo provides the robot and custom obstacle environment.
2. **Perception:** LiDAR and RGB-D sensor data provide environmental information.
3. **Localization and Mapping:** RTAB-Map supports mapping and localization.
4. **Navigation:** Nav2 provides path-planning and navigation capabilities.
5. **Patrol Execution:** The robot follows predefined waypoints while responding to obstacles.

## Autonomous Patrol Implementation

The patrol functionality is implemented through a ROS 2 Python node.

The `auto_mapper.py` script uses the following ROS 2 topics:

| Topic | Purpose |
|---|---|
| `/scan` | LiDAR sensor measurements |
| `/odom` | Robot odometry feedback |
| `/cmd_vel` | Robot velocity commands |

The node uses sensor feedback to control robot movement, follow predefined waypoints and perform reactive obstacle avoidance.

The project also includes RTAB-Map and Nav2 integration for mapping, localization and autonomous navigation.

## Project Structure

```text
Patrol-Bot/
│
└── patrol_ws/
    │
    └── src/
        │
        └── patrol_guard_bot/
            │
            ├── launch/
            ├── config/
            ├── maps/
            ├── worlds/
            ├── scripts/
            │   └── auto_mapper.py
            ├── package.xml
            └── CMakeLists.txt
```

Refer to the repository for the complete directory structure.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic
- TurtleBot3 packages
- Nav2
- RTAB-Map
- RViz2
- Colcon build tools

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Cyber-M4/Patrol-Bot.git
```

### 2. Navigate to the ROS 2 Workspace

```bash
cd Patrol-Bot/patrol_ws
```

### 3. Install Dependencies

```bash
rosdep install --from-paths src --ignore-src -r -y
```

### 4. Build the Workspace

```bash
colcon build --symlink-install
```

### 5. Source the Workspace

```bash
source install/setup.bash
```

## Running the Project

After successfully building the workspace, open three separate terminals and execute the following commands in order.

### Terminal 1 – Launch Gazebo Simulation

Start the custom Gazebo environment with the TurtleBot3 Waffle robot.

```bash
source /opt/ros/humble/setup.bash
source ~/Patrol-Bot/patrol_ws/install/setup.bash

ros2 launch patrol_guard_bot patrol_simulation.launch.py
```

**Expected Result:**
- Gazebo launches successfully.
- The TurtleBot3 Waffle appears inside the custom simulation environment.
- The robot is ready to receive commands.

Keep this terminal running.

### Terminal 2 – Launch RTAB-Map

Open a second terminal and start the RTAB-Map node for mapping and localization.

```bash
source /opt/ros/humble/setup.bash
source ~/Patrol-Bot/patrol_ws/install/setup.bash

ros2 launch patrol_guard_bot patrol_rtabmap.launch.py
```

**Expected Result:**
- RTAB-Map starts.
- Sensor information is processed.
- Mapping and localization functionality becomes available.

Keep this terminal running.

### Terminal 3 – Start Autonomous Patrol

Open a third terminal and execute the autonomous mapper and patrol node.

```bash
source /opt/ros/humble/setup.bash
source ~/Patrol-Bot/patrol_ws/install/setup.bash

ros2 run patrol_guard_bot auto_mapper
```

**Expected Result:**
- The robot begins autonomous movement.
- LiDAR data is used for obstacle detection.
- Odometry feedback supports movement tracking.
- The robot follows its predefined patrol waypoints.
- Map saving is performed according to the node's implementation.

### Execution Order

| Terminal | Process | Command |
|---|---|---|
| 1 | Gazebo simulation | `patrol_simulation.launch.py` |
| 2 | RTAB-Map | `patrol_rtabmap.launch.py` |
| 3 | Autonomous patrol | `auto_mapper` |

**Important:** Start the simulation first, followed by RTAB-Map, and finally the autonomous patrol node. Keep all three terminals running during the simulation.

## Demonstration

The robot was tested in a custom Gazebo environment containing obstacles and four predefined patrol locations.

During the demonstration, the robot successfully navigated through all four designated patrol points in approximately one minute.

The simulation demonstrates the integration of autonomous movement, sensor feedback and obstacle avoidance in a controlled environment.

## Learning Outcomes

This project provided practical experience in:

- Working with ROS 2 nodes, topics and communication.
- Integrating multiple sensors into a robotic system.
- Understanding SLAM and autonomous localization.
- Implementing waypoint-based patrol behaviour.
- Working with Nav2 and autonomous navigation concepts.
- Developing and testing robotic systems in Gazebo.
- Using Python for robotics applications.

## Future Improvements

- Integration with a physical mobile robot.
- Improved obstacle detection and navigation in dynamic environments.
- Remote monitoring and patrol status reporting.
- Integration of computer vision for object and human detection.
- Development of a more comprehensive autonomous surveillance system.


