# Project7

# 🤖 Multi-Robot Collaboration with GUI Monitoring – ROS2 + Gazebo  

---

## 📌 Project Overview

이 프로젝트는 **Gazebo + RVIZ2 + ROS2** 환경에서 다중 로봇 협력 시뮬레이션을 구현하고,  
실시간 GUI 모니터링 시스템과 함께 각 로봇의 상태를 제어/감시할 수 있도록 설계한 실습 프로젝트입니다.

---

## 🌕 Scenario 1: Lunar Exploration Rover

- 지형이 울퉁불퉁한 달 표면을 시뮬레이션한 world 제작
- Rover 기반 로봇을 활용해 Teleop 주행 및 SLAM Mapping 시도
- 사용한 월드: https://github.com/mgonzs13/ros2_rover

🛠 **도전과제**  
- 3D 지형으로 인해 SLAM Mapping 부정확  
- 2D LiDAR로는 고저차 탐지가 불가능  
- RVIZ2의 초기 Pose 잦은 오류

📽 [달 탐사 영상 보기](https://youtu.be/VBf4qBUBhFM)

---

## 🏥 Scenario 2: 병원 내 자율 청소로봇 협업

- 실제 병원을 모사한 Gazebo 맵 제작 (로비, 병실, 진료실 등 포함)
- 청소솔이 부착된 Turtlebot3 Waffle × 2 사용
- 처음에는 구역별 맵핑 → 최종적으로 하나의 공간에서 자율 협력 주행으로 변경

🛠 **구현 기능**
- GUI를 통한 Home / Start 명령
- 로봇 위치 및 카메라 영상 실시간 표시
- ROS2 Action 기반 자율 주행 제어

📽 [최종 영상 보기](https://youtu.be/x2ECUzd6cZU)

---

## 🖥️ GUI 통합 제어 시스템

- Qt + ROS2 통합 GUI (`MultiRobotGUI`)
- 실시간 맵 시각화 (/map)
- 로봇 위치 시각화 (/pose)
- 카메라 스트리밍 토픽 수신
- 버튼 클릭 → `/home_navigation` 및 `/start_navigation` 토픽 전송

---

## 🧠 Code Architecture

### `gazebo_n2.launch.py`
- 다중 로봇 순차 스폰
- 각 로봇의 `Nav2`, `RVIZ2`, `Map Server`, `Lifecycle Manager` 실행
- 초기 Pose 설정 포함

### `tb1.py`
- 행동 루틴 처리 및 Action Client 구현
- 랜덤 목표 10회 이동, `/start_navigation` 신호 수신 시 시작
- `/home_navigation` 신호 수신 시 중단 및 대기 상태로 전환

### `gui.py`
- 카메라 콜백, 맵 콜백, 위치 콜백, 버튼 핸들러 포함
- QImage + NumPy 조합으로 맵 렌더링
- 실시간 GUI 갱신 → 카메라/맵 동기화 처리

---

## 📂 Folder Structure (예시)

```bash
📦multi_robot_simulation
├── launch/
│   └── gazebo_n2.launch.py
├── robot/
│   └── tb1.py
├── gui/
│   └── gui.py
├── models/
├── maps/
├── urdf/
├── sdf/
└── README.md
```

---

## ⚠ 주요 이슈 & 해결

| 이슈 | 해결 전략 |
|------|------------|
| RVIZ2와 Gazebo 간 위치 불일치 | 초기 Pose를 정확히 정의 |
| 맵핑 정확도 낮음 | 구역 분할 및 단일 공간 자율 주행으로 구조 변경 |
| 자율 주행 실패 | Action 통신 구조 개선 + 상태관리 로직 도입 |

---

## 👥 Team Contribution

| 이름   | 담당 역할 |
|--------|-----------|
| **박성호** | `tb1.py`, GUI 연동, 로봇 상태 처리 및 제어 루틴 |
| **김xx** | GUI 설계 및 Qt 통합, 맵/카메라 시각화 처리 |
| **모xx** | World 제작, 맵핑 및 초기 로봇 배치, 발표자료 제작 |

---

> 이 프로젝트는 ROS2 환경에서의 다중 로봇 시스템 구성 및 협동 제어,  
> 실시간 시각화와 사용자 인터페이스 설계 등 실제 로봇 운영 시스템을 프로토타입 수준에서 경험할 수 있는 기회를 제공했습니다.
