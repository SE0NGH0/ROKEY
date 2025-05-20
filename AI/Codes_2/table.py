import sys
import threading
import rclpy
import sqlite3
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from order_msgs.srv import OrderService
from std_msgs.msg import String
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QMessageBox,
    QInputDialog, QScrollArea
)
from PyQt5.QtGui import QPixmap
from datetime import datetime


class TableOrderDisplay(Node, QWidget):
    def __init__(self, table_number):
        Node.__init__(self, f'table_order_display_{table_number}')
        QWidget.__init__(self)
        self.table_number = table_number
        self.client_ = self.create_client(OrderService, 'submit_order_service')
        while not self.client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service to become available...')
        
        # SQLite database connection
        self.db_connection = sqlite3.connect('/home/parkseongho/project_ws/database.db', check_same_thread=False)
        self.db_cursor = self.db_connection.cursor()
        self.setup_database()

        # ROS2 publisher to publish payment completion information
        self.payment_publisher = self.create_publisher(String, 'payment_completion', 10)

        # ROS2 publisher for robot call
        self.robot_call_publisher = self.create_publisher(String, 'robot_call', 10)

        self.status_subscriber = self.create_subscription(String, f'order_status_table_{self.table_number}', self.receive_status_callback, 10)

        self.initUI()

    def setup_database(self):
        # Create the orders table if it does not exist
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        self.db_connection.commit()

    def initUI(self):
        self.order_counts = {}
        self.total_price = 0.0

        layout = QVBoxLayout()

        # Table number label
        table_label = QLabel(f"Table {self.table_number}")
        layout.addWidget(table_label)

        # Menu items (name, price, image path)
        self.menu_items = [
            ("Burger", 5.99, "src/turtlebot3_gui/turtlebot3_gui/images/hamburger.png"),
            ("Pizza", 8.99, "src/turtlebot3_gui/turtlebot3_gui/images/pizza.png"),
            ("Salad", 4.99, "src/turtlebot3_gui/turtlebot3_gui/images/salad.png"),
            ("Pasta", 7.49, "src/turtlebot3_gui/turtlebot3_gui/images/pasta.png"),
        ]

        # Create menu buttons with images
        self.menu_buttons = QGridLayout()
        for i, (name, price, img_path) in enumerate(self.menu_items):
            button_layout = QVBoxLayout()
            pixmap = QPixmap(img_path)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setScaledContents(True)
            image_label.setFixedSize(100, 100)
            button_layout.addWidget(image_label)
            button = QPushButton(f"{name} - ${price}")
            button.clicked.connect(lambda checked, n=name, p=price: self.addOrder(n, p))
            button_layout.addWidget(button)
            self.menu_buttons.addLayout(button_layout, i // 2, i % 2)
            self.order_counts[name] = 0

        layout.addLayout(self.menu_buttons)
        self.order_label = QLabel("Current Order:")
        layout.addWidget(self.order_label)

        submit_button = QPushButton("Submit Order")
        submit_button.clicked.connect(self.submitOrder)
        layout.addWidget(submit_button)

        remove_button = QPushButton("Remove Order")
        remove_button.clicked.connect(self.removeOrder)
        layout.addWidget(remove_button)

        self.total_price_label = QLabel("Total Price: $0.00")
        layout.addWidget(self.total_price_label)
        self.status_label = QLabel("Status: None")
        layout.addWidget(self.status_label)

        self.order_check_label = QLabel("Order Check:")
        layout.addWidget(self.order_check_label)

        self.order_check_list = QListWidget()
        layout.addWidget(self.order_check_list)

        pay_button = QPushButton("Make Payment")
        pay_button.clicked.connect(self.makePayment)
        layout.addWidget(pay_button)

        # Robot call button
        call_robot_button = QPushButton("Call Robot")
        call_robot_button.clicked.connect(self.call_robot)
        layout.addWidget(call_robot_button)

        self.setLayout(layout)
        self.setWindowTitle(f'Table {self.table_number} Order Display')
        self.show()

    def makePayment(self):
        current_item = self.order_check_list.currentItem()
        if current_item:
            order_text = current_item.text()
            self.order_check_list.takeItem(self.order_check_list.row(current_item))
            QMessageBox.information(self, "Payment", f"Payment successful for:\n{order_text}")
            item_text = current_item.text()
            self.get_logger().info(f'item_text:\n{item_text}')
            items = item_text.split('\n')[1:]  # Extract items from the order message
            iterator = iter(items)
            for i in range(len(items)-2):
                item = next(iterator)
                if item:
                    item_name, quantity = item.split(': ')
                    quantity = int(quantity)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.db_cursor.execute(
                        "INSERT INTO completed_orders (item_name, quantity, timestamp) VALUES (?, ?, ?)",
                        (item_name, quantity, timestamp)
                    )
                    self.get_logger().info(f'saved) item_name: {item_name}, quantity: {quantity}, timestamp: {timestamp}')

                else:
                    self.get_logger().error('no item')
                    break
            self.db_connection.commit()
            try:
                table_number = int(order_text.split(' ')[2])
                payment_msg = String()
                payment_msg.data = f"Payment completed for Table {table_number}"
                self.payment_publisher.publish(payment_msg)
                self.get_logger().info(f'Published payment completion for Table {table_number}')
            except ValueError:
                self.get_logger().error(f"Failed to extract table number from order text: {order_text}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select an order to make payment.")

    def addOrder(self, item_name, item_price):
        self.order_counts[item_name] += 1
        self.total_price += item_price
        self.updateOrderLabel()

    def removeOrder(self):
        items = [item for item, count in self.order_counts.items() if count > 0]
        if not items:
            return

        item_name, ok = QInputDialog.getItem(self, "Remove Order", "Select item to remove:", items, 0, False)
        if ok and item_name:
            if self.order_counts[item_name] > 0:
                self.order_counts[item_name] -= 1
                for name, price, _ in self.menu_items:
                    if name == item_name:
                        self.total_price -= price
                        break
                self.updateOrderLabel()

    def updateOrderLabel(self):
        order_text = "Current Order:\n"
        for item, count in self.order_counts.items():
            if count > 0:
                order_text += f"{item}: {count}\n"
        self.order_label.setText(order_text)
        self.total_price_label.setText(f"Total Price: ${self.total_price:.2f}")

    def submitOrder(self):
        order_message = f"Table {self.table_number} Order:\n"
        for item, count in self.order_counts.items():
            if count > 0:
                order_message += f"{item}: {count}\n"
        order_message += f"Total Price: ${self.total_price:.2f}\n"

        req = OrderService.Request()
        req.order_message = order_message
        future = self.client_.call_async(req)
        future.add_done_callback(lambda future: self.handle_service_response(future))

    def handle_service_response(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info('Order submitted successfully')
                self.order_counts = {name: 0 for name in self.order_counts}
                self.total_price = 0.0
                self.updateOrderLabel()
            else:
                self.get_logger().error(f'Failed to submit the order: {response.response_message}')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

    def receive_status_callback(self, msg):
        if "Status:" in msg.data:
            self.status_label.setText(f"Status: {msg.data.split(' - Status: ')[-1]}")
            self.get_logger().info(f'Received status update: {msg.data}')
            if "Delivery Completed" in msg.data:
                for i in range(self.order_check_list.count()):
                    item_text = self.order_check_list.item(i).text()
                    if f"Table {self.table_number}" in item_text:
                        self.order_check_list.takeItem(i)
                        break
        elif "Order:" in msg.data:
            self.order_check_list.addItem(msg.data)
            self.get_logger().info(f'Added to Order Check: {msg.data}')
        else:
            self.get_logger().warning(f'Unexpected message format: {msg.data}')

    def call_robot(self):
        call_msg = String()
        call_msg.data = f"Call robot to Table {self.table_number}"
        self.robot_call_publisher.publish(call_msg)
        self.get_logger().info(f'Robot call sent for Table {self.table_number}')
        QMessageBox.information(self, "Robot Call", f"Robot moves to {self.table_number}.")


class AllTablesOrderDisplay(Node, QWidget):
    def __init__(self):
        Node.__init__(self, 'all_tables_order_display')
        QWidget.__init__(self)

        main_layout = QVBoxLayout()

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area_widget = QWidget()
        grid_layout = QGridLayout()

        self.tables = []
        for table_number in range(1, 10):
            table_display = TableOrderDisplay(table_number)
            row = (table_number - 1) // 3  # 3개씩 한 줄
            col = (table_number - 1) % 3
            grid_layout.addWidget(table_display, row, col)
            self.tables.append(table_display)

        scroll_area_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_area_widget)
        scroll_area.setWidgetResizable(True)

        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        self.setWindowTitle('All Tables Order Display with Scroll')
        self.show()


def main(args=None):
    rclpy.init(args=args)
    app = QApplication(sys.argv)

    all_tables_display = AllTablesOrderDisplay()

    executor = MultiThreadedExecutor()
    for table in all_tables_display.tables:
        executor.add_node(table)

    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    sys.exit(app.exec_())

    rclpy.shutdown()


if __name__ == '__main__':
    main()