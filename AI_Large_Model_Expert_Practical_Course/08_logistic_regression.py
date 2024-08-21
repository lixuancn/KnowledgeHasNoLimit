import numpy as np
from sklearn.linear_model import LogisticRegression

# 逻辑回归

# 学习时间和考试及格的关系
x = np.array([[10], [20], [30], [40], [50]])
y = np.array([0, 0, 1, 1, 1])

model = LogisticRegression()
model.fit(x, y)

prediction_probability = model.predict_proba([[25]])
prediction = model.predict([[25]])
print(f"通过考试的概率为：{prediction_probability[0][1]:.2f}")
print(f"预测分类：{'通过' if prediction[0] == 1 else '未通过'}")