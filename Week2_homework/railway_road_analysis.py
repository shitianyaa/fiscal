import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import os
import io
import re
import platform
import matplotlib.font_manager as fm

# 设置中文字体函数
def setup_chinese_font():
    """设置中文字体，解决中文显示问题"""
    system = platform.system()
    
    # 尝试的字体列表（按优先级排序）
    if system == "Windows":
        font_candidates = ["SimHei", "Microsoft YaHei", "KaiTi", "FangSong", "Arial Unicode MS"]
    elif system == "Darwin":  # macOS
        font_candidates = ["Heiti TC", "STHeiti", "PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
    else:  # Linux
        font_candidates = ["WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "DejaVu Sans", "Arial Unicode MS"]
    
    # 检查系统中可用的字体
    available_fonts = []
    for font in font_candidates:
        try:
            # 检查字体是否可用
            if font in [f.name for f in fm.fontManager.ttflist]:
                available_fonts.append(font)
        except:
            pass
    
    if available_fonts:
        # 使用第一个可用的字体
        plt.rcParams["font.family"] = available_fonts
        st.info(f"使用字体: {available_fonts[0]}")
    else:
        # 如果找不到中文字体，使用默认字体并显示警告
        plt.rcParams["font.family"] = ["sans-serif"]
        st.warning("未找到中文字体，图表中的中文可能无法正常显示")
    
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['xtick.labelsize'] = 8

# 应用字体设置
setup_chinese_font()

# 设置页面配置
st.set_page_config(
    page_title="铁路公路运货量分析",
    page_icon="🚂",
    layout="wide"
)

# 标题
st.title("铁路公路运货量对比分析")

# 文件处理 - 支持上传和路径输入
st.sidebar.subheader("数据文件设置")
file_option = st.sidebar.radio("选择数据来源", ("上传文件", "指定路径"))

excel_path = None
uploaded_file = None

if file_option == "上传文件":
    uploaded_file = st.sidebar.file_uploader("上传Excel文件", type=["xls", "xlsx"])
elif file_option == "指定路径":
    default_path = "C:/Users/Shitianyaa/Python/data/national_data/铁路运输.xls"
    excel_path = st.sidebar.text_input("文件路径", default_path)

# 检查文件可用性
if (file_option == "指定路径" and not os.path.exists(excel_path)) or (file_option == "上传文件" and not uploaded_file):
    st.error("请提供有效的Excel文件")
    st.stop()

# 数据加载函数
@st.cache_data
def load_data(file_source):
    """加载并返回数据框"""
    try:
        if isinstance(file_source, str):  # 文件路径
            return pd.read_excel(file_source)
        else:  # 上传的文件
            return pd.read_excel(file_source)
    except Exception as e:
        st.error(f"读取文件失败: {str(e)}")
        st.stop()

# 改进的时间解析函数
def parse_time_column(time_series):
    """改进的时间列解析函数"""
    results = []
    formats = ['%Y年%m月', '%Y-%m', '%Y/%m', '%Y%m', '%Y年%m', '%Y.%m']
    
    for time_val in time_series:
        if pd.isna(time_val):
            results.append(pd.NaT)
            continue
            
        # 如果是datetime类型直接返回
        if isinstance(time_val, datetime):
            results.append(time_val)
            continue
            
        time_str = str(time_val).strip()
        
        # 尝试直接解析为datetime
        try:
            parsed = pd.to_datetime(time_str)
            results.append(parsed)
            continue
        except:
            pass
        
        # 尝试各种格式
        parsed = None
        for fmt in formats:
            try:
                parsed = datetime.strptime(time_str, fmt)
                break
            except:
                continue
        
        # 尝试提取年份和月份
        if parsed is None:
            # 查找4位数字年份
            year_match = re.search(r'(\d{4})', time_str)
            if year_match:
                year = int(year_match.group(1))
                # 查找月份
                month_match = re.search(r'[^\d](\d{1,2})[^\d]', time_str.replace(year_match.group(1), ''))
                month = int(month_match.group(1)) if month_match else 1
                try:
                    parsed = datetime(year, month, 1)
                except:
                    parsed = None
        
        results.append(parsed if parsed is not None else pd.NaT)
    
    return pd.Series(results, index=time_series.index)

# 数据预处理函数
def preprocess_data(df):
    """预处理数据，主要处理时间列"""
    # 自动识别时间列
    time_cols = [col for col in df.columns if any(keyword in str(col) for keyword in ['时间', '日期', '年月', '月份', '时期'])]
    
    if not time_cols:
        st.warning("未发现时间相关列，使用索引作为时间参考")
        df['时间'] = pd.date_range(start='2000-01-01', periods=len(df), freq='M')
        return df
    
    time_col = time_cols[0]
    st.info(f"使用 '{time_col}' 作为时间列")
    
    # 应用时间转换
    original_len = len(df)
    df['时间'] = parse_time_column(df[time_col])
    
    # 清理数据
    cleaned_df = df.dropna(subset=['时间']).copy()
    cleaned_df = cleaned_df.sort_values(by='时间').reset_index(drop=True)
    
    # 检查数据损失
    if len(cleaned_df) < original_len:
        st.warning(f"时间格式转换后数据损失: {original_len - len(cleaned_df)} 行")
    
    return cleaned_df

# 改进的列名匹配函数
def find_matching_columns(df, keywords, exclude_keywords=None):
    """根据关键词列表查找匹配的列名"""
    if exclude_keywords is None:
        exclude_keywords = []
    
    best_match = None
    best_score = 0
    
    for col in df.columns:
        col_str = str(col).lower()
        
        # 排除包含排除关键词的列
        if any(exclude in col_str for exclude in exclude_keywords):
            continue
            
        # 计算匹配分数
        score = sum(1 for keyword in keywords if keyword.lower() in col_str)
        
        # 如果所有关键词都匹配，并且分数更高，则更新最佳匹配
        if score == len(keywords) and score > best_score:
            best_match = col
            best_score = score
        # 如果部分匹配，但分数更高，也考虑
        elif score > best_score:
            best_match = col
            best_score = score
    
    return best_match

# 主逻辑
try:
    # 加载数据
    df = load_data(excel_path if file_option == "指定路径" else uploaded_file)
    
    # 显示原始数据信息
    st.subheader("原始数据信息")
    st.write(f"数据形状: {df.shape} (行: {df.shape[0]}, 列: {df.shape[1]})")
    
    # 显示列信息
    with st.expander("原始列名及数据类型", expanded=False):
        col_info = pd.DataFrame({
            '列索引': range(len(df.columns)),
            '列名': df.columns,
            '数据类型': df.dtypes.astype(str)
        })
        st.dataframe(col_info)
    
    # 预处理数据
    df_processed = preprocess_data(df)
    
    # 显示处理后的数据预览
    with st.expander("处理后的数据预览", expanded=False):
        st.dataframe(df_processed.head(10))
        st.write(f"处理后数据形状: {df_processed.shape}")
    
    # 智能识别相关列 - 改进的匹配逻辑
    railway_columns = {
        '当期值': find_matching_columns(df_processed, ['铁路', '货运量', '当期'], exclude_keywords=['增长', '同比', '累计']),
        '累计值': find_matching_columns(df_processed, ['铁路', '货运量', '累计'], exclude_keywords=['增长', '同比']),
        '同比增长': find_matching_columns(df_processed, ['铁路', '货运量', '同比', '增长']),
        '累计增长': find_matching_columns(df_processed, ['铁路', '货运量', '累计', '增长'])
    }
    
    road_columns = {
        '当期值': find_matching_columns(df_processed, ['公路', '货运量', '当期'], exclude_keywords=['增长', '同比', '累计']),
        '累计值': find_matching_columns(df_processed, ['公路', '货运量', '累计'], exclude_keywords=['增长', '同比']),
        '同比增长': find_matching_columns(df_processed, ['公路', '货运量', '同比', '增长']),
        '累计增长': find_matching_columns(df_processed, ['公路', '货运量', '累计', '增长'])
    }
    
    # 检查并过滤不存在的列 - 修复这里的语法错误
    valid_rail = {k: v for k, v in railway_columns.items() if v is not None}
    valid_road = {k: v for k, v in road_columns.items() if v is not None}  # 修复这里：使用冒号而不是逗号
    
    # 显示找到的列信息
    st.subheader("识别到的数据列")
    col1, col2 = st.columns(2)
    with col1:
        st.write("铁路相关列:")
        for k, v in valid_rail.items():
            st.write(f"  {k}: {v}")
    with col2:
        st.write("公路相关列:")
        for k, v in valid_road.items():
            st.write(f"  {k}: {v}")
    
    # 检查是否有足够的列进行分析
    if not valid_rail or not valid_road:
        st.error("未找到足够的铁路或公路数据列，请检查数据文件")
        st.stop()
    
    # 用户选择数据类型
    st.subheader("数据分析配置")
    available_types = list(set(valid_rail.keys()) & set(valid_road.keys()))
    if not available_types:
        st.error("没有可对比的数据分析类型")
        st.stop()
    
    data_type = st.radio("选择数据类型", available_types)
    
    # 获取对应的列名
    railway_col = valid_rail[data_type]
    road_col = valid_road[data_type]
    
    # 确保使用运货量数据而不是增长率数据进行占比和相关性分析
    volume_rail_col = valid_rail.get('当期值') or valid_rail.get('累计值')
    volume_road_col = valid_road.get('当期值') or valid_road.get('累计值')
    
    # 验证数据列存在
    if not volume_rail_col or not volume_road_col:
        st.error("无法找到运货量数据列进行占比和相关性分析")
        st.stop()
    
    # 确保数据是数值类型
    for col in [railway_col, road_col, volume_rail_col, volume_road_col]:
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    # 移除包含NaN的行
    analysis_df = df_processed.dropna(subset=[volume_rail_col, volume_road_col, '时间']).copy()
    
    if len(analysis_df) == 0:
        st.error("运货量数据无效，无法进行分析")
        st.stop()
    
    # 可视化部分 - 运货量对比
    st.subheader("铁路公路运货量对比")
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(analysis_df['时间']))
    
    # 绘制运货量
    ax.bar(x - width/2, analysis_df[railway_col], width, label='铁路运货量', alpha=0.7, color='blue')
    ax.bar(x + width/2, analysis_df[road_col], width, label='公路运货量', alpha=0.7, color='orange')
    
    # 设置图表属性
    ax.set_xlabel('时间')
    ax.set_ylabel('运货量(万吨)')
    ax.set_title(f'铁路公路{data_type}对比')
    ax.legend(loc='upper left')
    
    # 动态调整x轴刻度
    step = max(1, len(analysis_df) // 15)
    ax.set_xticks(x[::step])
    ax.set_xticklabels([t.strftime('%Y-%m') for t in analysis_df['时间'][::step]], rotation=30, ha='right')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 增长率趋势图（如果存在增长率列）
    railway_growth_col = valid_rail.get('同比增长') or valid_rail.get('累计增长')
    road_growth_col = valid_road.get('同比增长') or valid_road.get('累计增长')
    
    if railway_growth_col or road_growth_col:
        st.subheader("增长率变化趋势")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        
        if railway_growth_col:
            # 确保增长率列是数值类型
            analysis_df[railway_growth_col] = pd.to_numeric(analysis_df[railway_growth_col], errors='coerce')
            ax2.plot(analysis_df['时间'], analysis_df[railway_growth_col], marker='o', label='铁路增长率(%)', color='blue')
        
        if road_growth_col:
            # 确保增长率列是数值类型
            analysis_df[road_growth_col] = pd.to_numeric(analysis_df[road_growth_col], errors='coerce')
            ax2.plot(analysis_df['时间'], analysis_df[road_growth_col], marker='s', label='公路增长率(%)', color='orange')
        
        ax2.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        ax2.set_xlabel('时间')
        ax2.set_ylabel('增长率(%)')
        ax2.set_title(f'铁路公路运货量{data_type}增长率变化趋势')
        ax2.legend()
        
        plt.gcf().autofmt_xdate(rotation=30)
        plt.tight_layout()
        st.pyplot(fig2)
    
    # 修正的堆叠图分析 - 使用运货量数据
    st.subheader("铁路公路运货量占比分析")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    
    # 使用运货量数据而不是增长率数据
    total = analysis_df[volume_rail_col] + analysis_df[volume_road_col]
    
    # 处理除零问题
    valid_mask = total > 0
    if valid_mask.sum() == 0:
        st.warning("运货量数据全为零，无法计算占比")
    else:
        railway_percentage = np.where(valid_mask, (analysis_df[volume_rail_col] / total) * 100, 0)
        road_percentage = np.where(valid_mask, (analysis_df[volume_road_col] / total) * 100, 0)
        
        # 只使用有效数据
        valid_times = analysis_df['时间'][valid_mask]
        valid_rail_pct = railway_percentage[valid_mask]
        valid_road_pct = road_percentage[valid_mask]
        
        if len(valid_times) > 0:
            ax3.stackplot(valid_times, valid_rail_pct, valid_road_pct, 
                         labels=['铁路占比', '公路占比'], colors=['blue', 'orange'], alpha=0.8)
            ax3.set_xlabel('时间')
            ax3.set_ylabel('占比(%)')
            ax3.set_title('铁路公路运货量占比变化趋势')
            ax3.legend(loc='upper left')
            
            plt.gcf().autofmt_xdate(rotation=30)
            plt.tight_layout()
            st.pyplot(fig3)
        else:
            st.warning("没有有效的运货量数据进行占比分析")
    
    # 修正的相关性分析 - 使用运货量数据
    st.subheader("相关性分析")
    
    # 使用运货量数据进行相关性分析
    corr_data = analysis_df[[volume_rail_col, volume_road_col]].dropna()
    
    if len(corr_data) < 2:
        st.warning("数据量不足，无法进行相关性分析")
    else:
        # 计算相关系数
        correlation = np.corrcoef(corr_data[volume_rail_col], corr_data[volume_road_col])[0, 1]
        
        # 判断相关性强度
        if abs(correlation) > 0.7:
            strength = "强"
        elif abs(correlation) > 0.3:
            strength = "中等"
        else:
            strength = "弱"
        
        relation = "正" if correlation > 0 else "负"
        
        st.write(f"铁路与公路运货量相关系数: {correlation:.4f}")
        st.write(f"相关性: {strength}{relation}相关")
        
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        ax4.scatter(corr_data[volume_rail_col], corr_data[volume_road_col], alpha=0.7, color='purple')
        ax4.set_xlabel(f'铁路运货量(万吨)')
        ax4.set_ylabel(f'公路运货量(万吨)')
        ax4.set_title('铁路与公路运货量散点图')
        
        # 添加趋势线（仅当有足够数据点且相关性较强时）
        if len(corr_data) > 2 and abs(correlation) > 0.3:
            z = np.polyfit(corr_data[volume_rail_col], corr_data[volume_road_col], 1)
            p = np.poly1d(z)
            ax4.plot(corr_data[volume_rail_col], p(corr_data[volume_rail_col]), "--", color='red', 
                    label=f'趋势线 (r={correlation:.3f})')
            ax4.legend()
        
        plt.tight_layout()
        st.pyplot(fig4)
    
    # 数据导出功能
    st.subheader("数据导出")
    export_columns = ['时间', railway_col, road_col]
    
    if railway_growth_col:
        export_columns.append(railway_growth_col)
    if road_growth_col:
        export_columns.append(road_growth_col)
    
    export_df = analysis_df[export_columns].copy()
    # 格式化时间列
    export_df['时间'] = export_df['时间'].dt.strftime('%Y-%m')
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="下载分析数据 (CSV)",
        data=csv,
        file_name=f"铁路公路运货量分析_{data_type}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    
    # 统计摘要
    st.subheader("统计摘要")
    
    # 准备统计数据
    stats_data = {'指标': ['平均值', '最大值', '最小值', '标准差', '数据量']}
    
    # 铁路运货量统计
    rail_stats = [
        analysis_df[railway_col].mean(),
        analysis_df[railway_col].max(),
        analysis_df[railway_col].min(),
        analysis_df[railway_col].std(),
        analysis_df[railway_col].count()
    ]
    stats_data['铁路运货量'] = rail_stats
    
    # 公路运货量统计
    road_stats = [
        analysis_df[road_col].mean(),
        analysis_df[road_col].max(),
        analysis_df[road_col].min(),
        analysis_df[road_col].std(),
        analysis_df[road_col].count()
    ]
    stats_data['公路运货量'] = road_stats
    
    # 增长率统计（如果存在）
    if railway_growth_col:
        rail_growth_stats = [
            analysis_df[railway_growth_col].mean(),
            analysis_df[railway_growth_col].max(),
            analysis_df[railway_growth_col].min(),
            analysis_df[railway_growth_col].std(),
            analysis_df[railway_growth_col].count()
        ]
        stats_data['铁路增长率(%)'] = rail_growth_stats
    
    if road_growth_col:
        road_growth_stats = [
            analysis_df[road_growth_col].mean(),
            analysis_df[road_growth_col].max(),
            analysis_df[road_growth_col].min(),
            analysis_df[road_growth_col].std(),
            analysis_df[road_growth_col].count()
        ]
        stats_data['公路增长率(%)'] = road_growth_stats
    
    # 创建统计表格
    stats_df = pd.DataFrame(stats_data)
    
    # 格式化数值
    for col in stats_df.columns[1:]:
        stats_df[col] = stats_df[col].apply(
            lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and not np.isnan(x) else "N/A"
        )
    
    st.dataframe(stats_df)
    
except Exception as e:
    st.error(f"处理数据时出错: {str(e)}")
    st.exception(e)