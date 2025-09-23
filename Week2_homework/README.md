#9.22上传第二周作业所用到的代码，其中
  - ailway_road_app.py - 包含完整的铁路公路运货量对比分析Streamlit应用
  - check_excel_structure.py - 用于检查Excel文件结构的脚本
  - railway_road_analysis.py - 基本的数据读取和分析脚本

  若要成功运行，则py文件中
  - ailway_road_app.py         第13行文件路径
  - check_excel_structure.py   第5行文件路径
  - railway_road_analysis.py   第23行文件路径
  需要修改为"铁路运输.xls"所作位置(例如"C:/Users/Shitianyaa/Python/data/national_data/铁路运输.xls")

  运行需要：
  - 1.确保安装了所有必要的库（pandas、streamlit、matplotlib、numpy等）
  - 2.导航到保存文件的目录
  - 3.运行命令： streamlit run railway_road_app.py
  这样，Streamlit应用会启动，并默认使用相同的8501端口，可在自己的浏览器中访问 http://localhost:8501

##9.22修复了以下问题
- 铁路公路数据时间显示异常
- 部分字体重影
- 部分数据计算错误

  优化了文件处理逻辑，现在下载完文件，并安装好必要的库（pandas、streamlit、matplotlib、numpy等）后，在代码文件所在位置运行终端并输入 streamlit run railway_road_analysis.py
  可以选择要上传分析的文件，不用对源代码进行更改

#9.23修复终端重复提示"findfont: Font family 'WenQuanYi Micro Hei' not found.  findfont: Font family 'Heiti TC' not found."的问题
