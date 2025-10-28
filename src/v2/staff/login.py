#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户登录程序 (使用 psycopg3)
验证PostgreSQL数据库中staff表的用户凭据

本模块使用 psycopg3 进行数据库操作，提供更好的性能和现代化的API设计
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


def authenticate_user(connection, username, password):
    """
    验证用户凭据 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        username (str): 用户名
        password (str): 密码
    
    Returns:
        dict: 用户信息（如果验证成功）或None（如果验证失败）
    """
    try:
        with connection.cursor() as cursor:
            # 使用MD5加密密码
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            # 查询用户信息
            cursor.execute("""
                SELECT staff_id, first_name, last_name, email, username, 
                       address_id, store_id, active, last_update
                FROM staff 
                WHERE username = %s AND password = %s
            """, (username, password_hash))
            
            result = cursor.fetchone()
            
            if result:
                # 构建用户信息字典
                user_info = {
                    'staff_id': result[0],
                    'first_name': result[1],
                    'last_name': result[2],
                    'email': result[3],
                    'username': result[4],
                    'address_id': result[5],
                    'store_id': result[6],
                    'active': result[7],
                    'last_update': result[8]
                }
                return user_info
            else:
                return None
                
    except Exception as e:
        print(f"用户验证过程中发生错误: {e}")
        return None


def update_last_login(connection, staff_id):
    """
    更新用户最后登录时间 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        staff_id (int): 职员ID
    
    Returns:
        bool: 更新是否成功
    """
    try:
        with connection.cursor() as cursor:
            # 更新最后登录时间
            cursor.execute("""
                UPDATE staff 
                SET last_update = %s 
                WHERE staff_id = %s
            """, (datetime.now(), staff_id))
            
            connection.commit()
            return True
            
    except Exception as e:
        print(f"更新登录时间失败: {e}")
        connection.rollback()
        return False


def login_user():
    """
    用户登录主函数 (使用 psycopg3)
    
    提供交互式登录界面，验证用户凭据并显示登录结果
    """
    print("=" * 50)
    print("职员登录系统 (psycopg3)")
    print("=" * 50)
    
    # 连接数据库
    connection = connect_to_database()
    if not connection:
        print("无法连接到数据库，登录失败")
        return False
    
    try:
        # 获取用户输入
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()
        
        if not username or not password:
            print("用户名和密码不能为空")
            return False
        
        # 验证用户凭据
        user_info = authenticate_user(connection, username, password)
        
        if user_info:
            print("\n登录成功!")
            print(f"欢迎, {user_info['first_name']} {user_info['last_name']}")
            print(f"职员ID: {user_info['staff_id']}")
            print(f"邮箱: {user_info['email']}")
            print(f"店铺ID: {user_info['store_id']}")
            print(f"状态: {'活跃' if user_info['active'] else '非活跃'}")
            
            # 更新最后登录时间
            if update_last_login(connection, user_info['staff_id']):
                print("登录时间已更新")
            
            return True
        else:
            print("\n登录失败!")
            print("用户名或密码错误，或用户不存在")
            return False
            
    except KeyboardInterrupt:
        print("\n\n登录已取消")
        return False
    except Exception as e:
        print(f"登录过程中发生错误: {e}")
        return False
    finally:
        # 关闭数据库连接
        connection.close()


def main():
    """
    主函数
    """
    try:
        success = login_user()
        if success:
            print("\n登录系统运行完成")
            sys.exit(0)
        else:
            print("\n登录系统运行失败")
            sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
