#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 数据库连接测试程序 (使用 psycopg3)
连接参数: localhost:5432, 用户: postgres, 数据库: dvdrental
"""

import psycopg
import sys
import os
from psycopg import OperationalError


def safe_str_decode(text):
    """
    安全地处理可能包含非UTF-8字符的字符串
    """
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            return text.decode('utf-8', errors='replace')
    else:
        try:
            return str(text)
        except UnicodeDecodeError:
            return str(text).encode('utf-8', errors='replace').decode('utf-8')


def test_database_connection():
    """
    测试PostgreSQL数据库连接 (使用 psycopg3)
    连接成功返回OK，失败返回错误信息
    """
    # 设置环境变量以确保正确的编码
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    
    # 数据库连接参数 (psycopg3 使用不同的参数格式)
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',  # 默认密码，请根据实际情况修改
        'dbname': 'dvdrental',  # psycopg3 使用 dbname 而不是 database
        'client_encoding': 'utf8'  # 明确指定客户端编码
    }
    
    try:
        # 尝试连接数据库
        print("正在连接数据库...")
        print(f"主机: {connection_params['host']}")
        print(f"端口: {connection_params['port']}")
        print(f"用户: {connection_params['user']}")
        print(f"数据库: {connection_params['dbname']}")
        
        # 建立连接 (psycopg3 使用不同的连接方式)
        with psycopg.connect(**connection_params) as connection:
            # 创建游标
            with connection.cursor() as cursor:
                # 执行简单查询测试连接
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                
                # 安全地处理数据库版本信息
                version_str = safe_str_decode(db_version[0])
                print(f"数据库版本: {version_str}")
                print("数据库连接成功!")
        
        return "OK"
        
    except OperationalError as e:
        error_msg = f"数据库连接失败: {str(e)}"
        print(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"发生未知错误: {str(e)}"
        print(error_msg)
        return error_msg


def test_advanced_features():
    """
    测试 psycopg3 的高级功能
    """
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
        'dbname': 'dvdrental',
        'client_encoding': 'utf8'
    }
    
    try:
        print("\n" + "=" * 50)
        print("测试 psycopg3 高级功能")
        print("=" * 50)
        
        with psycopg.connect(**connection_params) as connection:
            with connection.cursor() as cursor:
                # 测试事务功能
                print("测试事务功能...")
                cursor.execute("BEGIN;")
                
                # 查询数据库中的表数量
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                print(f"数据库中的表数量: {table_count}")
                
                # 查询一些示例数据
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name 
                    LIMIT 5
                """)
                tables = cursor.fetchall()
                print("前5个表名:")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # 测试参数化查询
                print("\n测试参数化查询...")
                cursor.execute("SELECT current_database(), current_user, version()")
                db_info = cursor.fetchone()
                print(f"当前数据库: {db_info[0]}")
                print(f"当前用户: {db_info[1]}")
                print(f"PostgreSQL版本: {safe_str_decode(db_info[2])}")
                
                cursor.execute("COMMIT;")
                print("事务提交成功!")
                
        return "OK"
        
    except Exception as e:
        error_msg = f"高级功能测试失败: {str(e)}"
        print(error_msg)
        return error_msg


def main():
    """
    主函数
    """
    print("=" * 50)
    print("PostgreSQL 数据库连接测试 (psycopg3)")
    print("=" * 50)
    
    # 基本连接测试
    result = test_database_connection()
    
    print("=" * 50)
    print(f"基本连接测试结果: {result}")
    print("=" * 50)
    
    # 如果基本连接成功，进行高级功能测试
    if result == "OK":
        advanced_result = test_advanced_features()
        print("=" * 50)
        print(f"高级功能测试结果: {advanced_result}")
        print("=" * 50)
        
        # 如果所有测试都成功，退出码为0；否则为1
        if advanced_result == "OK":
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
