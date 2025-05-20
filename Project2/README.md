# Project2

# 🤖 Smart Restaurant Service Robot System  

---

## 📌 Project Overview

본 프로젝트는 **ROS2 기반 TurtleBot3**를 활용하여 **스마트 음식 배달 및 관제 시스템**을 구현한 것입니다.  
GUI를 통한 주문 접수부터 주방 상태 모니터링, 자율 주행을 통한 서빙 로봇 연동까지 모두 포함된 통합 서비스 로봇 시스템입니다.

### 🧾 주요 구성

- **Table Order GUI**: 메뉴 주문, 결제, 로봇 호출
- **Kitchen Display GUI**: 주문 수락, 상태 관리, 배송 제어
- **Serving Robot GUI**: 로봇 실시간 위치 추적, 자율 주행 및 복귀
- **Turtlebot3 + Navigation2**: 실제 주행 로봇 및 맵 기반 내비게이션
- **ROS2 기반 통신**: Service / Publisher / Subscriber / Action 활용

🎥 [📽 시연 영상 보기](https://youtu.be/y0oaHXsJol4)

---

## 🛠 주요 기능 요약

| 모듈                  | 설명 |
|-----------------------|------|
| Table Order GUI       | 주문 추가/삭제, 결제, 로봇 호출 기능 |
| Kitchen Display GUI   | 주문 수락/거절, 상태 업데이트, 배송 제어 |
| Serving Robot GUI     | 실시간 맵 표시, 위치 추적, 배송 시작 및 복귀 |
| SQLite DB 연동        | 주문 내역 저장 및 조회 기능 |
| ROS2 통신 구조        | Service / Topic / Action 기반 모듈 연동 |
| 시각화                | OccupancyGrid → NumPy + QImage로 실시간 GUI 표시 |

---

## 📂 폴더 구조 예시

```bash
📦restaurant_delivery_system
├── table_order_gui/
├── kitchen_display_gui/
├── serving_robot_gui/
├── database/
├── launch/
├── msgs/
├── srv/
├── README.md
└── requirements.txt
```

---

## 💻 사용 기술

- **ROS2 Foxy + Python**
- **TurtleBot3 Burger**
- **PyQt5 GUI**
- **SQLite DB**
- **OccupancyGrid + QImage 시각화**
- **Service / Publisher / Subscriber / Action 통신**

---

## ⚠️ 주요 이슈 & 해결 전략

### ⚠ 시스템 동시 실행 시 충돌
- 문제: 여러 GUI와 launch 파일 동시에 실행 시 충돌 발생
- 해결: `TimerAction`을 활용해 시간차 실행으로 분산

### ⚠ 로봇 위치 실시간 GUI 표시 지연
- 문제: ROS topic 처리 속도와 GUI 반영 간 지연
- 해결: `NumPy + QImage` 조합으로 OccupancyGrid 데이터 시각화 처리

### ⚠ ROS2 서비스 통신 구조 구현 난이도
- 문제: 서비스 구조 설계와 동기화 어려움
- 해결: 간단한 구조부터 점진적으로 확대 설계, 콜백 구조로 안정성 확보

---

## 👥 Team Contribution

| 이름   | 담당 역할 |
|--------|-----------|
| **박성호** | Project Manager, Serving Robot GUI, Kitchen Display GUI, ROS2 Action 통신, 발표자료 제작 |
| **김XX** | Table Order GUI, Kitchen GUI, ROS2 service 통신, 실시간 맵 표시 |
| **모XX** | Table Order GUI, SQLite 연동 및 시각화, 시스템 통합 기획 |

---

> 본 프로젝트는 **스마트 레스토랑 서비스 시스템**의 프로토타입을 목표로 구성되었으며,  
> ROS2, GUI, 자율 주행 로봇 및 데이터베이스를 종합적으로 연동한 **All-in-One 시스템 통합 경험**을 제공합니다.
