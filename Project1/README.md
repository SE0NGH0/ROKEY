# Project1

# 🛡️ AI Vision Surveillance System  

---

## 📌 Project Overview

본 프로젝트는 **TurtleBot3**와 **ROS2**, **YOLO 기반의 객체 탐지 모델**을 활용하여  
AI 비전 기반의 감시 간이 시스템을 구축한 것입니다.

### 🔍 주요 목표
- 실시간 객체 탐지 및 경고 시스템 구현
- ROS 기반 시스템 통합 및 다중 센서 정보 처리
- 감시 카메라와 AMR 카메라 데이터를 통한 추적 기능

---

## 🧠 주요 기능

| 기능 모듈             | 설명 |
|----------------------|------|
| **Security Alert**   | 객체 탐지 및 경고 메시지 출력 |
| **System Monitor**   | 시스템 상태 및 카메라 출력 시각화 |
| **AMR Controller**   | SLAM 기반 이동, 객체 추적 및 거리 추정 |
| **정보 통합 및 시각화** | 감시 카메라 & AMR 카메라 데이터 종합 보고 |
| **로그인 기능**       | 사용자를 식별하고 접근 제어 |

- **YOLO 기반 Object Detection**
- **SLAM 기반 Mapping 및 Tracking**
- **멀티 카메라 및 센서 통합 출력**

🎥 [📽 실행 영상 링크](https://youtu.be/NdKa7HHMdJo)

---

## 🧩 기술 구성

- **Hardware**: TurtleBot3 Burger
- **OS & Middleware**: ROS2 Foxy, Ubuntu 20.04
- **Vision**: OpenCV + YOLOv5
- **Mapping & Localization**: SLAM Toolbox
- **통신**: ROS2 Topic, Service, Node 기반 메시지 송수신
- **언어**: Python, C++

---

## ⚠️ Key Issues & Challenges

### ⏱ 시간 및 장비 접근성 제한
- 실 장비 테스트 시간이 매우 제한되어, 코드 리뷰와 시뮬레이션을 병행하여 효율성 확보

### 🧩 ROS 이해도 부족
- ROS2 노드 구조와 메시지 통신 구조에 대한 경험 부족
- 반복 학습 및 에러 로그 분석을 통해 보완

### 🧵 시스템 통합의 어려움
- 개별 기능은 동작하지만, 전체 시스템 통합 시 충돌 및 메시지 비동기 문제가 빈번히 발생
- 모듈화 설계와 분산 처리 방식으로 문제 해결

---

## 🔧 개선 사항 제안

| 개선 항목                     | 설명 |
|------------------------------|------|
| 객체 탐지 정확도 향상        | YOLO 성능 개선 + LiDAR 통합 고려 |
| 실시간 동적 학습 시스템 구축 | 환경 변화에 적응 가능한 탐지 성능 확보 |
| 에너지 효율 최적화           | 필요한 순간에만 연산 수행 + 경로 최적화 |

---

## 🧠 Lessons Learned

- **ROS 통신 구조와 노드 설계의 중요성** 체감
- **기능 모듈화**가 시스템 통합 및 유지보수에 필수적
- **하드웨어 테스트의 중요성** → 코드가 정상이더라도 실제 장비에서는 예외 발생 가능

---

## 👥 Team Contribution

| 이름   | 담당 업무 |
|--------|-----------|
| **박성호** | 프로젝트 매니저, Security Alert & System Monitor 기능 설계 및 구현, 발표자료 제작 |
| **김XX** | Security Alert, System Monitor 함수 구현, 시스템 디자인 문서 작성 |
| **모XX** | AMR Controller 함수 설계 및 구현, 시스템 요구사항 문서 작성 |

---

## 📂 폴더 구조 예시 (추천)

```bash
📦ai_vision_surveillance
├── src/
│   ├── security_alert/
│   ├── system_monitor/
│   ├── amr_controller/
│   └── utils/
├── launch/
├── config/
├── README.md
└── requirements.txt
```

---

## 🏁 실행 환경

```bash
OS: Ubuntu 20.04  
ROS2: Foxy  
Python >= 3.8  
```

---

> 본 프로젝트는 ROKEY Boot Camp 산출물이며, 실제 TurtleBot3 장비와 ROS2를 기반으로 AI 비전 감시 시스템의 프로토타입을 구현하였습니다.
