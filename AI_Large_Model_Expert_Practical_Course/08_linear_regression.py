import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# 线性回归

# 定义数据
x = np.array([35,45,40,60,65]).reshape(-1,1)
y = np.array([30,40,35,60,65])

# 模型拟合
model = LinearRegression()
model.fit(x, y)

# 预测面积50平的价格
predict_area = np.array([50]).reshape(-1, 1)
predict_price = model.predict(predict_area)

print(predict_price)

plt.scatter(x, y)
plt.plot(x, model.predict(x), color='red')
plt.title('房价预测')
plt.xlabel('面积')
plt.ylabel('售价')
plt.show()