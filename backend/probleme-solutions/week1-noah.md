# 11/17 python 环境配置和项目基础理解
1. 虚拟环境
    - **conda**环境适合管理多语言和科学计算、
      - conda不仅管理python的各种包还管理python的解释器
      - 
    - **venv**创建虚拟环境适合比较轻量的python项目   
   &emsp;  
    - 虚拟环境是本地化的，团队成员通过共享`environment.yml`文件来重现不同设备相同的开发环境

2. 项目协作
    - 从远端拉取文件夹，在文件夹下的backend中创建我的虚拟虚拟环境，写我的代码
    - 后端两个人，一个创建了虚拟环境之后，另一个从远端拉取仓库之后需要重新创建虚拟环境，根据环境清单（environment.yml）  
    - 包含所有库的环境的文件夹非常大，不应该上传到git仓库，通常把虚拟环境文件夹添加到.gitignore文件中  
    - .gitignore文件的作用是告诉git,我的哪些文件不需要你跟踪，不需要上传到远端仓库，所以要把虚拟环境文件夹添加到.gitignore文件里面  


3. 虚拟环境下载的包在电脑中的存储位置
   - 使用 venv (Python 内置)
   >使用python内置的pip创建虚拟环境下载的包会存在项目文件夹下，项目文件夹在哪个盘这个包就占用哪个盘的空间。venv 旨在将环境紧密地捆绑在项目文件夹内。如果您的项目在 D 盘，那么 venv 文件夹和所有包就会占用 D 盘空间。
   - 使用conda  
   > 如果是使用conda创建虚拟环境，那么虚拟环境中下载的包，会存在Anaconda中的envs文件夹里面的文件夹是吗。(当然也可以使用命令指定存储位置)


# 11/18 虚拟环境的创建
## 一、本地创建虚拟环境
1. 打开终端输入`conda env list` 检查当前有虚拟环境列表
2. `conda create -n name-of-your-environment python=you-want-version(3.9)`创建虚拟环境
3. `conda activate name-of-your-environment` 激活虚拟环境
4. `conda deactivate` 切换虚拟环境的时候使用 

## 二、项目协作统一环境
1. 先从远端拉取仓库  
2. 第一次拉取仓库（本地还没有创建项目需要的虚拟环境的时候）
   - `conda env create -f environment.yml`，这个命令会让拉取人的本地创建一个跟项目伙伴同名的虚拟环境  
3. 如果是开发过程中，环境有更新就使用 `conda env update -f environment.yml` 来更新本地的虚拟环境

## 三、项目协作过程中推荐的操作流程
1. 同步代码 (Git Pull)
2. 同步环境 (Conda Update)
3. 激活环境 (Conda Activate)
4. 开始开发
5. 开发结束完成提交 (Git commit & push)

## 四、Git操作
1. 从远端仓库克隆
   - 在自己想要存储项目文件夹的地方右键打开git bash或者是随便一个地方打开git bash再用cd命令换到自己想要的文件夹位置
   - 使用`git clone [远程仓库的url]`,git就会将远程仓库的代码下载到这个文件夹下面
   - 不用担心不同的人员存储位置名字的不同导致push的时候的矛盾   


# 11/19 
## json文件是什么  
- JavaScript Object Notation 本质上就是一个纯文本文件，专门用来存储和传输数据  
- 格式和python中的字典和列表几乎一样  
- 结构：
  - `[]`中括号表示一个数组，python中叫列表，里面是一组有序的数据。
  - `{}`大括号代表一个对象，python中叫字典，里面是`key:value`的键值对  
  - json文件中所有的字符串都要用`" "`双引号，不可以用单引号  

## json文件在项目中的作用
当项目不想安装庞大的数据库（MySQL），JSON文件就是最好的替代品  
前端发给后端的数据就是JSON文件  
后端发给大模型的数据->JSON文件  
大模型返回给后端的数据->JSON文件  

## python中关于列表和字典的相关知识  
1. 列表 `[]`  
   - 存放同类型有序的数据
   - 相当于数组  
   - 支持创建、查找、增加（列表末端增加）、遍历等操作
2. 字典 `{}`  
   - 描述一个对象的详细属性，比如一件衣服想要知道他的id、价格、尺码
      ```python
         # 描述一件衣服
         t_shirt = {
            "name": "白色纯棉T恤",
            "price": 99,
            "size": "M",
            "is_stock": True
         }
      ```
   - 查找操作：通过**键**来查找**值**  
      ```python
         print(t_shirt["name"])   # 输出: 白色纯棉T恤
         print(t_shirt["price"])  # 输出: 99
      ```
   - 安全查找方法`get()`函数  
      ```python
         print(t_shirt["color"])  # 报错！因为字典里没有 "color"
         print(t_shirt.get("color")) # 输出: None (安全)
      ```  
3. 将列表和字典相互嵌套就是JSON的结构  

## 项目前端、后端、AI之间的接口设计和协作规范  
### 后端与AI端
#### 主要场景
1. 后端接收到前端传来的图片之后，需要调用ai端提供的函数  
2. 前端用户点击“开始分析”之后，发送请求给后端  
3. 


