from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Path to turtlebot3_navigation2 launch file
    nav2_launch_file_path = os.path.join(
        get_package_share_directory('turtlebot3_navigation2'),
        'launch',
        'navigation2.launch.py'
    )
    # Path to turtlebot3_gazebo launch file
    gazebo_launch_file_path = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'launch',
        'turtlebot3_world.launch.py'
    )
    return LaunchDescription([
        # Add Node actions for each of your Python scripts here, executed sequentially
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='turtlebot3_gui',  # Replace with the correct package name
                    executable='table',  # Replace with the correct executable name for table order display
                    name='table_node',
                    output='screen'
                )
            ]
        ),
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='turtlebot3_gui',  # Replace with the correct package name
                    executable='kitchen',  # Replace with the correct executable name for kitchen order display
                    name='kitchen_node',
                    output='screen'
                )
            ]
        ),
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='turtlebot3_gui',  # Replace with the correct package name
                    executable='robot',  # Replace with the correct executable name for serving robot GUI
                    name='robot_node',
                    output='screen'
                )
            ]
        ),
        # Include turtlebot3_navigation2 launch file
        TimerAction(
            period=6.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(nav2_launch_file_path),
                    launch_arguments={
                        'map': os.path.join(os.getenv('HOME'), 'map.yaml')
                    }.items()
                )
            ]
        ),
        # Include turtlebot3_gazebo launch file
        TimerAction(
            period=7.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(gazebo_launch_file_path)
                )
            ]
        ),
    ])