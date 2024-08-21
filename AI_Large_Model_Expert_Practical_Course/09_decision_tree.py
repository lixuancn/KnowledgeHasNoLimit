import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree

x = np.array([
    [0,2,0], # 晴天，高温，无风
    [1,1,1],# 阴天，中温，微风
    [2,0,2],# 雨天，低温，强风
    [0,0,2],# 晴天，低温，强风
])
y = np.array([0,1,2,4]) # 分别对应去野餐、去博物馆、在家看书

clf = DecisionTreeClassifier(max_depth=5, random_state=42)
clf.fit(x,y)
predict = clf.predict(np.array([[1,2,2]]))
print(predict)

plt.figure(figsize=(20, 10))
plot_tree(clf, filled=True, feature_names=["天气", "温度", "风速"], class_names=["去野餐", "去博物馆", "在家看书", "去烤火"], rounded=True, fontsize=12)
plt.show()
