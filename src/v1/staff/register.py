#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户注册程序 (使用 psycopg2)
将用户信息保存到PostgreSQL数据库的staff表中

本模块使用 psycopg2 进行数据库操作，这是传统的同步PostgreSQL适配器
psycopg2 是Python中最流行的PostgreSQL数据库适配器之一

依赖库:
    - psycopg2: PostgreSQL 数据库适配器 (传统同步版本)
    - hashlib: 密码加密
    - sys: 系统相关功能
    - datetime: 日期时间处理

作者: Database Staff Management System
版本: 1.0
"""

import psycopg2
import hashlib
import sys
from datetime import datetime


def connect_to_database():
    """
    连接到PostgreSQL数据库 (使用 psycopg2)
    
    使用 psycopg2.connect() 建立数据库连接
    注意：psycopg2 使用 'database' 参数名
    
    Returns:
        psycopg2.extensions.connection: 数据库连接对象，失败时返回None
    """
    try:
        # psycopg2 数据库连接参数
        # 注意：psycopg2 使用 'database' 参数名（而不是 'dbname'）
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="dvdrental",  # psycopg2 使用 'database'
            user="postgres",
            password="postgres"  # 请根据实际情况修改密码
        )
        return connection
    except psycopg2.Error as e:
        print(f"数据库连接失败: {e}")
        return None


def register_user(first_name, last_name, username, password, address_id, store_id):
    """
    注册新用户到staff表
    
    Args:
        first_name (str): 名字
        last_name (str): 姓氏
        username (str): 用户名
        password (str): 密码
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
        
        cursor = connection.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT staff_id FROM staff WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"错误: 用户名 '{username}' 已存在")
            return False
        
        # 检查地址ID是否存在
        cursor.execute("SELECT address_id FROM address WHERE address_id = %s", (address_id,))
        if not cursor.fetchone():
            print(f"错误: 地址ID {address_id} 不存在")
            return False
        
        # 检查店铺ID是否存在
        cursor.execute("SELECT store_id FROM store WHERE store_id = %s", (store_id,))
        if not cursor.fetchone():
            print(f"错误: 店铺ID {store_id} 不存在")
            return False
        
        # 使用MD5加密密码
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # 插入新用户
        insert_query = """
        INSERT INTO public.staff(
            first_name, 
            last_name, 
            email, 
            username, 
            password, 
            address_id, 
            store_id,
            active,
            last_update
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        cursor.execute(insert_query, (
            first_name,
            last_name,
            f"{username}@example.com",  # 默认邮箱
            username,
            password_hash,
            address_id,
            store_id,
            True,  # active默认为True
            datetime.now()
        ))
        
        # 提交事务
        connection.commit()
        
        # 获取新插入的用户ID
        cursor.execute("SELECT staff_id FROM staff WHERE username = %s", (username,))
        staff_id = cursor.fetchone()[0]
        
        print(f"用户注册成功! 用户ID: {staff_id}")
        print(f"姓名: {first_name} {last_name}")
        print(f"用户名: {username}")
        print(f"地址ID: {address_id}")
        print(f"店铺ID: {store_id}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"数据库操作失败: {e}")
        if connection:
            connection.rollback()
        return False
    except Exception as e:
        print(f"程序错误: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def get_user_input():
    """获取用户输入"""
    print("=== 用户注册系统 ===")
    print("请输入以下信息:")
    
    try:
        first_name = input("名字: ").strip()
        if not first_name:
            print("错误: 名字不能为空")
            return None
        
        last_name = input("姓氏: ").strip()
        if not last_name:
            print("错误: 姓氏不能为空")
            return None
        
        username = input("用户名: ").strip()
        if not username:
            print("错误: 用户名不能为空")
            return None
        
        password = input("密码: ").strip()
        if not password:
            print("错误: 密码不能为空")
            return None
        
        try:
            address_id = int(input("地址ID: ").strip())
        except ValueError:
            print("错误: 地址ID必须是数字")
            return None
        
        try:
            store_id = int(input("店铺ID: ").strip())
        except ValueError:
            print("错误: 店铺ID必须是数字")
            return None
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password,
            'address_id': address_id,
            'store_id': store_id
        }
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return None
    except Exception as e:
        print(f"输入错误: {e}")
        return None


def show_available_addresses():
    """显示可用的地址ID"""
    connection = None
    try:
        connection = connect_to_database()
        if not connection:
            return
        
        cursor = connection.cursor()
        cursor.execute("SELECT address_id, address, district FROM address ORDER BY address_id LIMIT 10")
        addresses = cursor.fetchall()
        
        print("\n可用的地址ID (前10个):")
        print("ID\t地址\t\t\t\t地区")
        print("-" * 60)
        for addr in addresses:
            print(f"{addr[0]}\t{addr[1][:30]}\t{addr[2]}")
            
    except Exception as e:
        print(f"获取地址信息失败: {e}")
    finally:
        if connection:
            connection.close()


def show_available_stores():
    """显示可用的店铺ID"""
    connection = None
    try:
        connection = connect_to_database()
        if not connection:
            return
        
        cursor = connection.cursor()
        cursor.execute("SELECT store_id, manager_staff_id FROM store ORDER BY store_id")
        stores = cursor.fetchall()
        
        print("\n可用的店铺ID:")
        print("店铺ID\t管理员员工ID")
        print("-" * 20)
        for store in stores:
            print(f"{store[0]}\t{store[1]}")
            
    except Exception as e:
        print(f"获取店铺信息失败: {e}")
    finally:
        if connection:
            connection.close()


def main():
    """主函数"""
    print("PostgreSQL DVD租赁系统 - 用户注册")
    print("=" * 50)
    
    # 显示可用的地址和店铺信息
    show_available_addresses()
    show_available_stores()
    
    # 获取用户输入
    user_data = get_user_input()
    if not user_data:
        return
    
    # 确认信息
    print(f"\n请确认以下信息:")
    print(f"名字: {user_data['first_name']}")
    print(f"姓氏: {user_data['last_name']}")
    print(f"用户名: {user_data['username']}")
    print(f"地址ID: {user_data['address_id']}")
    print(f"店铺ID: {user_data['store_id']}")
    
    confirm = input("\n确认注册? (y/n): ").strip().lower()
    if confirm != 'y':
        print("注册已取消")
        return
    
    # 执行注册
    if register_user(**user_data):
        print("\n注册完成!")
    else:
        print("\n注册失败!")


if __name__ == "__main__":
    main()
