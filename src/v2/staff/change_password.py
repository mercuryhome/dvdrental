#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户密码修改程序 (使用 psycopg3)
修改PostgreSQL数据库中staff表的用户密码

本模块使用 psycopg3 进行数据库操作，提供更好的性能和现代化的API设计
支持异步操作和自动资源管理

依赖库:
    - psycopg3: PostgreSQL 数据库适配器 (新一代版本)
    - hashlib: 密码加密
    - sys: 系统相关功能
    - datetime: 日期时间处理
    - os: 操作系统接口

作者: Database Staff Management System
版本: 2.0
"""

import psycopg
import hashlib
import sys
import os
from datetime import datetime
from psycopg import OperationalError


def connect_to_database():
    """
    连接到PostgreSQL数据库 (使用 psycopg3)
    
    Returns:
        psycopg.Connection: 数据库连接对象，失败时返回None
    """
    try:
        # 设置环境变量以确保正确的编码
        os.environ['PGCLIENTENCODING'] = 'UTF8'
        
        # psycopg3 连接参数
        connection_params = {
            'host': 'localhost',
            'port': '5432',
            'dbname': 'dvdrental',  # psycopg3 使用 dbname
            'user': 'postgres',
            'password': 'postgres',  # 请根据实际情况修改密码
            'client_encoding': 'utf8'
        }
        
        connection = psycopg.connect(**connection_params)
        return connection
    except OperationalError as e:
        print(f"数据库连接失败: {e}")
        return None


def verify_old_password(connection, username, old_password):
    """
    验证旧密码是否正确 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        username (str): 用户名
        old_password (str): 旧密码
    
    Returns:
        bool: 密码是否正确
    """
    try:
        with connection.cursor() as cursor:
            # 使用MD5加密旧密码
            old_password_hash = hashlib.md5(old_password.encode()).hexdigest()
            
            # 查询用户是否存在且密码正确
            cursor.execute("""
                SELECT staff_id, first_name, last_name 
                FROM staff 
                WHERE username = %s AND password = %s
            """, (username, old_password_hash))
            
            result = cursor.fetchone()
            return result is not None
            
    except Exception as e:
        print(f"验证旧密码时发生错误: {e}")
        return False


def update_password(connection, username, new_password):
    """
    更新用户密码 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        username (str): 用户名
        new_password (str): 新密码
    
    Returns:
        bool: 更新是否成功
    """
    try:
        with connection.cursor() as cursor:
            # 使用MD5加密新密码
            new_password_hash = hashlib.md5(new_password.encode()).hexdigest()
            
            # 更新密码
            cursor.execute("""
                UPDATE staff 
                SET password = %s, last_update = %s 
                WHERE username = %s
            """, (new_password_hash, datetime.now(), username))
            
            # 检查是否更新了记录
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                return False
                
    except Exception as e:
        print(f"更新密码时发生错误: {e}")
        connection.rollback()
        return False


def get_user_input():
    """
    获取用户输入信息
    
    Returns:
        dict: 用户输入的信息
    """
    print("=" * 50)
    print("密码修改系统 (psycopg3)")
    print("=" * 50)
    
    try:
        username = input("请输入用户名: ").strip()
        if not username:
            raise ValueError("用户名不能为空")
        
        old_password = input("请输入旧密码: ").strip()
        if not old_password:
            raise ValueError("旧密码不能为空")
        
        new_password = input("请输入新密码: ").strip()
        if not new_password:
            raise ValueError("新密码不能为空")
        
        if new_password == old_password:
            raise ValueError("新密码不能与旧密码相同")
        
        confirm_password = input("请确认新密码: ").strip()
        if new_password != confirm_password:
            raise ValueError("两次输入的新密码不一致")
        
        return {
            'username': username,
            'old_password': old_password,
            'new_password': new_password
        }
        
    except KeyboardInterrupt:
        print("\n\n密码修改已取消")
        return None
    except ValueError as e:
        print(f"输入错误: {e}")
        return None


def update_password_interactive():
    """
    交互式密码修改主函数 (使用 psycopg3)
    
    提供交互式界面，允许用户修改密码
    """
    # 连接数据库
    connection = connect_to_database()
    if not connection:
        print("无法连接到数据库，密码修改失败")
        return False
    
    try:
        # 获取用户输入
        user_data = get_user_input()
        if not user_data:
            return False
        
        username = user_data['username']
        old_password = user_data['old_password']
        new_password = user_data['new_password']
        
        # 验证旧密码
        if not verify_old_password(connection, username, old_password):
            print("旧密码错误，密码修改失败")
            return False
        
        # 更新密码
        if update_password(connection, username, new_password):
            print(f"用户 '{username}' 的密码修改成功")
            return True
        else:
            print(f"密码修改失败")
            return False
            
    except KeyboardInterrupt:
        print("\n\n密码修改已取消")
        return False
    except Exception as e:
        print(f"密码修改过程中发生错误: {e}")
        return False
    finally:
        # 关闭数据库连接
        connection.close()


def main():
    """
    主函数
    """
    try:
        success = update_password_interactive()
        
        if success:
            print("\n密码修改系统运行完成")
            sys.exit(0)
        else:
            print("\n密码修改系统运行失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
