import numpy as np
import matplotlib.pyplot as plt

#시뮬레이션파라미터
dt = 0.1
t_end = 50
t = np.arange(0, t_end, dt)

#차량파라미터
v = 15.0 # m/s

# PID제어기이득
Kp = 0.3
Ki = 0.05
Kd = 0.2

#초기화
x = 0.0
y = 0.0
theta = 0.0
delta = 0.0
integral = 0.0
prev_cte = 0.0

#로그저장용리스트
x_history = []
y_history = []
delta_history = []
cte_history = []
for ti in t:
    #도로의곡률계산
    kappa = 0.01 * np.sin(0.1 * x)

    #도로의목표방향계산
    theta_desired = kappa * x

    #횡방향오차계산
    cte = y-(0.5 * np.cos(0.1 * x))

    # PID제어기계산
    integral += cte * dt
    derivative = (cte-prev_cte) / dt
    prev_cte = cte
    delta =-(Kp * cte + Ki * integral + Kd * derivative)

    #차량의위치및방향업데이트(자전거모델)
    x += v * np.cos(theta) * dt
    y += v * np.sin(theta) * dt
    theta += (v / 2.5) * delta * dt

    #로그저장
    x_history.append(x)
    y_history.append(y)
    delta_history.append(delta)
    cte_history.append(cte)

#결과시각화
# 1.차량궤적과도로곡선
road_x = np.linspace(0, max(x_history), len(x_history))
road_y = 0.5 * np.cos(0.1 * road_x)
plt.figure(figsize=(10, 5))
plt.plot(road_x, road_y, 'g--', label='도로경로')
plt.plot(x_history, y_history, 'b-', label='차량궤적')
plt.xlabel('x위치(m)')
plt.ylabel('y위치(m)')
plt.title('차량궤적과도로경로')
plt.legend()
plt.grid(True)
plt.show()

# 2.횡방향오차그래프
plt.figure(figsize=(10, 5))
plt.plot(t, cte_history, label='횡방향오차')
plt.xlabel('시간(s)')
plt.ylabel('오차(m)')
plt.title('시간에따른횡방향오차')
plt.legend()
plt.grid(True)
plt.show()

# 3.조향각도그래프
plt.figure(figsize=(10, 5))
plt.plot(t, delta_history, label='조향각도')
plt.xlabel('시간(s)')
plt.ylabel('조향각도(rad)')
plt.title('시간에따른조향각도')
plt.legend()
plt.grid(True)
plt.show()
