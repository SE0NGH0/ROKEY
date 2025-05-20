import numpy as np
import matplotlib.pyplot as plt

#실제위치와측정값생성
actual_position = np.linspace(0, 10, 11)
measurements = actual_position + np.random.normal(0, 1, size=11)

 #초기추정값과불확실성설정
x_est = 0.0
P = 1.0

#상태천이행렬과관측행렬
A = 1.0
H = 1.0

#프로세스노이즈와측정노이즈공분산
Q = 0.0001
R = 1.0

x_estimates = []

for z in measurements:
    #예측단계
    x_pred = A * x_est
    P_pred = A * P * A + Q
    #업데이트단계
    K = P_pred * H / (H * P_pred * H + R)
    x_est = x_pred + K * (z-H * x_pred)
    P = (1-K * H) * P_pred
    x_estimates.append(x_est)

#결과시각화
plt.plot(actual_position, label='실제위치')
plt.plot(measurements, label='측정값', linestyle='dotted')
plt.plot(x_estimates, label='추정된위치', linestyle='--')
plt.legend()
plt.show()