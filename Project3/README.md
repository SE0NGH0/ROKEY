# Project3

# 📦 Fulfillment Automation Simulation Project  

---

## 📌 Project Overview

본 프로젝트는 ROS2 기반 TurtleBot3, Arduino, Manipulator, YOLOv8 등을 활용하여  
**물류 자동화 시뮬레이션 (Fulfillment Service)** 환경을 구축한 것입니다.

### 🧾 핵심 구성 요소

- **GUI 인터페이스**: CCTV 뷰, 객체 인식, ArUco 마커 위치 계산, Email 전송
- **TurtleBot3 + Manipulator-X**: 객체 인식 → 박스 집기 → 이동 → 컨베이어 적재
- **YOLOv8**: 박스 색상 기반 객체 인식 (파란색/빨간색)
- **Aruco 마커**: 위치 추적 및 거리 계산
- **Conveyor 제어**: Arduino 시리얼 통신 기반 ON/OFF

🎥 [📽 시연 영상 보기](https://youtube.com/shorts/Ix2YcW-HFpI)

---

## 🛠 기능 상세 설명

### ✅ TurtleBot3 + Manipulator 동작 흐름

1. YOLOv8 기반 객체 탐지 (빨간 박스, 파란 박스)
2. 객체 Tracking → 화면 중심에 맞춤
3. 객체 중심 정렬 시 Manipulator-X 동작
4. Joint 각도 설정 → 거리 조절 → Gripper로 집기
5. 컨베이어 위치로 이동 후 박스 적재
6. 지정된 높이까지 하강 후 박스 내려놓음
7. 다음 객체 탐지 후 반복 수행

### ✅ GUI 기능

- **World View Cam**: 카메라 영상 실시간 송출
- **Aruco 마커 인식**: 마커 좌표 및 거리 계산 표시
- **YOLO View**: YOLOv8 객체 인식 결과 시각화
- **Conveyor ON/OFF 버튼**: GUI → Serial → Arduino 제어
- **이메일 발송 기능** 포함

---

## 📂 폴더 구조 예시

```bash
📦fulfillment_simulation
├── gui/
│   ├── world_view_cam.py
│   ├── yolo_cam.py
│   └── system.py
├── robot/
│   ├── manipulator_controller.py
│   ├── yolov8_tracker.py
│   └── turtlebot_driver.py
├── arduino/
│   └── conveyor_control.ino
├── README.md
└── requirements.txt
```

---

## ⚠️ Key Issues

| 문제 항목                | 설명 |
|--------------------------|------|
| TurtleBot3 상태 확인 부족 | 장비 점검 미흡으로 초기 동작 오류 발생 |
| Manipulator Joint 제어 | YOLO 위치 기준으로 Joint 각도 보정이 어려움 |

---

## 👥 Team Contribution

| 이름   | 담당 역할 |
|--------|-----------|
| **박성호** | Project Manager, Manipulator 동작 구현, YOLO 연동, 전체 통합 |
| **김xx** | GUI 개발, ArUco 마커 추적, 이메일 송신 기능 |
| **모xx** | YOLOv8 객체 탐지, GUI 연동, 프로젝트 문서 작성 |

---

> 본 프로젝트는 실제 Fulfillment 환경을 모사한 가상 시스템으로,  
> **로봇 제어, 시각 인식, GUI, 시리얼 통신** 등 다양한 기술을 통합하여 로봇 자동화 프로세스를 체험할 수 있는 구성으로 설계되었습니다.
