import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, classification_report, confusion_matrix

# 데이터 로드
df = pd.read_json("./final_target_data.json")

combat_at14 = ['at14killsRatio', 'at14deathsRatio',
               'at14dpm', 'at14dtpm']

combat_af14 = ['af14killsRatio', 'af14deathsRatio', 'af14assistsRatio']

operation_at14 = ["at14cspm", "at14gpm", "at14xpm", "at14dpd", "at14dpg"]

operation_af14 = ["af14cspm", "af14gpm", "af14xpm", "af14dpd", "af14dpg"]

gap_at14 = ["at14dpmdiff", "at14dtpmdiff", "at14cspmdiff", "at14gpmdiff",
           "at14xpmdiff"]

gap_af14 = ["af14dpmdiff", "af14dtpmdiff", "af14cspmdiff", "af14gpmdiff",
             "af14xpmdiff"]

x = df[combat_af14]
y = df['targetWin'].astype(int)

from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, roc_auc_score

model = LinearRegression()
model.fit(x, y)

print("모델 계수 (theta) : ", model.coef_)
print("모델 절편 (b) : ", model.intercept_)

y_pred = model.predict(x)

threshold = 0.5
y_pred_class = (y_pred >= threshold).astype(int)

accuracy = accuracy_score(y, y_pred_class)
auroc = roc_auc_score(y, y_pred)

print(f"정확도 (Accuracy, threshold: {threshold}): {accuracy}")
print(f"AUROC: {auroc}")

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score

# 데이터 로드 (JSON 파일로 가정)
df = pd.read_json("./final_target_data.json")

# 사용할 피처 그룹 정의
combat_af14 = ['af14killsRatio', 'af14deathsRatio', 'af14dpm', 'af14dtpm']
operation_af14 = ["af14cspm", "af14gpm", "af14xpm", "af14dpd", "af14dpg"]
gap_af14 = ["af14dpmdiff", "af14dtpmdiff", "af14cspmdiff", "af14gpmdiff", "af14xpmdiff"]

# 타겟 변수
target = "targetWin"

# 그룹별 데이터를 표준화하고 학습
def train_group(features, group_name):
    print(f"\n[{group_name}] 그룹 모델 학습 및 평가")

    # 스케일러 선택 (MinMaxScaler 또는 StandardScaler)
    scaler = MinMaxScaler()  # Min-Max 정규화
    # scaler = StandardScaler()  # 표준화

    # 데이터 정규화
    x = scaler.fit_transform(df[features])
    y = df[target].astype(int)

    # 모델 학습
    model = LogisticRegression()
    model.fit(x, y)

    # 예측 및 평가
    y_pred = model.predict_proba(x)[:, 1]  # 승리 확률
    y_pred_class = (y_pred >= 0.5).astype(int)  # Threshold=0.5

    # 성능 측정
    accuracy = accuracy_score(y, y_pred_class)
    auroc = roc_auc_score(y, y_pred)

    print("모델 계수 (theta):", model.coef_)
    print("모델 절편 (b):", model.intercept_)
    print(f"정확도 (Accuracy): {accuracy:.2f}")
    print(f"AUROC: {auroc:.2f}")
    return model

# 각 피처 그룹별로 모델 학습 및 평가
combat_model = train_group(combat_af14, "Combat")
operation_model = train_group(operation_af14, "Operation")
gap_model = train_group(gap_af14, "Gap")

# 통합 모델 학습 및 평가 (combat과 gap의 비중을 증가)
print("\n[Combined] 그룹 모델 학습 및 평가")

# 그룹별 합산 계산
df['combat_sum'] = df[combat_af14].sum(axis=1)
df['gap_sum'] = df[gap_af14].sum(axis=1)
df['operation_sum'] = df[operation_af14].sum(axis=1)

# 그룹별 정규화
scaler = MinMaxScaler()
df[['combat_sum', 'gap_sum', 'operation_sum']] = scaler.fit_transform(df[['combat_sum', 'gap_sum', 'operation_sum']])

# 가중치 설정 (combat과 gap의 비중 증가)
combat_weight = 0.1
gap_weight = 0.6
operation_weight = 0.3

# combined 값 계산
df['combined'] = (
    df['combat_sum'] * combat_weight +
    df['gap_sum'] * gap_weight +
    df['operation_sum'] * operation_weight
)

# combined 값을 사용하여 모델 학습 및 평가
combined_model = train_group(['combined'], "Combined")


# 다 때려치고 각각의 요소가 win에 관계해 얼마나 큰 상관계수를 가진지 알아본 뒤, 수치가 무의미한것들은 삭제 글고...그 상관계수에 맞춰 정규화진행후, combat, gap, opration을 맞춰 정확도 예측하기.
# 각각의 데이터열 선택에 대해 합리적 설명이 가능하게 그래프나 그림을 통해 표현하기 구글에 검색해보셈 ! 챗지피티짱!
#요런느낌으로 진행 ㄱㄱ
