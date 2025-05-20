import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

# 데이터베이스 연결 및 데이터 가져오기
conn = sqlite3.connect('/home/msh/project_ws/database.db', check_same_thread=False)
cursor = conn.cursor()

# 테이블의 데이터 가져오기
cursor.execute("SELECT item_name, SUM(quantity) FROM completed_orders GROUP BY item_name")
item_sales = cursor.fetchall()

cursor.execute("SELECT timestamp, item_name, quantity FROM completed_orders")
time_sales = cursor.fetchall()

conn.close()

# 각 아이템의 가격 설정
prices = {
    'Burger': 5.99,
    'Pizza': 8.99,
    'Salad': 4.99,
    'Pasta': 7.49
}

# 판매량 비교 막대그래프 및 시간대별 매출 변화 그래프 생성
# 데이터프레임으로 변환하여 처리
df = pd.DataFrame(time_sales, columns=['timestamp', 'item_name', 'quantity'])
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 매출 계산
df['revenue'] = df.apply(lambda row: row['quantity'] * prices[row['item_name']], axis=1)
df.set_index('timestamp', inplace=True)

# 일일 매출 합계 계산
df_resampled = df.resample('D').sum()

fig, axs = plt.subplots(1, 2, figsize=(18, 6))

# 판매량 비교 막대그래프 및 총 판매량 막대그래프 (왼쪽)
item_names = [item[0] for item in item_sales]
quantities = [item[1] for item in item_sales]
item_names.append('Total')
quantities.append(sum(quantities))

# 가장 많이 판매된 아이템의 수량 확인
max_quantity = max(quantities[:-1])  # 총 판매량('Total') 제외
colors = ['blue' for _ in quantities]
for i, quantity in enumerate(quantities[:-1]):
    if quantity == max_quantity:
        axs[0].text(i, quantity + 3, 'Most Preferred!', color='red', ha='center', fontsize=10)  # 수치와 겹치지 않도록 더 위에 표시

colors[-1] = 'orange'  # 총 판매량 색상

bars = axs[0].bar(item_names, quantities, color=colors)
axs[0].set_xlabel('Item Name')
axs[0].set_ylabel('Total Quantity Sold')
axs[0].set_title('Total Sales Comparison by Item and Overall')
axs[0].set_ylim(0, max(quantities) * 1.2)  # y축 범위 설정 (0부터 시작하여 여유를 둠)

# 각 막대 위에 수치 표시
for bar, quantity in zip(bars, quantities):
    axs[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f'{quantity}', ha='center', va='bottom', fontsize=10)

# 일일 매출 변화 막대그래프 (오른쪽)
df_resampled_dates = df_resampled.index.strftime('%Y-%m-%d')
axs[1].bar(df_resampled_dates, df_resampled['revenue'], color='green')
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Total Revenue ($)')
axs[1].set_title('Daily Revenue Over Time')
axs[1].set_ylim(0, df_resampled['revenue'].max() * 1.2)  # y축 범위 설정 (0부터 시작하여 여유를 둠)
axs[1].tick_params(axis='x', rotation=45)

# 각 막대 위에 수치 표시
for i, revenue in enumerate(df_resampled['revenue']):
    axs[1].text(i, revenue + 0.5, f'{revenue:.2f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()
