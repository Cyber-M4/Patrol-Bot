import math
import subprocess
import time
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from rclpy.node import Node


class AutoMapperNode(Node):
    def __init__(self):
        super().__init__('auto_mapper_node')

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.odom_received = False
        self.min_front_dist = 10.0
        self.min_left_dist = 10.0
        self.min_right_dist = 10.0

        # Safe outer corridor loop around the 4 obstacles (10m x 10m room)
        # Avoids center obstacles (-2,2), (1.5,2.5), (2,-1.5), (-1.5,-2.5)
        self.waypoints = [
            (0.0, -3.5),
            (3.5, -3.5),
            (3.5, 0.0),
            (3.5, 3.5),
            (0.0, 3.5),
            (-3.5, 3.5),
            (-3.5, 0.0),
            (-3.5, -3.5),
            (0.0, 0.0)   # Return to origin to trigger Loop Closure
        ]

        self.current_wp_idx = 0
        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info('🤖 Smart Auto-Mapper Started: Navigating safe corridor with collision avoidance...')

    def scan_callback(self, msg: LaserScan):
        # 360-degree laser scan slices
        num_readings = len(msg.ranges)
        if num_readings == 0:
            return

        def get_min_range(start_deg, end_deg):
            start_idx = int(start_deg * num_readings / 360.0)
            end_idx = int(end_deg * num_readings / 360.0)
            if start_idx < end_idx:
                ranges = msg.ranges[start_idx:end_idx]
            else:
                ranges = msg.ranges[start_idx:] + msg.ranges[:end_idx]
            valid_ranges = [r for r in ranges if not math.isinf(r) and not math.isnan(r) and r > msg.range_min]
            return min(valid_ranges) if valid_ranges else 10.0

        self.min_front_dist = min(get_min_range(340, 360), get_min_range(0, 20))
        self.min_left_dist = get_min_range(20, 70)
        self.min_right_dist = get_min_range(290, 340)

    def odom_callback(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)
        self.odom_received = True

    def control_loop(self):
        if not self.odom_received:
            return

        if self.current_wp_idx >= len(self.waypoints):
            self.stop_robot()
            self.timer.cancel()
            self.get_logger().info('✅ Closed loop completed! RTAB-Map loop closure achieved.')
            self.save_map_and_finish()
            return

        target_x, target_y = self.waypoints[self.current_wp_idx]
        dx = target_x - self.current_x
        dy = target_y - self.current_y
        distance = math.hypot(dx, dy)

        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - self.current_yaw

        while angle_diff > math.pi:
            angle_diff -= 2.0 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2.0 * math.pi

        twist = Twist()

        # Check waypoint arrival
        if distance < 0.40:
            self.get_logger().info(f'Reached Waypoint {self.current_wp_idx + 1}/{len(self.waypoints)} -> Moving to next')
            self.current_wp_idx += 1
            return

        # Reactive Obstacle Avoidance override
        if self.min_front_dist < 0.60:
            # Too close in front -> slow down and turn away from the nearest side
            twist.linear.x = 0.02
            if self.min_left_dist < self.min_right_dist:
                twist.angular.z = -0.6  # Turn right
            else:
                twist.angular.z = 0.6   # Turn left
        elif self.min_left_dist < 0.45:
            # Wall/obstacle on the left -> nudge right
            twist.linear.x = 0.12
            twist.angular.z = -0.4
        elif self.min_right_dist < 0.45:
            # Wall/obstacle on the right -> nudge left
            twist.linear.x = 0.12
            twist.angular.z = 0.4
        else:
            # Path clear -> steer towards target waypoint
            if abs(angle_diff) > 0.35:
                twist.linear.x = 0.05
                twist.angular.z = 0.6 if angle_diff > 0 else -0.6
            else:
                twist.linear.x = min(0.20, 0.15 * distance + 0.08)
                twist.angular.z = 0.5 * angle_diff

        self.cmd_vel_pub.publish(twist)

    def stop_robot(self):
        self.cmd_vel_pub.publish(Twist())

    def save_map_and_finish(self):
        self.get_logger().info('💾 Automatically saving 2D occupancy map to maps/patrol_map...')
        time.sleep(2.0)

        save_cmd = [
            'ros2', 'run', 'nav2_map_server', 'map_saver_cli',
            '-f', '/home/ros2ar/patrol_ws/src/patrol_guard_bot/maps/patrol_map'
        ]
        try:
            subprocess.run(save_cmd, check=True)
            self.get_logger().info('🎉 Map saved successfully! Ready for Localization & Patrol Mode.')
        except Exception as e:
            self.get_logger().error(f'Failed to auto-save map: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = AutoMapperNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
