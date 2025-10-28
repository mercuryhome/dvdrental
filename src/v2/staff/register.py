#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户注册程序 (使用 psycopg3)
将用户信息保存到PostgreSQL数据库的staff表中

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


def check_username_exists(connection, username):
    """
    检查用户名是否已存在 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        username (str): 用户名
    
    Returns:
        bool: 用户名是否存在
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM staff WHERE username = %s
            """, (username,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
    except Exception as e:
        print(f"检查用户名时发生错误: {e}")
        return True  # 出错时假设用户名已存在，避免重复注册


def check_email_exists(connection, email):
    """
    检查邮箱是否已存在 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        email (str): 邮箱地址
    
    Returns:
        bool: 邮箱是否存在
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM staff WHERE email = %s
            """, (email,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
    except Exception as e:
        print(f"检查邮箱时发生错误: {e}")
        return True  # 出错时假设邮箱已存在，避免重复注册


def get_next_staff_id(connection):
    """
    获取下一个可用的职员ID (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
    
    Returns:
        int: 下一个职员ID
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(MAX(staff_id), 0) + 1 FROM staff
            """)
            
            next_id = cursor.fetchone()[0]
            return next_id
            
    except Exception as e:
        print(f"获取下一个职员ID时发生错误: {e}")
        return 1  # 默认返回1


def register_user(first_name, last_name, username, password, email, address_id, store_id):
    """
    注册新用户到staff表 (使用 psycopg3)
    
    Args:
        first_name (str): 名字
        last_name (str): 姓氏
        username (str): 用户名
        password (str): 密码
        email (str): 邮箱
        address_id (int): 地址ID
        store_id (int): 店铺ID
    
    Returns:
        bool: 注册是否成功
    """
    connection = None
    try:
        # 连接数据库
        connection = connect_to_database()
        if not connection:
            return False
        
        # 检查用户名是否已存在
        if check_username_exists(connection, username):
            print(f"用户名 '{username}' 已存在，请选择其他用户名")
            return False
        
        # 检查邮箱是否已存在
        if check_email_exists(connection, email):
            print(f"邮箱 '{email}' 已被使用，请使用其他邮箱")
            return False
        
        # 获取下一个职员ID
        staff_id = get_next_staff_id(connection)
        
        # 使用MD5加密密码
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # 插入新用户
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO staff (
                    staff_id, first_name, last_name, email, username, 
                    password, address_id, store_id, active, last_update
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                staff_id, first_name, last_name, email, username,
                password_hash, address_id, store_id, True, datetime.now()
            ))
            
            connection.commit()
            print(f"用户注册成功! 职员ID: {staff_id}")
            return True
            
    except Exception as e:
        print(f"注册用户时发生错误: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def get_user_input():
    """
    获取用户输入信息
    
    Returns:
        dict: 用户输入的信息
    """
    print("=" * 50)
    print("职员注册系统 (psycopg3)")
    print("=" * 50)
    
    try:
        first_name = input("请输入名字: ").strip()
        if not first_name:
            raise ValueError("名字不能为空")
        
        last_name = input("请输入姓氏: ").strip()
        if not last_name:
            raise ValueError("姓氏不能为空")
        
        username = input("请输入用户名: ").strip()
        if not username:
            raise ValueError("用户名不能为空")
        
        password = input("请输入密码: ").strip()
        if not password:
            raise ValueError("密码不能为空")
        
        email = input("请输入邮箱: ").strip()
        if not email:
            raise ValueError("邮箱不能为空")
        
        try:
            address_id = int(input("请输入地址ID: ").strip())
            if address_id <= 0:
                raise ValueError("地址ID必须大于0")
        except ValueError:
            raise ValueError("地址ID必须是有效的数字")
        
        try:
            store_id = int(input("请输入店铺ID: ").strip())
            if store_id <= 0:
                raise ValueError("店铺ID必须大于0")
        except ValueError:
            raise ValueError("店铺ID必须是有效的数字")
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password,
            'email': email,
            'address_id': address_id,
            'store_id': store_id
        }
        
    except KeyboardInterrupt:
        print("\n\n注册已取消")
        return None
    except ValueError as e:
        print(f"输入错误: {e}")
        return None


def main():
    """
    主函数
    """
    try:
        # 获取用户输入
        user_data = get_user_input()
        if not user_data:
            sys.exit(1)
        
        # 注册用户
        success = register_user(**user_data)
        
        if success:
            print("\n注册系统运行完成")
            sys.exit(0)
        else:
            print("\n注册系统运行失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
