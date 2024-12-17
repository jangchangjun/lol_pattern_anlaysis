import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# 데이터 로드
df = pd.read_json("./final_target_data.json")

# Gap 피처 정의
gap_at14 = ["at14dpmdiff", "at14dtpmdiff", "at14cspmdiff", "at14gpmdiff",
            "at14xpmdiff", "at14dpddiff", "at14dpgdiff"]

gap_af14 = ["af14dpmdiff", "af14dtpmdiff", "af14cspmdiff", "af14gpmdiff",
            "af14xpmdiff", "af14dpddiff", "af14dpgdiff"]

# at14와 af14의 Gap 피처 통합
gap_features = gap_at14 + gap_af14

# X와 y 설정
X = df[gap_features]
y = df['targetWin'].astype(int)

# === 상관계수 계산 및 피처 선택 ===
correlations = X.corrwith(y)  # y와의 상관계수 계산
threshold = 0.1  # 상관계수 임계값 (절대값 기준)
selected_features = correlations[correlations.abs() > threshold].index.tolist()

# 상관계수 확인
print("\n=== 피처 상관계수 ===")
print(correlations)

# 선택된 피처 출력
print("\n=== 상관계수 기반 선택된 피처 ===")
print(selected_features)

# 선택된 피처만 사용
X = X[selected_features]

# === 데이터 정규화 ===
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# === 학습 데이터와 테스트 데이터 분리 ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# === Logistic Regression 모델 학습 ===
model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train, y_train)

# 예측 및 평가
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auroc = roc_auc_score(y_test, y_pred_proba)

# 결과 출력
print("\n=== Logistic Regression 모델 ===")
print(f"정확도 (Accuracy): {accuracy:.4f}")
print(f"AUROC: {auroc:.4f}")

