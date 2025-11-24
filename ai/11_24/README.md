### 为了配合后端的使用，做出以下两点修改：
1. 将Body_Analysis.py 中 main() 改名为 process_image(image_path)，直接接收图片路径作为参数，并将函数返回改为字典形式，方便后端判断
2. 将Body_ratio.py中的所有print函数删除，改为返回标准的JSON 数据结构

其他地方（如身材计算逻辑，图像处理均未更改）
