from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 定义面积、卧室数、位置
x = [[100, 2, 1],
[150, 3, 2],
[120, 2, 2],
[80, 1, 1]]
# 对应的售价
y = [300, 450, 350, 220]

# 数据集分割为训练集和测试级
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(x_train, y_train)
predictions = model.predict(x_test)
print(predictions)