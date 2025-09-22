#~~大二下金融数据分析，仅用于大二上的课程学习~~

#9.20日不小心把大一的python代码上传了进去，不知道怎么删

#9.22上传周二所用到的代码，其中
  - ailway_road_app.py - 包含完整的铁路公路运货量对比分析Streamlit应用
  - check_excel_structure.py - 用于检查Excel文件结构的脚本
  - railway_road_analysis.py - 基本的数据读取和分析脚本
若要运行，则py文件中
  - ailway_road_app.py         第13行文件路径
  - check_excel_structure.py   第5行文件路径
  - railway_road_analysis.py   第23行文件路径
  需要修改为"铁路运输.xls"所作位置(例如"C:/Users/Shitianyaa/Python/data/national_data/铁路运输.xls")

运行需要：
   - 1.确保安装了所有必要的库（pandas、streamlit、matplotlib、numpy等）
  - 2.导航到保存文件的目录
  - 3.运行命令： streamlit run railway_road_app.py
这样，Streamlit应用会启动，并默认使用相同的8501端口，可在自己的浏览器中访问 http://localhost:8501
