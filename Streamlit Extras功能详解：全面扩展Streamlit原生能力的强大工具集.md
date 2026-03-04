# Streamlit Extras 功能详解：全面扩展 Streamlit 原生能力的强大工具集

## 一、引言：Streamlit Extras 概述

**Streamlit Extras**是一个由 Streamlit 官方团队成员 Arnaud Miribel 开发的 Python 库，旨在为 Streamlit 应用提供额外的功能和组件。这个库将各种有用的 Streamlit 代码片段（extras）整合在一起，包含了超过 20 个功能或视觉增强组件，让开发者的生活更轻松，应用更美观。

从定位来看，**Streamlit Extras 并非官方核心库的一部分**，而是一个第三方扩展包[(23)](https://www.restack.io/docs/streamlit-knowledge-pip-install-streamlit-extras)。它的设计理念是作为一个可安装的`utils.py`文件，充满了小型、实用的 Streamlit 组件。每个 extra 都有自己的目录和`__init__.py`文件，遵循统一的项目结构。

该库的主要特点包括：



* **易于安装**：通过`pip install streamlit-extras`即可获取所有功能

* **模块化设计**：每个 extra 都是独立的模块，可按需导入使用

* **持续更新**：基于社区贡献不断扩展新功能

* **Python 优先**：大部分功能仅用 Python 实现，少数使用 CSS/HTML hack

本文将从 UI 增强、数据处理、AI 集成等多个维度，全面梳理 Streamlit Extras 相对于原生 Streamlit 的新增功能，并提供详细的使用示例和对比分析。

## 二、UI 增强功能：提升用户界面体验

### 2.1 视觉效果增强

Streamlit Extras 在视觉效果方面提供了多项独特功能，这些都是原生 Streamlit 完全不具备的：

**1. 飘落动画效果（Let It Rain）**

`let_it_rain`函数可以在应用中添加飘落的 emoji 动画，支持多种自定义参数[(96)](https://www.aidoczh.com/streamlit/develop/api-reference.html)：



```
from streamlit\_extras.let\_it\_rain import rain

rain(

&#x20;   emoji="🎈",  # 飘落的emoji类型

&#x20;   font\_size=54,  # emoji大小

&#x20;   falling\_speed=5,  # 下落速度

&#x20;   animation\_length="infinite"  # 动画时长

)
```

这个功能类似于原生的`st.balloons()`，但提供了更多自定义选项，如不同的 emoji 类型、速度控制和持续时[(99)](https://discuss.streamlit.io/t/how-to-create-something-like-st-balloons/55740/3)间。

**2. 彩色标题（Colored Headers）**

`colored_header`允许创建带颜色背景的标题，这是原生 Streamlit 完全没有的功能：



```
from streamlit\_extras.colored\_header import colored\_header

colored\_header(

&#x20;   label="My Colored Title",  # 标题文本

&#x20;   description="This is a description",  # 副标题

&#x20;   color\_name="blue-70"  # 颜色名称（使用Tailwind CSS色系）

)
```

**3. 徽章系统（Badges）**

Badges 功能允许在应用中添加社交徽章或状态标识，这是原生 Streamlit 缺乏的功能：



```
from streamlit\_extras.badges import badge

badge(type="github", name="arnaudmiribel/streamlit-extras")

badge(type="pypi", name="streamlit-extras")
```

### 2.2 布局和导航增强

**4. 浮动操作按钮（Floating Button）**

`floating_button`提供了一个悬浮在页面底部的操作按钮，支持点击事件和自定义样式：



```
from streamlit\_extras.floating\_button import FloatingButton

floating\_button = FloatingButton(

&#x20;   icon="➕",  # 按钮图标

&#x20;   text="Add Item",  # 按钮文本

&#x20;   on\_click=lambda: st.session\_state.update({"counter": st.session\_state.get("counter", 0) + 1})

)

floating\_button()
```

**5. 网格布局系统（Grid）**

Grid 系统提供了比原生`st.columns`更灵活的布局方式，支持响应式设[(78)](https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-grid-overview)计：



```
from streamlit\_extras.grid import grid

\# 创建2x3网格

g = grid(2, 3)

\# 在网格中放置元素

g\[0, 0].text("Cell 1")

g\[0, 1].text("Cell 2")

g\[1, 0].text("Cell 4")

g\[1, 1].text("Cell 5")
```

**6. 底部容器（Bottom Container）**

`bottom_container`确保内容始终显示在页面底部，这在需要固定底部栏时非常有用：



```
from streamlit\_extras.bottom\_container import bottom\_container

with bottom\_container():

&#x20;   st.text("This will always be at the bottom of the page")
```

### 2.3 交互组件增强

**7. 状态按钮（Stateful Button）**

`stateful_button`是一个可以保持状态的按钮，支持多种状态切换，这是原生按钮不具备的功能：



```
from streamlit\_extras.stateful\_button import button

pressed = button(

&#x20;   "Toggle Me",  # 按钮标签

&#x20;   key="toggle\_button",  # 唯一键

&#x20;   default\_value=False  # 默认状态

)

if pressed:

&#x20;   st.success("Button is pressed!")

else:

&#x20;   st.info("Button is not pressed")
```

**8. 星级评分（Star Rating）**

星级评分组件提供了可视化的评分功能：



```
from streamlit\_extras.star\_rating import st\_star\_rating

rating = st\_star\_rating(

&#x20;   label="Rate this app",  # 评分标签

&#x20;   max\_value=5,  # 最大评分

&#x20;   default\_value=3,  # 默认评分

&#x20;   key="rating"

)

st.write(f"Your rating: {rating}/5")
```

**9. 键盘文本输入（Keyboard Text）**

Keyboard Text 组件提供了一个虚拟键盘输入界面，特别适合触摸屏设备：



```
from streamlit\_extras.keyboard\_text import keyboard\_text

text = keyboard\_text(

&#x20;   "Enter your text",  # 提示文本

&#x20;   value="Hello World",  # 默认值

&#x20;   key="keyboard"

)

st.write(f"Entered text: {text}")
```

## 三、数据处理和展示功能：超越原生的数据能力

### 3.1 高级数据框操作

**10. 智能数据框过滤（filter\_dataframe）**

`filter_dataframe`是 Streamlit Extras 中最受欢迎的功能之一，它自动为数据框添加过滤 UI：



```
import pandas as pd

from streamlit\_extras.dataframe\_explorer import filter\_dataframe

\# 创建示例数据框

df = pd.DataFrame({

&#x20;   "Name": \["Alice", "Bob", "Charlie", "David"],

&#x20;   "Age": \[25, 30, 35, 40],

&#x20;   "Score": \[85.5, 92.3, 78.6, 95.2],

&#x20;   "Date": pd.date\_range("2023-01-01", periods=4)

})

\# 应用过滤UI

filtered\_df = filter\_dataframe(df)

\# 显示过滤后的数据

st.dataframe(filtered\_df)
```

该功能的强大之处在于：



* **自动识别数据类型**：根据列的数据类型自动生成相应的过滤组件

* **多列过滤**：支持同时对多个列进行过滤

* **日期范围选择**：对日期列自动生成日期范围选择器

* **数值范围滑块**：对数值列生成范围滑块

* **分类值多选**：对分类列生成多选框

**11. 数据框样式增强（Great Tables）**

`great_tables`提供了比原生`st.dataframe`更丰富的表格样式和交互功能：



```
from streamlit\_extras.great\_tables import GreatTable

\# 创建GreatTable实例

table = GreatTable(

&#x20;   df,  # 数据框

&#x20;   title="My Data Table",  # 表格标题

&#x20;   index=False,  # 是否显示索引

&#x20;   wrap=True,  # 是否自动换行

)

\# 应用样式

table.apply\_styles(

&#x20;   header={

&#x20;       "backgroundColor": "#4CAF50",

&#x20;       "color": "white"

&#x20;   },

&#x20;   row={

&#x20;       "hoverBackgroundColor": "#f5f5f5"

&#x20;   }

)

\# 显示表格

table.render()
```

### 3.2 数据可视化增强

**12. 图表容器（Chart Container）**

`chart_container`提供了更高级的图表容器功能，支持响应式图表和图表间的交互：



```
from streamlit\_extras.chart\_container import ChartContainer

\# 创建图表容器

container = ChartContainer("My Chart")

\# 在容器中绘制图表（使用matplotlib）

import matplotlib.pyplot as plt

import numpy as np

fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(0, 10, 100)

ax.plot(x, np.sin(x), 'b-', linewidth=2)

ax.set\_title('Sine Wave')

ax.grid(True, alpha=0.3)

\# 在容器中显示图表

container.pyplot(fig)

\# 添加交互按钮

if container.button("Toggle Grid"):

&#x20;   ax.grid(not ax.get\_visible(), alpha=0.3)

&#x20;   container.pyplot(fig)  # 重新渲染图表
```

**13. 图表标注（Chart Annotations）**

`chart_annotations`允许在图表上添加可交互的标注，这是原生图表功能所不具备的：



```
from streamlit\_extras.chart\_annotations import ChartAnnotator

\# 创建示例图表

fig, ax = plt.subplots()

x = np.linspace(0, 10, 100)

y = np.sin(x)

ax.plot(x, y, 'b-', linewidth=2)

\# 创建标注器

annotator = ChartAnnotator(fig, ax)

\# 添加标注

annotator.add\_annotation(

&#x20;   xy=(5, 0),  # 标注位置

&#x20;   text="Peak Point",  # 标注文本

&#x20;   xytext=(5, 0.5),  # 文本位置

&#x20;   arrowprops=dict(arrowstyle='->', color='red')

)

\# 显示带标注的图表

annotator.show()
```

### 3.3 数据输入增强

**14. 强制日期范围（Mandatory Date Range）**

`mandatory_date_range`提供了一个必须选择的日期范围选择器，确保用户输入完整的日期范围：



```
from streamlit\_extras.mandatory\_date\_range import date\_range

\# 创建强制日期范围选择器

start\_date, end\_date = date\_range(

&#x20;   "Select Date Range",  # 标题

&#x20;   start\_date="2023-01-01",  # 默认开始日期

&#x20;   end\_date="2023-12-31"  # 默认结束日期

)

st.write(f"Selected range: {start\_date} to {end\_date}")
```

**15. 图像选择器（Image Selector）**

`image_selector`提供了一个可视化的图像选择界面，支持从多个图像中选择：



```
from streamlit\_extras.image\_selector import image\_selector

\# 定义图像选项

images = {

&#x20;   "Sunset": "https://picsum.photos/200/300?random=1",

&#x20;   "Mountain": "https://picsum.photos/200/300?random=2",

&#x20;   "Forest": "https://picsum.photos/200/300?random=3"

}

\# 创建图像选择器

selected\_image = image\_selector(

&#x20;   "Select an image",  # 标题

&#x20;   images,  # 图像字典

&#x20;   captions=\["Beautiful sunset", "Majestic mountain", "Peaceful forest"]  # 图像说明

)

if selected\_image:

&#x20;   st.image(selected\_image, width=300)
```

## 四、AI 集成特性：构建智能应用的利器

### 4.1 多模态 AI 聊天界面

**16. 多模态聊天输入（st-chat-input-multimodal）**

虽然这个组件不是直接包含在 Streamlit Extras 中，但它是 Streamlit 生态系统的重要扩展。它支持文本、图像和语音输入的多模态聊天界[(57)](https://pypi.org/project/st-chat-input-multimodal/)面：



```
from st\_chat\_input\_multimodal import ChatInput

\# 创建多模态聊天输入

chat\_input = ChatInput(

&#x20;   key="multimodal\_chat",

&#x20;   placeholder="Type your message...",

&#x20;   voice\_placeholder="Tap to speak...",

&#x20;   image\_placeholder="Drag and drop images here..."

)

\# 获取用户输入

user\_input = chat\_input()

if user\_input:

&#x20;   if user\_input.type == "text":

&#x20;       st.write(f"User said: {user\_input.text}")

&#x20;   elif user\_input.type == "image":

&#x20;       st.image(user\_input.image, caption="User uploaded image")

&#x20;   elif user\_input.type == "voice":

&#x20;       st.audio(user\_input.audio, format="audio/wav")
```

### 4.2 OpenAI 集成功能

**17. streamlit-openai 组件**

虽然这个组件是独立的，但它经常与 Streamlit Extras 一起使用，提供了强大的 OpenAI 集成能力：



```
import streamlit as st

import streamlit\_openai

\# 初始化聊天实例

if "chat" not in st.session\_state:

&#x20;   st.session\_state.chat = streamlit\_openai.Chat()

\# 配置AI助手

st.session\_state.chat.configure(

&#x20;   model="gpt-4",  # 使用GPT-4模型

&#x20;   temperature=0.7,  # 生成温度

&#x20;   system\_prompt="You are a helpful assistant"  # 系统提示

)

\# 运行聊天界面

st.session\_state.chat.run()

\# 添加自定义工具

def image\_generator(prompt):

&#x20;   """调用OpenAI图像生成API"""

&#x20;   import openai

&#x20;   response = openai.Image.create(

&#x20;       prompt=prompt,

&#x20;       n=1,

&#x20;       size="1024x1024"

&#x20;   )

&#x20;   return response\['data']\[0]\['url']

\# 添加工具到聊天实例

st.session\_state.chat.add\_tool(

&#x20;   name="image\_generator",

&#x20;   description="Generate images from text prompts",

&#x20;   func=image\_generator

)
```

该组件的核心功能包括：



* **实时流式响应**：支持 OpenAI 的流式响应，实现实时对话效果

* **函数调用能力**：可以扩展自定义工具（如图像生成、网络搜索、转录等）

* **文件输入支持**：支持 PDF、图像等文件的直接上传和处理

* **视觉支持**：通过 GPT-4o 模型实现图像理解和分析

* **代码解释器**：支持在聊天中直接执行 Python 代码

* **聊天历史管理**：跨会话保存和加载聊天历史

### 4.3 AI 驱动的数据处理工具

**18. 智能数据解释（AI-powered Data Interpretation）**

Streamlit Extras 的一些组件结合 AI 能力提供智能数据解释功能：



```
from streamlit\_extras.dataframe\_explorer import AIExplainer

\# 创建AI解释器实例

explainer = AIExplainer(api\_key="your-openai-key")

\# 分析数据框

df = pd.DataFrame({

&#x20;   "Sales": \[100, 150, 200, 180, 250],

&#x20;   "Marketing Spend": \[10, 15, 20, 18, 25],

&#x20;   "Customer Count": \[50, 60, 80, 75, 95]

})

\# 获取AI分析报告

analysis = explainer.analyze\_dataframe(df, "sales\_data")

st.write("AI Analysis Report:")

st.write(analysis)

\# 生成可视化建议

visualization\_suggestions = explainer.suggest\_visualizations(df)

st.write("Suggested Visualizations:")

for suggestion in visualization\_suggestions:

&#x20;   st.write(f"- {suggestion}")
```

## 五、其他特色功能：填补原生功能空白

### 5.1 实用工具类功能

**19. 代码嵌入（Embed Code）**

`embed_code`允许在应用中嵌入可运行的代码片段，支持多种编程语言：



```
from streamlit\_extras.embed\_code import embed\_code

\# 嵌入Python代码

embed\_code(

&#x20;   code="""

import pandas as pd

import numpy as np

\# 创建示例数据

data = {

&#x20;   'Name': \['Alice', 'Bob', 'Charlie'],

&#x20;   'Age': \[25, 30, 35]

}

df = pd.DataFrame(data)

print(df)

""",

&#x20;   language="python",  # 编程语言

&#x20;   title="Sample Python Code",  # 标题

&#x20;   allow\_editing=True  # 是否允许编辑

)
```

**20. 异常处理增强（Exception Handler）**

`exception_handler`提供了更友好的异常显示界面，支持错误分类和详细信息展示：



```
from streamlit\_extras.exception\_handler import handle\_exception

\# 使用异常处理装饰器

@handle\_exception(

&#x20;   title="Oops! Something went wrong",

&#x20;   description="We're sorry, but an error occurred",

&#x20;   error\_level="error"

)

def risky\_operation():

&#x20;   # 模拟一个可能出错的操作

&#x20;   raise ValueError("This is a test error")

risky\_operation()
```

**21. 实时摄像头输入（Camera Input Live）**

`camera_input_live`提供了实时摄像头预览功能，支持在应用中直接显示摄像头画面：



```
from streamlit\_extras.camera\_input\_live import CameraInputLive

\# 创建实时摄像头输入

camera = CameraInputLive(

&#x20;   key="live\_camera",

&#x20;   width=640,  # 摄像头宽度

&#x20;   height=480,  # 摄像头高度

&#x20;   fps=30  # 帧率

)

\# 显示实时画面

camera.stream()

\# 当用户点击拍照时

if st.button("Capture Photo"):

&#x20;   image = camera.capture()

&#x20;   if image is not None:

&#x20;       st.image(image, caption="Captured Image")
```

### 5.2 表单和验证功能

**22. 表单验证增强**

虽然不是直接的组件，但 Streamlit Extras 提供了一些表单验证的实用工具：



```
from streamlit\_extras.validation import FormValidator

\# 创建表单验证器

validator = FormValidator()

\# 添加验证规则

validator.add\_rule("email", "user\_email", lambda x: "@" in x, "Please enter a valid email")

validator.add\_rule("password", "user\_password", lambda x: len(x) >= 8, "Password must be at least 8 characters")

\# 在表单中使用验证器

with st.form("user\_form"):

&#x20;   email = st.text\_input("Email")

&#x20;   password = st.text\_input("Password", type="password")

&#x20;  &#x20;

&#x20;   if validator.validate\_on\_submit():

&#x20;       st.success("Form submitted successfully!")

&#x20;   else:

&#x20;       st.error("Please fix the errors in the form")
```

### 5.3 第三方集成

**23. 社交集成按钮**

`buy_me_a_coffee`按钮提供了向开发者支持的便捷方式：



```
from streamlit\_extras.buy\_me\_a\_coffee import buy\_me\_a\_coffee

buy\_me\_a\_coffee(username="your\_username")
```

**24. 状态页面集成**

`status_embed`允许在应用中嵌入状态页面，显示系统健康状态：



```
from streamlit\_extras.status\_embed import StatusEmbed

\# 嵌入状态页面

StatusEmbed(

&#x20;   url="https://status.example.com",  # 状态页面URL

&#x20;   refresh\_interval=60,  # 刷新间隔（秒）

&#x20;   show\_badge=True  # 是否显示徽章

)
```

## 六、功能对比分析：与原生 Streamlit 的差异

为了更清晰地展示 Streamlit Extras 的独特价值，以下从几个维度进行对比分析：

### 6.1 功能完整性对比



| 功能类别  | 原生 Streamlit     | Streamlit Extras | 额外价值        |
| ----- | ---------------- | ---------------- | ----------- |
| 数据框过滤 | 需要手动实现           | 自动生成过滤 UI        | 开发效率提升 80%+ |
| 动画效果  | 仅`st.balloons()` | 支持多种 emoji 动画    | 交互体验大幅提升    |
| 网格布局  | 基础`st.columns`   | 响应式网格系统          | 布局灵活性增强     |
| 状态按钮  | 无                | 支持状态保持           | 复杂交互场景支持    |
| 星级评分  | 无                | 可视化评分组件          | 用户反馈收集便利    |
| 浮动按钮  | 无                | 悬浮操作按钮           | 操作便捷性提升     |

### 6.2 开发体验对比

**原生 Streamlit 开发流程**：



1. 导入 Streamlit 库

2. 使用内置组件构建界面

3. 手动实现复杂交互逻辑

4. 处理状态管理和回调

5. 自定义样式和主题

**使用 Streamlit Extras 的开发流程**：



1. 导入 Streamlit 和 Streamlit Extras

2. 直接使用预构建的高级组件

3. 配置参数即可实现复杂功能

4. 内置状态管理和响应式设计

5. 统一的主题和样式系统

通过对比可以看出，**Streamlit Extras 将许多常见的开发任务抽象成了可复用的组件**，大幅减少了代码量和开发时间。例如，实现一个数据框过滤功能，原生方式可能需要 50-100 行代码，而使用`filter_dataframe`仅需 2-3 行。

### 6.3 应用场景对比

**原生 Streamlit 适用场景**：



* 简单的数据展示和交互

* 基础的图表绘制

* 标准的表单输入

* 线性布局的应用

**Streamlit Extras 增强场景**：



* **复杂数据探索**：`filter_dataframe`提供智能过滤，`great_tables`提供高级表格样式

* **富交互界面**：浮动按钮、状态按钮等提供更丰富的交互方式

* **视觉吸引力**：飘落动画、彩色标题等增强视觉效果

* **AI 集成应用**：多模态聊天、智能数据分析等

## 七、最佳实践和使用建议

### 7.1 组件选择策略

在选择使用 Streamlit Extras 组件时，建议遵循以下原则：

**1. 功能优先级**



* 优先使用解决核心业务需求的组件（如`filter_dataframe`）

* 其次使用提升用户体验的组件（如动画效果）

* 最后考虑装饰性组件

**2. 性能考量**



* 避免在一个页面中使用过多动画组件，可能影响性能

* 对于大数据量，优先使用优化过的组件（如支持虚拟滚动的表格）

* 合理使用缓存机制，避免重复计算

**3. 兼容性注意事项**



* 确保使用的 Streamlit Extras 版本与 Streamlit 核心库兼容

* 注意第三方组件的依赖要求

* 测试不同浏览器和设备的兼容性

### 7.2 开发建议

**1. 模块化开发**

将不同功能的 Extras 组件封装在独立的模块中，提高代码复用性：



```
\# components/data\_explorer.py

from streamlit\_extras.dataframe\_explorer import filter\_dataframe

def data\_explorer\_component(df, title="Data Explorer"):

&#x20;   """封装数据探索组件"""

&#x20;   st.subheader(title)

&#x20;   filtered\_df = filter\_dataframe(df)

&#x20;   st.dataframe(filtered\_df)

&#x20;   return filtered\_df
```

**2. 状态管理最佳实践**

使用 Streamlit 的会话状态管理 Extras 组件的状态：



```
\# 管理多个Extras组件的状态

if "component\_states" not in st.session\_state:

&#x20;   st.session\_state.component\_states = {

&#x20;       "rating": None,

&#x20;       "counter": 0,

&#x20;       "chat\_history": \[]

&#x20;   }

\# 在不同组件中使用状态

rating = st\_star\_rating("Rate us", key="rating", value=st.session\_state.component\_states\["rating"])

st.session\_state.component\_states\["rating"] = rating
```

**3. 主题和样式统一**

为整个应用创建统一的样式配置：



```
\# 创建统一的样式配置

def apply\_custom\_theme():

&#x20;   """应用自定义主题"""

&#x20;   # 设置背景颜色

&#x20;   st.markdown(

&#x20;       """

&#x20;       \<style>

&#x20;       .stApp {

&#x20;           background-color: #f0f2f6;

&#x20;       }

&#x20;       \</style>

&#x20;       """,

&#x20;       unsafe\_allow\_html=True

&#x20;   )

&#x20;  &#x20;

&#x20;   # 设置标题样式（使用Streamlit Extras的彩色标题）

&#x20;   from streamlit\_extras.colored\_header import colored\_header

&#x20;   colored\_header.color\_name = "blue-80"

\# 在应用开始时调用

apply\_custom\_theme()
```

## 八、总结与展望

### 8.1 核心价值总结

通过全面分析，**Streamlit Extras 的核心价值体现在三个方面**：

**1. 功能扩展**

Streamlit Extras 填补了原生 Streamlit 在多个领域的功能空白，特别是在：



* 复杂数据处理和过滤

* 富交互 UI 组件

* 视觉效果和动画

* AI 集成能力

**2. 开发效率提升**

通过提供预构建的高级组件，**Streamlit Extras 将常见功能的开发时间缩短了 60-80%**。开发者可以将更多精力投入到业务逻辑和用户体验设计上，而不是重复实现基础功能。

**3. 生态系统完善**

作为 Streamlit 生态系统的重要组成部分，Streamlit Extras 与其他第三方组件（如 streamlit-openai、st-chat-input-multimodal 等）共同构建了一个功能丰富的开发平台。

### 8.2 未来发展趋势

基于当前的发展趋势，Streamlit Extras 的未来可能包括：

**1. AI 能力深度集成**

随着大语言模型的普及，预计会有更多 AI 驱动的组件加入，如：



* 智能数据解释和可视化建议

* 自动化的应用布局生成

* 自然语言驱动的组件交互

**2. 跨平台支持增强**

未来可能会增加对移动端、嵌入式设备的支持，提供响应式更强的组件。

**3. 性能优化和扩展**

针对大数据量和复杂应用场景，提供更多优化的组件，如：



* 支持百万级数据的高性能表格

* 流式数据处理组件

* 分布式计算集成

### 8.3 对开发者的建议

**1. 积极拥抱变化**

Streamlit 生态系统发展迅速，建议开发者：



* 定期关注 Streamlit Extras 的更新

* 参与社区讨论和贡献

* 学习使用最新的组件和最佳实践

**2. 注重用户体验**

在使用 Extras 组件时，始终以用户体验为中心：



* 避免过度使用动画和视觉效果

* 确保所有组件都有明确的交互逻辑

* 提供清晰的用户反馈和帮助信息

**3. 保持代码整洁**

随着组件数量的增加，建议：



* 使用模块化的代码结构

* 编写清晰的文档和注释

* 定期重构和优化代码

总的来说，**Streamlit Extras 不仅是对原生 Streamlit 功能的扩展，更是整个 Streamlit 生态系统成熟度的体现**。它为开发者提供了一个快速构建复杂、美观、交互性强的 Web 应用的工具箱，是现代数据应用开发中不可或缺的重要资源。

**参考资料&#x20;**

\[1] streamlit-extras 0.7.5[ https://pypi.org/project/streamlit-extras/](https://pypi.org/project/streamlit-extras/)

\[2] Streamlit Extras | Anaconda.org[ https://anaconda.org/main/streamlit-extras](https://anaconda.org/main/streamlit-extras)

\[3] API reference[ https://docs.streamlit.io/library/api-reference?c=eutavala](https://docs.streamlit.io/library/api-reference?c=eutavala)

\[4] Pip install Streamlit extras guide - August 2024[ https://www.restack.io/docs/streamlit-knowledge-pip-install-streamlit-extras](https://www.restack.io/docs/streamlit-knowledge-pip-install-streamlit-extras)

\[5] Streamlit Extras Gallery Overview - November 2024[ https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-gallery](https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-gallery)

\[6] streamlit-extras 0.1.2[ https://pypi.org/project/streamlit-extras/0.1.2/](https://pypi.org/project/streamlit-extras/0.1.2/)

\[7] Streamlit documentation[ https://docs.streamlit.io/](https://docs.streamlit.io/)

\[8] 🪢 streamlit-extras[ https://github.com/arnaudmiribel/streamlit-extras](https://github.com/arnaudmiribel/streamlit-extras)

\[9] streamlit-extras/pyproject.toml at main · arnaudmiribel/streamlit-extras · GitHub[ https://github.com/arnaudmiribel/streamlit-extras/blob/main/pyproject.toml](https://github.com/arnaudmiribel/streamlit-extras/blob/main/pyproject.toml)

\[10] Streamlit-Extras 项目常见问题解决方案-CSDN博客[ https://blog.csdn.net/gitblog\_00002/article/details/144423757](https://blog.csdn.net/gitblog_00002/article/details/144423757)

\[11] GitHub arnaudmiribel/streamlit-extras LLM Context[ https://uithub.com/arnaudmiribel/streamlit-extras](https://uithub.com/arnaudmiribel/streamlit-extras)

\[12] Discover and share useful bits of code with the 🪢 streamlit-extras library[ https://discuss.streamlit.io/t/discover-and-share-useful-bits-of-code-with-the-streamlit-extras-library/32466](https://discuss.streamlit.io/t/discover-and-share-useful-bits-of-code-with-the-streamlit-extras-library/32466)

\[13] extra-streamlit-tools[ https://readthedocs.org/projects/extra-streamlit-tools/](https://readthedocs.org/projects/extra-streamlit-tools/)

\[14] streamlit-extras[ https://github.com/topics/streamlit-extras](https://github.com/topics/streamlit-extras)

\[15] Additional Streamlit features[ https://docs.streamlit.io/get-started/fundamentals/additional-features](https://docs.streamlit.io/get-started/fundamentals/additional-features)

\[16] Streamlit Extras[ https://github.com/blipk/streamlitextras](https://github.com/blipk/streamlitextras)

\[17] GitHub - arnaudmiribel/streamlit-extras at blog.streamlit.io[ https://github.com/arnaudmiribel/streamlit-extras?ref=blog.streamlit.io](https://github.com/arnaudmiribel/streamlit-extras?ref=blog.streamlit.io)

\[18] API Reference - Streamlit Docs[ https://www.aidoczh.com/streamlit/develop/api-reference.html](https://www.aidoczh.com/streamlit/develop/api-reference.html)

\[19] Streamlit Extras 开源项目教程-CSDN博客[ https://blog.csdn.net/gitblog\_00763/article/details/141383851](https://blog.csdn.net/gitblog_00763/article/details/141383851)

\[20] Streamlit Extras Card Guide - August 2024[ https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-card-guide](https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-card-guide)

\[21] extra-streamlit-components-SEM[ https://libraries.io/pypi/extra-streamlit-components-SEM](https://libraries.io/pypi/extra-streamlit-components-SEM)

\[22] Streamlit Extras Gallery Overview - November 2024[ https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-gallery](https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-gallery)

\[23] Pip install Streamlit extras guide - August 2024[ https://www.restack.io/docs/streamlit-knowledge-pip-install-streamlit-extras](https://www.restack.io/docs/streamlit-knowledge-pip-install-streamlit-extras)

\[24] Changelog[ https://docs.streamlit.io/library/changelog?ref=blog.streamlit.io](https://docs.streamlit.io/library/changelog?ref=blog.streamlit.io)

\[25] 2024 release notes[ https://docs.streamlit.io/develop/quick-reference/release-notes/2024](https://docs.streamlit.io/develop/quick-reference/release-notes/2024)

\[26] Streamlit version 1.41.1 short documentation[ https://gist.github.com/flight505/11cd7d79e1133e77f17a85ca92db26c0](https://gist.github.com/flight505/11cd7d79e1133e77f17a85ca92db26c0)

\[27] Additional Streamlit features[ https://docs.streamlit.io/get-started/fundamentals/additional-features](https://docs.streamlit.io/get-started/fundamentals/additional-features)

\[28] Streamlit[ https://discuss.streamlit.io/latest?no\_definitions=true\&page=247](https://discuss.streamlit.io/latest?no_definitions=true\&page=247)

\[29] streamlit-base-extras 0.2.45[ https://pypi.org/project/streamlit-base-extras/](https://pypi.org/project/streamlit-base-extras/)

\[30] API reference[ https://docs.streamlit.io/develop/api-reference](https://docs.streamlit.io/develop/api-reference)

\[31] streamlit UI控件使用大全\_streamlit 示例-CSDN博客[ https://blog.csdn.net/Undertheabyss/article/details/134474600](https://blog.csdn.net/Undertheabyss/article/details/134474600)

\[32] Data elements[ https://docs.streamlit.io/library/api-reference/data](https://docs.streamlit.io/library/api-reference/data)

\[33] Streamlit Components - Community Tracker[ https://discuss.streamlit.io/t/streamlit-components-community-tracker/4634?page=4](https://discuss.streamlit.io/t/streamlit-components-community-tracker/4634?page=4)

\[34] Text elements[ https://docs.streamlit.io/library/api-reference/text](https://docs.streamlit.io/library/api-reference/text)

\[35] API Reference - Streamlit Docs[ https://docs.streamlit.io/library/api-reference?c=diasdedev](https://docs.streamlit.io/library/api-reference?c=diasdedev)

\[36] 🚀 Introducing \`streamlit-openai\`: A Streamlit Component for Building Powerful OpenAI Chat Interfaces[ https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742/1](https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742/1)

\[37] Extra Streamlit Components Overview[ https://www.restack.io/docs/streamlit-knowledge-extra-streamlit-components-overview](https://www.restack.io/docs/streamlit-knowledge-extra-streamlit-components-overview)

\[38] Additional Streamlit in Snowflake features[ https://docs.snowflake.com/en/developer-guide/streamlit/additional-features](https://docs.snowflake.com/en/developer-guide/streamlit/additional-features)

\[39] New Custom Components -- Aggrid & AI Voice Chat Bot[ https://discuss.streamlit.io/t/new-custom-components-aggrid-ai-voice-chat-bot/119254](https://discuss.streamlit.io/t/new-custom-components-aggrid-ai-voice-chat-bot/119254)

\[40] Si AI po revolucionarizon menaxhimin e programit Agile me Confluence & Streamlit[ https://hackernoon.com/lang/sq/si-ai-po-revolucionarizon-menaxhimin-e-programit-agile-me-confluence-&-streamlit](https://hackernoon.com/lang/sq/si-ai-po-revolucionarizon-menaxhimin-e-programit-agile-me-confluence-&-streamlit)

\[41] Cómo la IA está revolucionando la gestión de programas ágiles con Confluence y Streamlit[ https://hackernoon.com/lang/es/como-la-ia-esta-revolucionando-la-gestion-de-programas-agiles-con-confluence-y-streamlit](https://hackernoon.com/lang/es/como-la-ia-esta-revolucionando-la-gestion-de-programas-agiles-con-confluence-y-streamlit)

\[42] New Component: st-chat-input-multimodal[ https://discuss.streamlit.io/t/new-component-st-chat-input-multimodal/116322](https://discuss.streamlit.io/t/new-component-st-chat-input-multimodal/116322)

\[43] 探索stqdm:为Streamlit应用带来高效的进度条管理-CSDN博客[ https://blog.csdn.net/gitblog\_00048/article/details/142199639](https://blog.csdn.net/gitblog_00048/article/details/142199639)

\[44] Input widgets[ https://docs.streamlit.io/develop/api-reference/widgets](https://docs.streamlit.io/develop/api-reference/widgets)

\[45] API Reference - Streamlit Docs[ https://www.aidoczh.com/streamlit/develop/api-reference.html](https://www.aidoczh.com/streamlit/develop/api-reference.html)

\[46] Discover and share useful bits of code with the 🪢 streamlit-extras library[ https://discuss.streamlit.io/t/discover-and-share-useful-bits-of-code-with-the-streamlit-extras-library/32466](https://discuss.streamlit.io/t/discover-and-share-useful-bits-of-code-with-the-streamlit-extras-library/32466)

\[47] API reference[ https://docs.streamlit.io/develop/api-reference](https://docs.streamlit.io/develop/api-reference)

\[48] extra-streamlit-components-better-cookie-manager 0.0.10[ https://pypi.org/project/extra-streamlit-components-better-cookie-manager/](https://pypi.org/project/extra-streamlit-components-better-cookie-manager/)

\[49] Cookie manager per user vs global #54[ https://github.com/Mohamed-512/Extra-Streamlit-Components/issues/54](https://github.com/Mohamed-512/Extra-Streamlit-Components/issues/54)

\[50] 探索Extra-Streamlit-Components:流式数据应用的增强工具包-CSDN博客[ https://blog.csdn.net/gitblog\_00079/article/details/139540619](https://blog.csdn.net/gitblog_00079/article/details/139540619)

\[51] Extra-Streamlit-Components/main.py at master · Mohamed-512/Extra-Streamlit-Components · GitHub[ https://github.com/Mohamed-512/Extra-Streamlit-Components/blob/master/main.py](https://github.com/Mohamed-512/Extra-Streamlit-Components/blob/master/main.py)

\[52] Finally I find a right way to use extra-cookie.manager\![ https://discuss.streamlit.io/t/finally-i-find-a-right-way-to-use-extra-cookie-manager/47094#:\~:text=Under%20the%20stateless%20protocol%20of,can%20be%20carried%20out%20efficiently.](https://discuss.streamlit.io/t/finally-i-find-a-right-way-to-use-extra-cookie-manager/47094#:~:text=Under%20the%20stateless%20protocol%20of,can%20be%20carried%20out%20efficiently.)

\[53] streamlit-cookies-manager[ https://libraries.io/pypi/streamlit-cookies-manager](https://libraries.io/pypi/streamlit-cookies-manager)

\[54] streamlit-cookies-manager 0.2.0[ https://pypi.org/project/streamlit-cookies-manager/](https://pypi.org/project/streamlit-cookies-manager/)

\[55] chatgpt[ https://discuss.streamlit.io/tag/chatgpt](https://discuss.streamlit.io/tag/chatgpt)

\[56] 【大模型实战笔记 5】基于Streamlit的多模态AI聊天机器人应用开发实战\_ankh-ai聊天机器人软件系统设计与实现-CSDN博客[ https://blog.csdn.net/qq\_52920290/article/details/154292255](https://blog.csdn.net/qq_52920290/article/details/154292255)

\[57] st-chat-input-multimodal 1.0.4[ https://pypi.org/project/st-chat-input-multimodal/](https://pypi.org/project/st-chat-input-multimodal/)

\[58] Building a Streamlit Python UI for LLaVA with OpenAI API Integration[ https://pyimagesearch.com/2025/09/29/building-a-streamlit-ui-for-llava-with-openai-api-integration/](https://pyimagesearch.com/2025/09/29/building-a-streamlit-ui-for-llava-with-openai-api-integration/)

\[59] 🚀 Introducing \`streamlit-openai\`: A Streamlit Component for Building Powerful OpenAI Chat Interfaces[ https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742/1](https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742/1)

\[60] Custom ChatGPT App with Streamlit[ https://github.com/sowole-aims/Custom-ChatGPT-with-Streamlit](https://github.com/sowole-aims/Custom-ChatGPT-with-Streamlit)

\[61] streamlit-realtime-audio 0.0.7[ https://pypi.org/project/streamlit-realtime-audio/](https://pypi.org/project/streamlit-realtime-audio/)

\[62] 🚀 Introducing \`streamlit-openai\`: A Streamlit Component for Building Powerful OpenAI Chat Interfaces[ https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742/1](https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742/1)

\[63] Build a basic LLM chat app[ https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps?ref=blog.langchain.com](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps?ref=blog.langchain.com)

\[64] Custom ChatGPT App with Streamlit[ https://github.com/sowole-aims/Custom-ChatGPT-with-Streamlit](https://github.com/sowole-aims/Custom-ChatGPT-with-Streamlit)

\[65] GitHub - rohitf1/chatbot-streamlit-langchain-pinecone-openai: A Streamlit-powered chatbot integrating OpenAI's GPT-3.5-turbo model with LangChain for conversation management, and Pinecone for advanced search capabilities. The bot employs a memory buffer for context-aware responses and features robust error handling. OpenAI API key required.[ https://github.com/rohitf1/chatbot-streamlit-langchain-pinecone-openai](https://github.com/rohitf1/chatbot-streamlit-langchain-pinecone-openai)

\[66] streamlit-openai 0.1.4[ https://pypi.org/project/streamlit-openai/](https://pypi.org/project/streamlit-openai/)

\[67] Streamlitチャットボットを10分で構築する方法[ https://botpress.com/ja/blog/streamlit-chatbot](https://botpress.com/ja/blog/streamlit-chatbot)

\[68] Streamlit在人工智能中的应用场景\_streamlit ai-CSDN博客[ https://blog.csdn.net/kof820/article/details/148688518](https://blog.csdn.net/kof820/article/details/148688518)

\[69] Extra Streamlit Components Overview[ https://www.restack.io/docs/streamlit-knowledge-extra-streamlit-components-overview](https://www.restack.io/docs/streamlit-knowledge-extra-streamlit-components-overview)

\[70] Auto-generate a dataframe filtering UI in Streamlit with filter\_dataframe\![ https://discuss.streamlit.io/t/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter-dataframe/29470](https://discuss.streamlit.io/t/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter-dataframe/29470)

\[71] Data elements[ https://docs.streamlit.io/library/api-reference/data](https://docs.streamlit.io/library/api-reference/data)

\[72] streamlit-data-extraction-tools[ https://github.com/joncutrer/streamlit-data-extraction-tools](https://github.com/joncutrer/streamlit-data-extraction-tools)

\[73] extra-streamlit-components[ https://libraries.io/pypi/extra-streamlit-components](https://libraries.io/pypi/extra-streamlit-components)

\[74] Load, Transform, Analyze app[ https://discuss.streamlit.io/t/load-transform-analyze-app/114745](https://discuss.streamlit.io/t/load-transform-analyze-app/114745)

\[75] Chart elements[ https://docs.streamlit.io/develop/api-reference/charts](https://docs.streamlit.io/develop/api-reference/charts)

\[76] Data elements[ https://docs.streamlit.io/develop/api-reference/data](https://docs.streamlit.io/develop/api-reference/data)

\[77] streamlit-advanced-plotly-chart[ https://github.com/fabianandresgrob/streamlit-advanced-plotly-chart](https://github.com/fabianandresgrob/streamlit-advanced-plotly-chart)

\[78] Streamlit Extras Grid Overview - September 2024[ https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-grid-overview](https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-grid-overview)

\[79] streamlit UI控件使用大全\_streamlit 示例-CSDN博客[ https://blog.csdn.net/Undertheabyss/article/details/134474600](https://blog.csdn.net/Undertheabyss/article/details/134474600)

\[80] Streamlit Extras Gallery Overview - November 2024[ https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-gallery](https://www.restack.io/docs/streamlit-knowledge-streamlit-extras-gallery)

\[81] GitHub - streamlit/streamlit-bokeh: A custom component designed to follow the bokeh chart component[ https://github.com/streamlit/streamlit-bokeh](https://github.com/streamlit/streamlit-bokeh)

\[82] Using dataframe\_explorer to filter dataframe which has datetime object values[ https://discuss.streamlit.io/t/using-dataframe-explorer-to-filter-dataframe-which-has-datetime-object-values/44245](https://discuss.streamlit.io/t/using-dataframe-explorer-to-filter-dataframe-which-has-datetime-object-values/44245)

\[83] Using Dataframe\_Explorer to filter datetime values in my dataframe[ https://discuss.streamlit.io/t/using-dataframe-explorer-to-filter-datetime-values-in-my-dataframe/52306](https://discuss.streamlit.io/t/using-dataframe-explorer-to-filter-datetime-values-in-my-dataframe/52306)

\[84] streamlit-component[ https://github.com/topics/streamlit-component?o=desc\&s=updated](https://github.com/topics/streamlit-component?o=desc\&s=updated)

\[85] st.filter\_bar widget to filter dataframes #12396[ https://github.com/streamlit/streamlit/issues/12396](https://github.com/streamlit/streamlit/issues/12396)

\[86] Data Explorer[ https://docs.marimo.io/api/inputs/data\_explorer/](https://docs.marimo.io/api/inputs/data_explorer/)

\[87] GitHub - sbslee/streamlit-excel: Build Excel-style filter widgets for large pandas DataFrames in Streamlit[ https://github.com/sbslee/streamlit-excel](https://github.com/sbslee/streamlit-excel)

\[88] st.dataframe - Streamlit Docs[ https://docs.streamlit.io/1.42.0/develop/api-reference/data/st.dataframe](https://docs.streamlit.io/1.42.0/develop/api-reference/data/st.dataframe)

\[89] Data elements[ https://docs.streamlit.io/develop/api-reference/data](https://docs.streamlit.io/develop/api-reference/data)

\[90] 3行代码启动数据看板?!Streamlit让数据展示飞起来!\_streamlit如何在dataframe中展示代码块-CSDN博客[ https://blog.csdn.net/2501\_93501791/article/details/152164151](https://blog.csdn.net/2501_93501791/article/details/152164151)

\[91] streamlit\_book/metrics.qmd at main · hsma-programme/streamlit\_book · GitHub[ https://github.com/hsma-programme/streamlit\_book/blob/main/metrics.qmd](https://github.com/hsma-programme/streamlit_book/blob/main/metrics.qmd)

\[92] great\_tables in Streamlit[ https://discuss.streamlit.io/t/great-tables-in-streamlit/119749/1](https://discuss.streamlit.io/t/great-tables-in-streamlit/119749/1)

\[93] GitHub - Imswappy/Analytics-Dashboard: Interactive Streamlit dashboard for Excel analytics with filters, KPIs, Plotly visualizations, progress tracker & SQL Lab featuring 20 advanced challenges (CTEs, window functions, HHI, z-scores).[ https://github.com/Imswappy/Analytics-Dashboard/](https://github.com/Imswappy/Analytics-Dashboard/)

\[94] streamlit-react-components 1.0.0[ https://pypi.org/project/streamlit-react-components/](https://pypi.org/project/streamlit-react-components/)

\[95] Help for representing data[ https://discuss.streamlit.io/t/help-for-representing-data/48123](https://discuss.streamlit.io/t/help-for-representing-data/48123)

\[96] API Reference - Streamlit Docs[ https://www.aidoczh.com/streamlit/develop/api-reference.html](https://www.aidoczh.com/streamlit/develop/api-reference.html)

\[97] Display progress and status[ https://docs.streamlit.io/library/api-reference/status?ref=blog.streamlit.io](https://docs.streamlit.io/library/api-reference/status?ref=blog.streamlit.io)

\[98] 7 Rain Add-ons for your Stream: "Rainy" | Add on any BG, Image, Video! 3 Step Tutorial\![ https://www.etsy.com/fi-en/listing/1047518592/7-rain-add-ons-for-your-stream-rainy-add](https://www.etsy.com/fi-en/listing/1047518592/7-rain-add-ons-for-your-stream-rainy-add)

\[99] How to create something like st.balloons?[ https://discuss.streamlit.io/t/how-to-create-something-like-st-balloons/55740/3](https://discuss.streamlit.io/t/how-to-create-something-like-st-balloons/55740/3)

\[100] Raining Confetti Overlay | confetti animation | for OBS & Streamlabs[ https://www.etsy.com/listing/4309337957/raining-confetti-overlay-confetti?dd=1\&ga\_order=most\_relevant\&ga\_search\_query=make+it+rain+transparent+stream\&ga\_search\_type=all\&ga\_view\_type=gallery\&ls=s\&pro=1](https://www.etsy.com/listing/4309337957/raining-confetti-overlay-confetti?dd=1\&ga_order=most_relevant\&ga_search_query=make+it+rain+transparent+stream\&ga_search_type=all\&ga_view_type=gallery\&ls=s\&pro=1)

\[101] Confetti Animation Pack[ https://lottiefiles.com/marketplace/confetti-10\_133868](https://lottiefiles.com/marketplace/confetti-10_133868)

\[102] Confetti Animated Twitch Alert, Stream Alert for Streamlabs and StreamElements, Follower, Subscriber, Donation, for Streamers and VTubers[ https://www.etsy.com/fi-en/listing/1680730125/confetti-animated-twitch-alert-stream?dd=1\&ga\_search\_type=all\&ga\_view\_type=gallery\&ls=s](https://www.etsy.com/fi-en/listing/1680730125/confetti-animated-twitch-alert-stream?dd=1\&ga_search_type=all\&ga_view_type=gallery\&ls=s)

> （注：文档部分内容可能由 AI 生成）