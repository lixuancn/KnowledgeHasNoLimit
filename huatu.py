import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties

# 使用系统已安装的中文字体
font = FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc')  # macOS系统自带字体

# 数据准备
sizes = [16, 24, 48, 12]  # 四个扇形大小相同
colors = ['#FFD700', '#1E90FF', '#FF8C00', '#3CB371']  # 扇形颜色
labels = ['方向POC', '高潜', '常规', '尾部']  # 每个扇形的标签

sizes = [32, 52, 16]  # 四个扇形大小相同
colors = ['#FFD700', '#1E90FF', '#FF8C00']  # 扇形颜色
labels = ['熟悉核心业务', '熟悉部分业务', '实习/试用']  # 每个扇形的标签

# 创建饼状图
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
       shadow=False, startangle=90, textprops={'fontproperties': font})

# 设置标题（增大字体到16，并增加与图的间距）
ax.set_title('业务熟悉度',
             fontproperties=matplotlib.font_manager.FontProperties(
                 fname='/System/Library/Fonts/STHeiti Medium.ttc',
                 size=16),
             pad=20)  # 增加标题与图的间距

# 确保图形是圆形
ax.axis('equal')

# 显示图形
plt.show()