import sys
import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from order_msgs.srv import OrderService
from std_msgs.msg import String
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox, QComboBox, QGridLayout
from PyQt5.QtCore import pyqtSignal, QObject

class Signals(QObject):
    order_signal = pyqtSignal(str, int)
    status_signal = pyqtSignal(str, int)
    table_popup_signal = pyqtSignal(str, int)

signals = Signals()

class KitchenOrderDisplay(Node, QWidget):
    def __init__(self):
        Node.__init__(self, 'kitchen_order_display')
        QWidget.__init__(self)
        self.initUI()

        # ROS2 service to receive orders
        self.service = self.create_service(OrderService, 'submit_order_service', self.receive_order_callback)

        # ROS2 publisher to publish order status
        self.status_publishers = {}
        for i in range(1, 10):
            self.status_publishers[i] = self.create_publisher(String, f'order_status_table_{i}', 10)

        # ROS2 subscriber to receive payment completion updates
        self.payment_subscriber = self.create_subscription(String, 'payment_completion', self.receive_payment_callback, 10)

        # 결제 상태를 관리하는 딕셔너리
        self.payment_status = {}

        # 각 테이블의 현재 상태를 관리하는 딕셔너리
        self.current_status = {}

        # 상태 단계 리스트 (정해진 순서)
        self.status_sequence = [
            "Order Accepted",
            "Cooking",
            "Cooking Completed",
            "Delivery In Progress"
        ]

        # delivery_publisher 추가
        self.delivery_publisher = self.create_publisher(String, 'delivery_order', 10)

        # Connect to signals for table status updates
        signals.status_signal.connect(self.update_status_from_signal)
        
        # ROS2 subscriber to receive delivery completion updates
        self.delivery_completion_subscriber = self.create_subscription(String, 'delivery_completion', self.receive_delivery_completion_callback, 10)

        # 최근 클릭된 테이블 번호를 저장할 변수
        self.selected_table_number = None

    def initUI(self):
        main_layout = QVBoxLayout()

        # Grid layout for table order displays
        grid_layout = QGridLayout()
        self.table_orders = {}

        # Create 9 QListWidgets for each table with SingleSelection mode
        for i in range(1, 10):
            table_label = QLabel(f"Table {i} Orders:")
            table_order_list = QListWidget()
            table_order_list.setSelectionMode(QListWidget.SingleSelection)
            self.table_orders[i] = table_order_list

            # itemClicked 시그널을 슬롯에 연결해 선택된 테이블 번호를 저장합니다.
            table_order_list.itemClicked.connect(lambda item, table_number=i: self.update_selected_table(table_number))

            grid_layout.addWidget(table_label, (i - 1) // 3, (i - 1) % 3 * 2)
            grid_layout.addWidget(table_order_list, (i - 1) // 3, (i - 1) % 3 * 2 + 1)

        main_layout.addLayout(grid_layout)

        # Accept and Reject buttons
        self.accept_button = QPushButton("Accept Order")
        self.accept_button.clicked.connect(self.acceptOrder)
        main_layout.addWidget(self.accept_button)

        self.reject_button = QPushButton("Reject Order")
        self.reject_button.clicked.connect(self.rejectOrder)
        main_layout.addWidget(self.reject_button)

        # Status update combo box
        self.status_combobox = QComboBox()
        self.status_combobox.addItems(["Cooking", "Cooking Completed", "Delivery In Progress"])
        main_layout.addWidget(self.status_combobox)

        # Button to update order status
        self.update_status_button = QPushButton("Update Status")
        self.update_status_button.clicked.connect(self.updateOrderStatus)
        main_layout.addWidget(self.update_status_button)

        self.setLayout(main_layout)
        self.setWindowTitle('Kitchen Order Display')
        self.show()

    def update_selected_table(self, table_number):
        # 선택된 테이블 번호를 업데이트합니다.
        self.selected_table_number = table_number

    def receive_order_callback(self, request, response):
        table_number = int(request.order_message.split(' ')[1])
        if table_number in self.table_orders:
            self.table_orders[table_number].addItem(request.order_message)
        self.get_logger().info(f'Received Order: {request.order_message}')
        response.success = True
        response.response_message = 'Order received successfully'
        return response

    def acceptOrder(self):
        # 선택된 테이블 번호가 설정되어 있는지 확인합니다.
        if self.selected_table_number is None:
            QMessageBox.warning(self, "No Selection", "Please select an order to accept.")
            return

        table_list = self.table_orders[self.selected_table_number]
        current_item = table_list.currentItem()
        if current_item:
            order_message = current_item.text()
            QMessageBox.information(self, "Order Accepted", f"Order accepted: {order_message}")

            order_details_msg = String()
            order_details_msg.data = f"Order: {order_message}"
            self.status_publishers[self.selected_table_number].publish(order_details_msg)
            self.get_logger().info(f'Published Order Details: {order_details_msg.data}')
            
            self.publish_status(order_message, "Order Accepted")

            self.payment_status[self.selected_table_number] = False
            
            # 선택 초기화
            table_list.clearSelection()
        else:
            QMessageBox.warning(self, "No Selection", "Please select an order to accept.")

    def rejectOrder(self):
        if self.selected_table_number is None:
            QMessageBox.warning(self, "No Selection", "Please select an order to reject.")
            return

        table_list = self.table_orders[self.selected_table_number]
        current_item = table_list.currentItem()
        if current_item:
            order_message = current_item.text()
            QMessageBox.information(self, "Order Rejected", f"Order rejected: {order_message}")
            table_list.takeItem(table_list.row(current_item))
            
            self.publish_status(order_message, "Order Rejected")

            # 선택 초기화
            table_list.clearSelection()
        else:
            QMessageBox.warning(self, "No Selection", "Please select an order to reject.")

    def updateOrderStatus(self):
        if self.selected_table_number is None:
            QMessageBox.warning(self, "No Selection", "Please select an order to update status.")
            return

        table_list = self.table_orders[self.selected_table_number]
        current_item = table_list.currentItem()
        if current_item:
            order_message = current_item.text()

            if not self.payment_status.get(self.selected_table_number, False):
                QMessageBox.warning(self, "Payment Required", "Cannot update status until payment is made.")
                return

            current_status = self.current_status.get(self.selected_table_number, "Order Accepted")
            next_status = self.status_combobox.currentText()

            try:
                current_index = self.status_sequence.index(current_status)
                next_index = self.status_sequence.index(next_status)

                if next_index == current_index + 1:
                    QMessageBox.information(self, "Status Updated", f"Order status updated to: {next_status}")
                    self.publish_status(order_message, f"{next_status}")
                    self.current_status[self.selected_table_number] = next_status
                    self.get_logger().info(f"Order status for table {self.selected_table_number} updated to: {next_status}")

                    if next_status == "Delivery In Progress":
                        delivery_msg = String()
                        delivery_msg.data = f"Table {self.selected_table_number} - Delivery In Progress"
                        self.delivery_publisher.publish(delivery_msg)
                        self.get_logger().info(f'Published delivery task for Table {self.selected_table_number}')
                    
                    table_list.clearSelection()

                elif next_index <= current_index:
                    QMessageBox.warning(self, "Invalid Status Transition", "You must move to the next sequential status.")
                else:
                    QMessageBox.warning(self, "Invalid Status Transition", "Skipping statuses is not allowed.")
            except ValueError as e:
                self.get_logger().error(f"Status transition error: {e}")
                QMessageBox.warning(self, "Invalid Status", f"Selected status is not valid: {next_status}")
            
            table_list.clearSelection()
        else:
            QMessageBox.warning(self, "No Selection", "Please select an order to update status.")

    def publish_status(self, order_message, status):
        table_number = int(order_message.split(' ')[1])
        status_message = String()
        status_message.data = f"Table {table_number} - Status: {status}"
        
        if table_number in self.status_publishers:
            self.status_publishers[table_number].publish(status_message)
            self.get_logger().info(f'Published Order Status to table {table_number}: {status_message.data}')
            signals.status_signal.emit(status, table_number)

    def receive_payment_callback(self, msg):
        if "Payment completed for Table" in msg.data:
            table_number = int(msg.data.split(' ')[-1])
            self.payment_status[table_number] = True
            self.get_logger().info(f'Received payment completion for table {table_number}')

    def update_status_from_signal(self, status, table_number):
        if table_number in self.table_orders:
            for i in range(self.table_orders[table_number].count()):
                item_text = self.table_orders[table_number].item(i).text()
                if f"Table {table_number}" in item_text:
                    self.table_orders[table_number].item(i).setText(f"Table {table_number} - Status: {status}")
                    break

    def receive_delivery_completion_callback(self, msg):
        if "Delivery Completed" in msg.data:
            try:
                parts = msg.data.split(' ')
                table_number = int(parts[1])

                # 상태 초기화
                self.publish_status(f"Table {table_number}", "Delivery Completed")
                self.get_logger().info(f'Received delivery completion for table {table_number}')
                
                if table_number in self.current_status:
                    del self.current_status[table_number]
                if table_number in self.payment_status:
                    del self.payment_status[table_number]
                
                # 주문 리스트에서 해당 항목 제거
                for i in range(self.table_orders[table_number].count()):
                    item_text = self.table_orders[table_number].item(i).text()
                    if f"Table {table_number}" in item_text:
                        self.table_orders[table_number].takeItem(i)
                        break
                
            except ValueError as e:
                self.get_logger().error(f"Failed to parse delivery completion message: {msg.data}, error: {e}")


def main(args=None):
    rclpy.init(args=args)
    app = QApplication(sys.argv)
    kitchen_display = KitchenOrderDisplay()

    # Run ROS2 spin in a separate thread to avoid blocking the GUI
    ros_thread = threading.Thread(target=rclpy.spin, args=(kitchen_display,), daemon=True)
    ros_thread.start()

    sys.exit(app.exec_())
    rclpy.shutdown()

if __name__ == '__main__':
    main()