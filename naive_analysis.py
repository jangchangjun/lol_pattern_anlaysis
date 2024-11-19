import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, classification_report, confusion_matrix

# 데이터 로드
df = pd.read_json("./final_target_data.json")

# metrics 정의
metrics = {
    'combat_at14': ['at14killsRatio', 'at14deathsRatio', 'at14assistsRatio',
                    'at14solokillsRatio', 'at14solodeathsRatio',
                    'at14dpm', 'at14dtpm'],

    'combat_af14': ['af14killsRatio', 'af14deathsRatio', 'af14assistsRatio',
                    'af14solokillsRatio', 'af14solodeathsRatio',
                    'af14dpm', 'af14dtpm'],

    'operation_at14': ["at14cspm", "at14gpm", "at14xpm", "at14dpd", "at14dpg"],

    'operation_af14': ["af14cspm", "af14gpm", "af14xpm", "af14dpd", "af14dpg"],

    'gap_at14': ["at14dpmdiff", "at14dtpmdiff", "at14cspmdiff", "at14gpmdiff",
                 "at14xpmdiff", "at14dpddiff", "at14dpgdiff"],

    'gap_af14': ["af14dpmdiff", "af14dtpmdiff", "af14cspmdiff", "af14gpmdiff",
                 "af14xpmdiff", "af14dpddiff", "af14dpgdiff"]
}

# 목표 변수
y = df['targetWin'].astype(int)

# 가중치 설정 (combat_af14 전용)
weights = [0.25, -0.05, 0.15, 0.15, -0.05, 0.3, -0.05]

for key, features in metrics.items():
    print(f"\n--- {key} ---")

    # 각 지표 집합의 특징 선택
    x = df[features].fillna(0)

    # 스케일링 적용 (정규화 or 표준화)
    from sklearn.preprocessing import MinMaxScaler

    # combat_af14 지표 스케일링
    scaler = MinMaxScaler()
    x_scaled_minmax = scaler.fit_transform(df[metrics['combat_af14']])
    weighted_sums_minmax = np.dot(x_scaled_minmax, weights)
    df['combat_af14_weighted_minmax'] = weighted_sums_minmax

    # 'combat_af14' 가중 평균 처리
    if key == 'combat_af14':
        # 가중 평균 계산 (스케일링된 값 사용)
        weighted_sums = np.dot(x_scaled_minmax, weights)
        df['combat_af14_weighted'] = weighted_sums
        print("Combat AF14 Weighted Example (First 5):", df['combat_af14_weighted'].head())

    # 로지스틱 회귀 모델 설정 및 학습
    model = LogisticRegression()
    model.fit(x_scaled_minmax, y)

    # 예측 수행
    y_pred = model.predict(x_scaled_minmax)
    y_pred_prob = model.predict_proba(x_scaled_minmax)[:, 1]

    # 모델 계수 및 평가
    print("모델 계수 (theta) : ", model.coef_)
    print("모델 절편 (b) : ", model.intercept_)
    print("평균 제곱 오차 (MSE) : ", mean_squared_error(y, y_pred))
    print("분류 보고서 : ")
    print(classification_report(y, y_pred))
    print("혼돈 행렬 : ")
    print(confusion_matrix(y, y_pred))
