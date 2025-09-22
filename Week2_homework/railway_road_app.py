import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import os

# 设置页面配置
st.set_page_config(
    page_title="铁路公路运货量分析",
    page_icon="🚂",
    layout="wide"
)

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 标题
st.title("铁路公路运货量对比分析")

# 文件路径
excel_path = "C:/Users/Shitianyaa/Python/data/national_data/铁路运输.xls"

# 检查文件是否存在
if not os.path.exists(excel_path):
    st.error(f"文件不存在: {excel_path}")
    st.stop()

# 读取Excel文件
try:
    # 读取文件
    df = pd.read_excel(excel_path)
    
    # 数据预处理函数
    def preprocess_data(df):
        # 转换时间列格式
        def parse_time(time_str):
            try:
                # 处理"2025年6月"格式
                if isinstance(time_str, str):
                    year = int(time_str[:4])
                    # 处理可能的不同格式
                    if '年' in time_str and '月' in time_str:
                        month_part = time_str.split('年')[1].split('月')[0]
                        month = int(month_part) if month_part else 1
                    else:
                        month = int(time_str[5:7]) if len(time_str) > 5 else 1
                    return datetime(year, month, 1)
                return time_str
            except:
                # 如果转换失败，返回原始值
                return time_str
        
        # 应用时间转换
        df['时间'] = df['时间'].apply(parse_time)
        
        # 确保时间列所有值都是datetime类型
        # 对于无法转换的值，尝试其他处理方法或标记为NaT
        df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
        
        # 按时间排序
        df = df.sort_values(by='时间')
        
        # 移除时间为NaT的行
        df = df.dropna(subset=['时间'])
        
        return df
    
    # 预处理数据
    df = preprocess_data(df)
    
    # 显示数据预览
    st.subheader("数据预览")
    st.dataframe(df.head(10))
    
    # 显示数据信息
    st.subheader("数据信息")
    import io
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())
    
    # 自动识别相关列
    railway_columns = {
        '当期值': '铁路货运量当期值(万吨)',
        '累计值': '铁路货运量累计值(万吨)',
        '同比增长': '铁路货运量同比增长(%)',
        '累计增长': '铁路货运量累计增长(%)'
    }
    
    road_columns = {
        '当期值': '公路货运量当期值(万吨)',
        '累计值': '公路货运量累计值(万吨)',
        '同比增长': '公路货运量同比增长(%)',
        '累计增长': '公路货运量累计增长(%)'
    }
    
    # 检查列是否存在
    for col_type, col_name in list(railway_columns.items()):
        if col_name not in df.columns:
            st.warning(f"列不存在: {col_name}")
            del railway_columns[col_type]
    
    for col_type, col_name in list(road_columns.items()):
        if col_name not in df.columns:
            st.warning(f"列不存在: {col_name}")
            del road_columns[col_type]
    
    # 用户选择数据类型
    st.subheader("数据分析配置")
    
    # 选择数据类型（当期值或累计值）
    data_type = st.radio(
        "选择数据类型",
        ('当期值', '累计值')
    )
    
    # 获取对应的列名
    railway_col = railway_columns.get(data_type, list(railway_columns.values())[0])
    road_col = road_columns.get(data_type, list(road_columns.values())[0])
    
    # 获取增长率列
    railway_growth_col = railway_columns.get('同比增长' if data_type == '当期值' else '累计增长')
    road_growth_col = road_columns.get('同比增长' if data_type == '当期值' else '累计增长')
    
    # 可视化部分
    st.subheader("铁路公路运货量对比")
    
    # 创建运货量对比图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 使用双Y轴
    ax2 = ax.twinx()
    
    # 绘制运货量
    width = 0.35
    x = np.arange(len(df['时间']))
    
    # 铁路数据
    ax.bar(x - width/2, df[railway_col], width, label='铁路运货量', alpha=0.7, color='blue')
    
    # 公路数据
    ax.bar(x + width/2, df[road_col], width, label='公路运货量', alpha=0.7, color='orange')
    
    # 设置图表属性
    ax.set_xlabel('时间')
    ax.set_ylabel('运货量(万吨)')
    ax.set_title(f'铁路公路{data_type}对比')
    ax.legend(loc='upper left')
    
    # 设置x轴刻度
    ax.set_xticks(x)
    ax.set_xticklabels([str(t)[:7] for t in df['时间']], rotation=45)
    
    plt.tight_layout()
    
    # 显示图表
    st.pyplot(fig)
    
    # 创建增长率趋势图
    st.subheader("增长率变化趋势")
    
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    # 绘制增长率
    if railway_growth_col:
        ax2.plot(df['时间'], df[railway_growth_col], marker='o', label='铁路增长率(%)', color='blue')
    if road_growth_col:
        ax2.plot(df['时间'], df[road_growth_col], marker='s', label='公路增长率(%)', color='orange')
    
    # 添加零线
    ax2.axhline(y=0, color='r', linestyle='-', alpha=0.3)
    
    # 设置图表属性
    ax2.set_xlabel('时间')
    ax2.set_ylabel('增长率(%)')
    ax2.set_title(f'铁路公路运货量{data_type}增长率变化趋势')
    ax2.legend()
    
    # 自动格式化x轴日期
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    # 显示图表
    st.pyplot(fig2)
    
    # 堆叠图分析
    st.subheader("铁路公路运货量占比分析")
    
    # 创建堆叠图
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    
    # 计算总和用于百分比计算
    total = df[railway_col] + df[road_col]
    railway_percentage = (df[railway_col] / total) * 100
    road_percentage = (df[road_col] / total) * 100
    
    # 绘制堆叠图
    ax3.stackplot(df['时间'], railway_percentage, road_percentage, labels=['铁路占比', '公路占比'], 
                 colors=['blue', 'orange'], alpha=0.8)
    
    # 设置图表属性
    ax3.set_xlabel('时间')
    ax3.set_ylabel('占比(%)')
    ax3.set_title(f'铁路公路运货量{data_type}占比变化趋势')
    ax3.legend(loc='upper left')
    
    # 自动格式化x轴日期
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    # 显示图表
    st.pyplot(fig3)
    
    # 相关性分析
    st.subheader("相关性分析")
    
    # 计算相关系数
    correlation = df[[railway_col, road_col]].corr().iloc[0, 1]
    st.write(f"铁路与公路运货量相关系数: {correlation:.4f}")
    
    # 散点图
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.scatter(df[railway_col], df[road_col], alpha=0.7, color='purple')
    ax4.set_xlabel('铁路运货量(万吨)')
    ax4.set_ylabel('公路运货量(万吨)')
    ax4.set_title('铁路与公路运货量散点图')
    
    # 添加趋势线
    if len(df) > 1:
        # 同时删除两列中的NaN值，确保x和y长度一致
        clean_data = df[[railway_col, road_col]].dropna()
        if len(clean_data) > 1:
            z = np.polyfit(clean_data[railway_col], clean_data[road_col], 1)
            p = np.poly1d(z)
            ax4.plot(clean_data[railway_col], p(clean_data[railway_col]), "--", color='red')
    
    plt.tight_layout()
    st.pyplot(fig4)
    
    # 数据导出功能
    st.subheader("数据导出")
    
    # 准备导出数据
    export_columns = ['时间', railway_col, road_col]
    if railway_growth_col:
        export_columns.append(railway_growth_col)
    if road_growth_col:
        export_columns.append(road_growth_col)
    
    export_df = df[export_columns]
    
    # 转换为CSV
    csv = export_df.to_csv(index=False).encode('utf-8')
    
    # 提供下载按钮
    st.download_button(
        label="下载分析数据 (CSV)",
        data=csv,
        file_name=f"铁路公路运货量分析_{data_type}.csv",
        mime="text/csv",
    )
    
    # 添加统计摘要
    st.subheader("统计摘要")
    
    # 计算统计信息
    stats_data = {
        '指标': ['平均值', '最大值', '最小值', '标准差'],
        '铁路运货量': [
            df[railway_col].mean(),
            df[railway_col].max(),
            df[railway_col].min(),
            df[railway_col].std()
        ],
        '公路运货量': [
            df[road_col].mean(),
            df[road_col].max(),
            df[road_col].min(),
            df[road_col].std()
        ]
    }
    
    if railway_growth_col:
        stats_data['铁路增长率'] = [
            df[railway_growth_col].mean(),
            df[railway_growth_col].max(),
            df[railway_growth_col].min(),
            df[railway_growth_col].std()
        ]
    
    if road_growth_col:
        stats_data['公路增长率'] = [
            df[road_growth_col].mean(),
            df[road_growth_col].max(),
            df[road_growth_col].min(),
            df[road_growth_col].std()
        ]
    
    # 创建统计数据框
    stats_df = pd.DataFrame(stats_data)
    
    # 格式化数值
    numeric_cols = stats_df.columns[1:]
    stats_df[numeric_cols] = stats_df[numeric_cols].applymap(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
    
    # 显示统计摘要
    st.dataframe(stats_df)
    
except Exception as e:
    st.error(f"处理数据时出错: {str(e)}")
    st.exception(e)