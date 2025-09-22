import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import os

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取Excel文件
excel_path = "C:/Users/Shitianyaa/Python/data/national_data/铁路运输.xls"

# 检查文件是否存在
if not os.path.exists(excel_path):
    st.error(f"文件不存在: {excel_path}")
    st.stop()

# 尝试读取文件
try:
    # 先读取前几行查看数据结构
    df_sample = pd.read_excel(excel_path, nrows=20)
    st.write("数据样例:")
    st.dataframe(df_sample)
    
    # 尝试读取所有数据
    df = pd.read_excel(excel_path)
    st.write(f"数据形状: {df.shape}")
    st.write("数据列名:")
    st.write(df.columns.tolist())
    
    # 显示数据信息
    buffer = []
    df.info(buf=buffer)
    st.text('\n'.join(buffer))
    
    # 显示基本统计信息
    st.write("基本统计信息:")
    st.dataframe(df.describe())
    
    # 这里需要根据实际数据结构调整后续分析代码
    # 假设数据中有日期、铁路运货量、公路运货量等列
    
except Exception as e:
    st.error(f"读取文件时出错: {str(e)}")