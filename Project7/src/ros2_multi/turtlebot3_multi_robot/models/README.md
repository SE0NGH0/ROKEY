
# 🧱 Custom Gazebo Models for Simulation Environments  
**ROKEY BOOT CAMP – Simulation Assets**

---

## 📦 Overview

이 저장소는 ROS2 + Gazebo 기반의 시뮬레이션 환경을 구축할 때 사용할 수 있는  
다양한 카테고리의 **3D 모델 리소스**들을 포함하고 있습니다.

모델들은 **의료 시뮬레이션**, **주거 환경**, **소매점**, **창고 작업장**, **병원 운영** 등에 적합하며,  
TurtleBot, 서비스 로봇, 협동로봇 시뮬레이션에서 사용할 수 있도록 구성되어 있습니다.

---

## 🗂 Directory Structure

```
models/
├── AdjTable
├── AnesthesiaMachine
├── aws_robomaker_hospital_*
├── aws_robomaker_residential_*
├── aws_robomaker_warehouse_*
├── aws_robomaker_retail_*
├── BedsideTable
├── BloodPressureMonitor
├── BMWCart
├── Chair
├── Drawer
├── ElderLadyPatient
└── ...
```

> 참고: `aws_robomaker_*` 네이밍은 Amazon Web Services에서 제공한 고해상도 모델을 의미합니다.

---

## 🏥 주요 카테고리 및 예시

### 🏥 의료 환경
- `AnesthesiaMachine`, `BloodPressureMonitor`, `BedTable`, `BMWCart`, `CGMClassic`
- `aws_robomaker_hospital_floor_*`, `aws_robomaker_hospital_nursesstation_01`

### 🛋️ 주거 환경
- `aws_robomaker_residential_Sofa_01`, `Refrigerator_01`, `KitchenCabinet_01`
- 다양한 액자(`PortraitA~E`), TV, Trash 등

### 🛒 상업 환경
- `aws_robomaker_retail_BookshelfB_01`, `Computer_01`

### 🏭 창고 환경
- `aws_robomaker_warehouse_ClutteringA_01`, `ClutteringC_01`

---

## 🛠 사용 방법

1. `models/` 폴더를 Gazebo 모델 경로에 추가:

```bash
export GAZEBO_MODEL_PATH=${GAZEBO_MODEL_PATH}:/path/to/models
```

2. `sdf` 또는 `world` 파일 내에서 해당 모델 참조:

```xml
<include>
  <uri>model://AnesthesiaMachine</uri>
</include>
```

---

## 🧪 적용 예시

이 모델들은 다음과 같은 프로젝트에서 활용될 수 있습니다:

- 병원 시나리오 기반 SLAM 자율주행 시뮬레이션
- ROS2 기반 협동로봇 간병 서비스
- 물류 로봇의 장애물 회피 테스트
- 로봇팔의 객체 인식 및 픽업 테스트 등

---

## 👥 Contributors

- 박성호 · 김문영 · 모승휘  
- *Rokey Boot Camp Simulation 팀*

---

> 본 모델들은 실습 및 연구 목적에 사용되며, 일부 모델은 AWS 및 오픈소스 Gazebo 라이브러리 기반입니다.

