import sys
import threading
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from rclpy.action.client import GoalStatus
from std_msgs.msg import String
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QTextEdit
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont
import numpy as np
from rclpy.qos import QoSProfile, ReliabilityPolicy
import time
import pyttsx3


class ServingRobotGUI(Node, QWidget):
    update_signal = pyqtSignal(str)

    def __init__(self):
        Node.__init__(self, 'serving_robot_gui')
        QWidget.__init__(self)
        self.initUI()

        # Connect update signal to message display
        self.update_signal.connect(self.log_message)

        # QoS profile for map subscription
        qos_profile = QoSProfile(depth=10)
        qos_profile.reliability = ReliabilityPolicy.BEST_EFFORT

        # ROS2 subscribers
        self.map_subscriber = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, qos_profile)
        self.pose_subscriber = self.create_subscription(
            PoseWithCovarianceStamped, '/amcl_pose', self.pose_callback, 10)
        self.delivery_subscriber = self.create_subscription(
            String, 'delivery_order', self.receive_delivery_callback, 10)
        
        # Subscribe to robot_call topic for table call functionality
        self.robot_call_subscriber = self.create_subscription(
            String, 'robot_call', self.handle_robot_call, 10)

        # ROS2 publishers
        self.delivery_completion_publisher = self.create_publisher(String, 'delivery_completion', 10)
        self.initial_pose_publisher = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)

        # Action Client for autonomous navigation
        self.navigate_to_pose_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Variables to store map and robot pose
        self.map_data = None
        self.robot_pose = None
        self.position = None  # Target position for navigation
        self.is_robot_call_active = False  # Tracks if robot is responding to a robot call
        self.is_delivery_active = False   # Tracks if robot is responding to a delivery task

        # Timer to update the map display
        self.map_update_timer = QTimer(self)
        self.map_update_timer.timeout.connect(self.update_map_display)
        self.map_update_timer.start(500)  # Update every 500ms
        self.update_signal.emit("[INFO] Timer for map update started.")

        # Set initial pose
        self.publish_initial_pose()

    def initUI(self):
        layout = QVBoxLayout()

        # Label for serving robot tasks
        self.label = QLabel("Serving Robot Tasks:")
        layout.addWidget(self.label)

        # List to display delivery tasks
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        # Button to start delivery
        self.start_delivery_button = QPushButton("Start Delivery")
        self.start_delivery_button.clicked.connect(self.start_delivery)
        layout.addWidget(self.start_delivery_button)

        # Button to return to kitchen (initially disabled)
        self.return_to_kitchen_button = QPushButton("Return to Kitchen")
        self.return_to_kitchen_button.setEnabled(False)
        self.return_to_kitchen_button.clicked.connect(self.return_to_kitchen)
        layout.addWidget(self.return_to_kitchen_button)

        # Map display label
        self.map_image_label = QLabel("Map:")
        self.map_image_label.setFixedSize(800, 600)  # Set map label size
        self.map_image_label.setScaledContents(True)
        layout.addWidget(self.map_image_label)

        # Message display for logging
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)

        self.setLayout(layout)
        self.setWindowTitle('Serving Robot GUI with Dynamic Map')
        self.show()

    def log_message(self, message):
        # Display log messages in the message_display widget
        self.message_display.append(message)

    def publish_initial_pose(self):
        time.sleep(4)
        initial_pose_msg = PoseWithCovarianceStamped()
        initial_pose_msg.header.frame_id = "map"
        initial_pose_msg.pose.pose.position.x = 0.0
        initial_pose_msg.pose.pose.position.y = 0.0
        initial_pose_msg.pose.pose.position.z = 0.0
        initial_pose_msg.pose.pose.orientation.z = 0.0
        initial_pose_msg.pose.pose.orientation.w = 1.0
        self.initial_pose_publisher.publish(initial_pose_msg)
        self.update_signal.emit("[INFO] Initial pose has been set automatically.")

    def map_callback(self, msg):
        # Store the latest map data
        self.map_data = msg
        self.update_signal.emit("[INFO] Received new map data")

    def pose_callback(self, msg):
        # Store the latest robot pose
        self.robot_pose = msg.pose.pose
        self.update_signal.emit("[INFO] Received new robot pose data")

    def receive_delivery_callback(self, msg):
        """
        Callback for receiving delivery tasks from the 'delivery_order' topic.
        Adds the received task to the task list for navigation.
        """
        # Add the delivery task to the list
        self.task_list.addItem(msg.data)
        self.get_logger().info(f'Received delivery task: {msg.data}')
        self.update_signal.emit(f"[INFO] Received delivery task: {msg.data}")

    def handle_robot_call(self, msg):
        try:
            table_number = int(msg.data.split(" ")[-1])
            self.get_logger().info(f'Received robot call for Table {table_number}')
            self.position = self.get_table_coordinates(table_number)
            self.is_robot_call_active = True
            self.is_delivery_active = False
            message = f"[INFO] Robot call - navigating to Table {table_number} at {self.position[0]}, {self.position[1]}"
            self.update_signal.emit(message)
            self.navigate_to_pose_send_goal()
        except ValueError:
            self.get_logger().error(f"Failed to extract table number from robot call message: {msg.data}")

    def start_delivery(self):
        current_item = self.task_list.currentItem()
        if current_item:
            task_text = current_item.text()
            try:
                table_number = int(task_text.split(' ')[1])
                self.position = self.get_table_coordinates(table_number)
                self.is_robot_call_active = False
                self.is_delivery_active = True
                message = f"[INFO] Starting delivery to Table {table_number} at {self.position[0]}, {self.position[1]}"
                self.update_signal.emit(message)
                self.navigate_to_pose_send_goal()
            except ValueError:
                self.get_logger().error(f"Failed to extract table number from task text: {task_text}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a task to start delivery.")

    def return_to_kitchen(self):
        # Set position to kitchen coordinates
        self.position = [0.0, 0.0]
        self.is_robot_call_active = False
        self.is_delivery_active = False
        message = f"[INFO] Returning to Kitchen at {self.position[0]}, {self.position[1]}"
        self.update_signal.emit(message)
        self.navigate_to_pose_send_goal()
        self.return_to_kitchen_button.setEnabled(False)

    def get_table_coordinates(self, table_number):
        # Define coordinates for each table (example values)
        coordinates = {
            1: [3.7, 1.6],
            2: [3.7, 0.5],
            3: [3.7, -0.5],
            4: [2.5, 1.6],
            5: [2.5, 0.5],
            6: [2.5, -0.5],
            7: [1.5, 1.6],
            8: [1.5, 0.5],
            9: [1.5, -0.5]
        }
        return coordinates.get(table_number, [0.0, 0.0])

    def navigate_to_pose_send_goal(self):
        if not self.navigate_to_pose_action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('NavigateToPose action server not available.')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = self.position[0]
        goal_msg.pose.pose.position.y = self.position[1]
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f"Sending navigation goal to: {self.position}")
        send_goal_future = self.navigate_to_pose_action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Navigation goal was rejected.")
            return

        self.get_logger().info("Navigation goal accepted.")
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        try:
            result = future.result()
            if result.status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info("Navigation goal succeeded!")
                self.update_signal.emit("[INFO] Navigation goal succeeded!")

                # Remove the completed task from the task list if it was a delivery task
                if self.is_delivery_active:
                    current_item = self.task_list.currentItem()
                    if current_item:
                        task_text = current_item.text()
                        self.task_list.takeItem(self.task_list.row(current_item))
                        self.update_signal.emit(f"[INFO] Completed task removed: {task_text}")

                        # Publish 'Delivery Completed' message to Kitchen Display
                        try:
                            table_number = int(task_text.split(" ")[1])
                            completion_msg = String()
                            completion_msg.data = f"Table {table_number} - Delivery Completed"
                            self.delivery_completion_publisher.publish(completion_msg)
                            self.update_signal.emit(f"[INFO] Published delivery completion for Table {table_number}")

                            # Show popup message with automatic close
                            self.show_auto_closing_popup(f"Delivery to Table {table_number} completed.\nEnjoy your meal!")
                        except ValueError as e:
                            self.update_signal.emit(f"[ERROR] Failed to process delivery completion: {e}")

                # Activate return to kitchen button if necessary
                if self.is_robot_call_active or self.is_delivery_active:
                    self.return_to_kitchen_button.setEnabled(True)
                    self.is_robot_call_active = False
                    self.is_delivery_active = False
            else:
                self.get_logger().error(f"Navigation goal failed with status: {result.status}")
                self.update_signal.emit(f"[WARN] Navigation goal failed with status: {result.status}")
        except Exception as e:
            self.get_logger().error(f"Error in result_callback: {e}")
            self.update_signal.emit(f"[ERROR] An error occurred: {e}")

    def show_auto_closing_popup(self, message):
            """
            Show a popup message that automatically closes after 2 seconds.
            """
            # 음성 출력
            self.speak_message(message)

            popup = QMessageBox(self)
            popup.setWindowTitle("Enjoy Your Meal!")
            popup.setText(message)
            popup.setStandardButtons(QMessageBox.Ok)

            # Timer to close the popup automatically after 2 seconds
            QTimer.singleShot(2000, popup.close)

            popup.exec_()

    def speak_message(self, message):
        """
        Use pyttsx3 to convert text to speech using voice 58.
        """
        try:
            engine = pyttsx3.init()  # pyttsx3 엔진 초기화

            # 지원되는 음성 목록에서 58번 음성 선택
            voices = engine.getProperty('voices')
            if len(voices) > 58:  # 58번 음성이 존재하는지 확인
                engine.setProperty('voice', voices[24].id)  # 58번 음성 설정
            else:
                self.update_signal.emit("[WARN] Voice 58 not found, using default voice.")
            
            # 음성 속도와 볼륨 설정
            engine.setProperty('rate', 150)  # 음성 속도
            engine.setProperty('volume', 0.9)  # 볼륨

            # 메시지 읽기
            engine.say(message)
            engine.runAndWait()  # 음성 재생

        except Exception as e:
            self.update_signal.emit(f"[ERROR] Failed to play voice message: {e}")



    def update_map_display(self):
            if self.map_data is None:
                self.update_signal.emit("[WARN] No map data available to display")
                return
            # Convert OccupancyGrid data to image (no rotation, keep the original orientation)
            width = self.map_data.info.width
            height = self.map_data.info.height
            map_array = np.array(self.map_data.data).reshape((height, width))
            map_array = np.flip(map_array, axis=0)  # Flip vertically to correct orientation (as in RViz)
            # Convert occupancy values to grayscale (0: free, 100: occupied, -1: unknown)
            map_image = np.zeros((height, width, 3), dtype=np.uint8)
            map_image[map_array == 0] = [255, 255, 255]  # Free space
            map_image[map_array == 100] = [0, 0, 0]      # Occupied space
            map_image[map_array == -1] = [128, 128, 128] # Unknown space
            # Convert numpy array to QImage
            qimage = QImage(map_image.data, width, height, width * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            # Draw robot position if available
            if self.map_data is not None and self.robot_pose is not None:
                painter = QPainter(pixmap)
                try:
                    painter.setBrush(QColor(255, 0, 0))  # Red color for the robot
                    # Calculate the robot's position on the map
                    resolution = self.map_data.info.resolution
                    origin_x = self.map_data.info.origin.position.x
                    origin_y = self.map_data.info.origin.position.y
                    # Ensure resolution is valid
                    if resolution == 0:
                        raise ValueError("Invalid map resolution: 0")
                    # Convert robot's real-world position to pixel coordinates
                    x_pixel = int((self.robot_pose.position.x - origin_x) / resolution)
                    y_pixel = height - int((self.robot_pose.position.y - origin_y) / resolution)
                    # Draw the robot's position on the map
                    painter.drawEllipse(x_pixel - 5, y_pixel - 5, 10, 10)
                    # Draw table numbers on the map
                    painter.setFont(QFont("Verdana", 9, QFont.Bold))
                    painter.setPen(QColor(0, 0, 255))  # Blue color for table numbers
                    table_coordinates = {
                        1: [3.1, 1.6],
                        2: [3.1, 0.5],
                        3: [3.1, -0.5],
                        4: [2.0, 1.6],
                        5: [2.0, 0.5],
                        6: [2.0, -0.5],
                        7: [0.97, 1.6],
                        8: [0.97, 0.5],
                        9: [0.97, -0.5]
                    }
                    for table_number, (x, y) in table_coordinates.items():
                        x_pixel = int((x - origin_x) / resolution)
                        y_pixel = height - int((y - origin_y) / resolution)
                        painter.drawText(x_pixel, y_pixel, f"{table_number}")
                except Exception as e:
                    self.update_signal.emit(f"[ERROR] Failed to draw on map: {e}")
                finally:
                    painter.end()
            # Set the pixmap to the QLabel to display the map
            self.map_image_label.setPixmap(pixmap)


def main(args=None):
    rclpy.init(args=args)
    app = QApplication(sys.argv)
    serving_robot_gui = ServingRobotGUI()
    # Run ROS2 spin in a separate thread to avoid blocking the GUI
    ros_thread = threading.Thread(target=rclpy.spin, args=(serving_robot_gui,), daemon=True)
    ros_thread.start()
    sys.exit(app.exec_())
    rclpy.shutdown()


if __name__ == '__main__':
    main()