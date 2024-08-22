import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

iris = load_iris()
x, y = iris.data, iris.target
print(x)
print(y)

rf = RandomForestClassifier(n_estimators=3, random_state=42) # 3棵树
rf.fit(x, y)

# 绘制
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 5), dpi=100)
for index in range(0, 3):
    plot_tree(rf.estimators_[index], feature_names=iris.feature_names, class_names=iris.target_names, filled=True, ax=axes[index])
    axes[index].set_title(f'Tree {index + 1}')
plt.tight_layout()
plt.show()