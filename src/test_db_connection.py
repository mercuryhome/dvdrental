#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 数据库连接测试程序
连接参数: localhost:5432, 用户: postgres, 数据库: dvdrental
"""

import psycopg2
import sys
from psycopg2 import OperationalError


def test_database_connection():
    """
    测试PostgreSQL数据库连接
    连接成功返回OK，失败返回错误信息
    """
    # 数据库连接参数
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',  # 默认密码，请根据实际情况修改
        'database': 'dvdrental'
    }
    
    try:
        # 尝试连接数据库
        print("正在连接数据库...")
        print(f"主机: {connection_params['host']}")
        print(f"端口: {connection_params['port']}")
        print(f"用户: {connection_params['user']}")
        print(f"数据库: {connection_params['database']}")
        
        # 建立连接
        connection = psycopg2.connect(**connection_params)
        
        # 创建游标
        cursor = connection.cursor()
        
        # 执行简单查询测试连接
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print(f"数据库版本: {db_version[0]}")
        print("数据库连接成功!")
        
        # 关闭游标和连接
        cursor.close()
        connection.close()
        
        return "OK"
        
    except OperationalError as e:
        error_msg = f"数据库连接失败: {str(e)}"
        print(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"发生未知错误: {str(e)}"
        print(error_msg)
        return error_msg


def main():
    """
    主函数
    """
    print("=" * 50)
    print("PostgreSQL 数据库连接测试")
    print("=" * 50)
    
    result = test_database_connection()
    
    print("=" * 50)
    print(f"测试结果: {result}")
    print("=" * 50)
    
    # 如果连接成功，退出码为0；否则为1
    if result == "OK":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
