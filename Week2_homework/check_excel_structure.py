import pandas as pd
import os

# 文件路径
excel_path = "C:/Users/Shitianyaa/Python/data/national_data/铁路运输.xls"

# 检查文件是否存在
if os.path.exists(excel_path):
    print(f"文件存在: {excel_path}")
    print(f"文件大小: {os.path.getsize(excel_path)/1024:.2f} KB")
    
    # 读取Excel文件信息
    try:
        # 打印工作表名称
        xl = pd.ExcelFile(excel_path)
        print(f"工作表名称: {xl.sheet_names}")
        
        # 读取第一个工作表
        df = pd.read_excel(excel_path, sheet_name=xl.sheet_names[0])
        
        print(f"\n数据形状: {df.shape}")
        print("\n列名:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
        
        print("\n前5行数据:")
        print(df.head())
        
        print("\n数据类型:")
        print(df.dtypes)
        
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
else:
    print(f"文件不存在: {excel_path}")