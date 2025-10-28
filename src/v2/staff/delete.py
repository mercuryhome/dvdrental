#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户删除程序 (使用 psycopg3)
从PostgreSQL数据库中删除staff表的指定用户

本模块使用 psycopg3 进行数据库操作，提供更好的性能和现代化的API设计
"""

import psycopg
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


def check_user_exists(connection, username):
    """
    检查用户是否存在 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        username (str): 用户名
    
    Returns:
        dict: 用户信息（如果存在）或None（如果不存在）
    """
    try:
        with connection.cursor() as cursor:
            # 查询用户信息
            cursor.execute("""
                SELECT staff_id, first_name, last_name, email, username, 
                       address_id, store_id, active, last_update
                FROM staff 
                WHERE username = %s
            """, (username,))
            
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
        print(f"检查用户时发生错误: {e}")
        return None


def delete_user(connection, username):
    """
    删除指定用户 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        username (str): 用户名
    
    Returns:
        bool: 删除是否成功
    """
    try:
        with connection.cursor() as cursor:
            # 删除用户
            cursor.execute("""
                DELETE FROM staff WHERE username = %s
            """, (username,))
            
            # 检查是否删除了记录
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                return False
                
    except Exception as e:
        print(f"删除用户时发生错误: {e}")
        connection.rollback()
        return False


def confirm_deletion(user_info):
    """
    确认删除操作
    
    Args:
        user_info (dict): 用户信息
    
    Returns:
        bool: 用户是否确认删除
    """
    print("\n找到以下用户信息:")
    print(f"职员ID: {user_info['staff_id']}")
    print(f"姓名: {user_info['first_name']} {user_info['last_name']}")
    print(f"用户名: {user_info['username']}")
    print(f"邮箱: {user_info['email']}")
    print(f"店铺ID: {user_info['store_id']}")
    print(f"状态: {'活跃' if user_info['active'] else '非活跃'}")
    print(f"最后更新: {user_info['last_update']}")
    
    while True:
        confirm = input("\n确认删除此用户? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            return True
        elif confirm in ['n', 'no', '']:
            return False
        else:
            print("请输入 'y' 或 'n'")


def delete_user_interactive():
    """
    交互式删除用户主函数 (使用 psycopg3)
    
    提供交互式界面，允许用户输入要删除的用户名并确认删除操作
    """
    print("=" * 50)
    print("职员删除系统 (psycopg3)")
    print("=" * 50)
    
    # 连接数据库
    connection = connect_to_database()
    if not connection:
        print("无法连接到数据库，删除操作失败")
        return False
    
    try:
        # 获取要删除的用户名
        username = input("请输入要删除的用户名: ").strip()
        
        if not username:
            print("用户名不能为空")
            return False
        
        # 检查用户是否存在
        user_info = check_user_exists(connection, username)
        
        if not user_info:
            print(f"用户 '{username}' 不存在")
            return False
        
        # 确认删除
        if not confirm_deletion(user_info):
            print("删除操作已取消")
            return False
        
        # 执行删除
        if delete_user(connection, username):
            print(f"用户 '{username}' 删除成功")
            return True
        else:
            print(f"删除用户 '{username}' 失败")
            return False
            
    except KeyboardInterrupt:
        print("\n\n删除操作已取消")
        return False
    except Exception as e:
        print(f"删除过程中发生错误: {e}")
        return False
    finally:
        # 关闭数据库连接
        connection.close()


def main():
    """
    主函数
    """
    try:
        success = delete_user_interactive()
        
        if success:
            print("\n删除系统运行完成")
            sys.exit(0)
        else:
            print("\n删除系统运行失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
