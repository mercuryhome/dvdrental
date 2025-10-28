#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 数据库连接测试程序 (使用 psycopg2)
连接参数: localhost:5432, 用户: postgres, 数据库: dvdrental

本程序使用 psycopg2 库进行 PostgreSQL 数据库连接测试
psycopg2 是 Python 中最流行的 PostgreSQL 适配器之一

依赖库:
    - psycopg2: PostgreSQL 数据库适配器
    - sys: 系统相关功能
    - os: 操作系统接口

作者: Database Test Suite
版本: 1.0
"""

import psycopg2
import sys
import os
from psycopg2 import OperationalError


def safe_str_decode(text):
    """
    安全地处理可能包含非UTF-8字符的字符串
    
    在 Windows WSL 环境中，PostgreSQL 返回的数据可能包含非UTF-8字符
    此函数确保字符串能够安全地转换为UTF-8编码
    
    Args:
        text: 需要处理的文本，可能是字符串或字节对象
        
    Returns:
        str: 安全转换后的UTF-8字符串
    """
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            # 如果解码失败，使用替换字符
            return text.decode('utf-8', errors='replace')
    else:
        try:
            return str(text)
        except UnicodeDecodeError:
            # 对于字符串对象，先编码再解码
            return str(text).encode('utf-8', errors='replace').decode('utf-8')


def test_database_connection():
    """
    测试PostgreSQL数据库连接 (使用 psycopg2)
    
    此函数使用 psycopg2.connect() 建立数据库连接，
    执行简单的版本查询来验证连接是否成功
    
    Returns:
        str: 连接成功返回 "OK"，失败返回错误信息
    """
    # 设置环境变量以确保正确的编码
    # 这在 WSL 环境中特别重要，可以避免编码问题
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    
    # psycopg2 数据库连接参数
    # 注意：psycopg2 使用 'database' 参数名
    connection_params = {
        'host': 'localhost',           # 数据库主机地址
        'port': 5432,                 # PostgreSQL 默认端口
        'user': 'postgres',           # 数据库用户名
        'password': 'postgres',       # 数据库密码，请根据实际情况修改
        'database': 'dvdrental',      # 目标数据库名称
        'client_encoding': 'utf8'     # 明确指定客户端编码为UTF-8
    }
    
    try:
        # 尝试连接数据库
        print("正在连接数据库...")
        print(f"主机: {connection_params['host']}")
        print(f"端口: {connection_params['port']}")
        print(f"用户: {connection_params['user']}")
        print(f"数据库: {connection_params['database']}")
        
        # 使用 psycopg2.connect() 建立数据库连接
        connection = psycopg2.connect(**connection_params)
        
        # 创建数据库游标对象
        # 游标用于执行SQL语句和获取结果
        cursor = connection.cursor()
        
        # 执行简单查询测试连接
        # SELECT version() 是 PostgreSQL 的内置函数，返回数据库版本信息
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        # 安全地处理数据库版本信息
        # 使用 safe_str_decode 函数处理可能的编码问题
        version_str = safe_str_decode(db_version[0])
        print(f"数据库版本: {version_str}")
        print("数据库连接成功!")
        
        # 关闭游标和连接
        # 这是良好的编程实践，释放数据库资源
        cursor.close()
        connection.close()
        
        return "OK"
        
    except OperationalError as e:
        # 捕获 psycopg2 的操作错误
        # 这通常表示连接参数错误或数据库服务不可用
        error_msg = f"数据库连接失败: {str(e)}"
        print(error_msg)
        return error_msg
        
    except Exception as e:
        # 捕获其他未知错误
        # 这包括编码错误、网络问题等
        error_msg = f"发生未知错误: {str(e)}"
        print(error_msg)
        return error_msg


def main():
    """
    主函数
    
    程序的入口点，负责协调整个测试流程
    """
    print("=" * 50)
    print("PostgreSQL 数据库连接测试 (psycopg2)")
    print("=" * 50)
    
    # 执行数据库连接测试
    result = test_database_connection()
    
    print("=" * 50)
    print(f"测试结果: {result}")
    print("=" * 50)
    
    # 根据测试结果设置退出码
    # 0 表示成功，1 表示失败
    # 这有助于脚本在自动化环境中使用
    if result == "OK":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    # 当脚本直接运行时执行主函数
    # 这允许脚本既可以作为模块导入，也可以直接执行
    main()
