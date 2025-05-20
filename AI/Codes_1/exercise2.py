import numpy as np
import matplotlib.pyplot as plt

#시간설정
dt = 1.0
t = np.arange(0, 10, dt)

#실제속도와측정값생성
actual_velocity = 2 * t #가속도2 m/s^2
measurements = actual_velocity + np.random.normal(0, 2, size=len(t))

#초기추정값과불확실성설정
v_est = 0.0
P = 1.0

#상태천이행렬과관측행렬
A = 1.0
H = 1.0

#프로세스노이즈와측정노이즈공분산
Q = 0.1
R = 4.0

v_estimates = []
for z in measurements:
    
    #예측단계
    v_pred = A * v_est
    P_pred = A * P * A + Q

    #업데이트단계
    K = P_pred * H / (H * P_pred * H + R)
    v_est = v_pred + K * (z-H * v_pred)
    P = (1-K * H) * P_pred
    v_estimates.append(v_est)

#결과시각화
plt.plot(t, actual_velocity, label='실제속도')
plt.plot(t, measurements, label='측정값', linestyle='dotted')
plt.plot(t, v_estimates, label='추정된속도', linestyle='--')
plt.legend()
plt.show()