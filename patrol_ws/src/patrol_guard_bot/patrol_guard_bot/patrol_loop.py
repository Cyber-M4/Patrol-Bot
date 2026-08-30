import math
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


class AutonomousPatrolNode(Node):
    def __init__(self):
        super().__init__('autonomous_patrol_node')

        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.get_logger().info('⏳ Connecting to Nav2 /navigate_to_pose action server...')
        if not self._action_client.wait_for_server(timeout_sec=20.0):
            self.get_logger().error('❌ Nav2 action server not available! Make sure patrol_nav2.launch.py is running.')
            return

        self.get_logger().info('✅ Connected to Nav2!')
        self.get_logger().info('🛡️  AUTONOMOUS PATROL BOT: Navigation & Localization Active')

        # 4 Strategic Security Checkpoints (Safe corridor positions)
        self.checkpoints = [
            {"name": "Sector Alpha (East)",   "x": 3.0,  "y": 0.0,  "yaw": 90.0},
            {"name": "Sector Bravo (North)",  "x": 0.0,  "y": 3.0,  "yaw": 180.0},
            {"name": "Sector Charlie (West)", "x": -3.0, "y": 0.0,  "yaw": 270.0},
            {"name": "Sector Delta (South)",  "x": 0.0,  "y": -3.0, "yaw": 0.0},
        ]

        self.current_cp_idx = 0
        self.patrol_cycle = 1
        self.goal_active = False

        # Start patrol execution
        self.send_next_checkpoint()

    def create_pose(self, x: float, y: float, yaw_deg: float) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        yaw_rad = math.radians(yaw_deg)
        pose.pose.orientation.z = math.sin(yaw_rad / 2.0)
        pose.pose.orientation.w = math.cos(yaw_rad / 2.0)
        return pose

    def send_next_checkpoint(self):
        if self.current_cp_idx == 0:
            print("\n" + "="*50)
            print(f"COMMENCING PATROL CYCLE #{self.patrol_cycle}")
            print("="*50)

        cp = self.checkpoints[self.current_cp_idx]
        print(f"\n Navigating to Checkpoint {self.current_cp_idx + 1}/{len(self.checkpoints)}: {cp['name']} at ({cp['x']}, {cp['y']})...")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(cp['x'], cp['y'], cp['yaw'])

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal was rejected by Nav2. Retrying in 2 seconds...')
            time.sleep(2.0)
            self.send_next_checkpoint()
            return

        self.get_logger().info('Route planned! Robot is en route...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        # Optional: Can monitor remaining distance
        pass

    def get_result_callback(self, future):
        status = future.result().status
        cp_name = self.checkpoints[self.current_cp_idx]['name']

        if status == GoalStatus.STATUS_SUCCEEDED:
            print(f" Reached {cp_name}!")
            print("Performing 3-second security surveillance scan...")
            time.sleep(3.0)
        else:
            print(f" Navigation to {cp_name} completed with status: {status}. Moving to next sector.")

        # Advance checkpoint and loop
        self.current_cp_idx += 1
        if self.current_cp_idx >= len(self.checkpoints):
            print(f"\n Patrol Cycle #{self.patrol_cycle} completed successfully!")
            self.patrol_cycle += 1
            self.current_cp_idx = 0
            time.sleep(1.0)

        self.send_next_checkpoint()


def main(args=None):
    rclpy.init(args=args)
    node = AutonomousPatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n Patrol operation halted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
