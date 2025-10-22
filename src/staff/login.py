#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户登录程序
验证PostgreSQL数据库中staff表的用户凭据
"""

import psycopg2
import hashlib
import sys
from datetime import datetime


def connect_to_database():
    """连接到PostgreSQL数据库"""
    try:
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="dvdrental",
            user="postgres",
            password="postgres"  # 请根据实际情况修改密码
        )
        return connection
    except psycopg2.Error as e:
        print(f"数据库连接失败: {e}")
        return None


def authenticate_user(connection, username, password):
    """
    验证用户凭据
    
    Args:
        connection: 数据库连接
        username (str): 用户名
        password (str): 密码
    
    Returns:
        dict: 用户信息（如果验证成功）或None（如果验证失败）
    """
    try:
        cursor = connection.cursor()
        
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
            # 检查用户是否活跃
            active = result[7]  # active字段
            if not active:
                print("❌ 登录失败: 用户账户已被禁用")
                return None
            
            # 返回用户信息
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
            
    except psycopg2.Error as e:
        print(f"验证用户时发生错误: {e}")
        return None


def get_user_input():
    """获取用户输入"""
    print("=== 用户登录系统 ===")
    print("请输入登录信息:")
    
    try:
        username = input("用户名: ").strip()
        if not username:
            print("错误: 用户名不能为空")
            return None
        
        password = input("密码: ").strip()
        if not password:
            print("错误: 密码不能为空")
            return None
        
        return {
            'username': username,
            'password': password
        }
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return None
    except Exception as e:
        print(f"输入错误: {e}")
        return None


def display_user_info(user_info):
    """显示用户信息"""
    print("\n" + "=" * 50)
    print("🎉 登录成功！")
    print("=" * 50)
    print(f"员工ID: {user_info['staff_id']}")
    print(f"姓名: {user_info['first_name']} {user_info['last_name']}")
    print(f"用户名: {user_info['username']}")
    print(f"邮箱: {user_info['email']}")
    print(f"地址ID: {user_info['address_id']}")
    print(f"店铺ID: {user_info['store_id']}")
    print(f"状态: {'活跃' if user_info['active'] else '非活跃'}")
    print(f"最后更新: {user_info['last_update']}")
    print("=" * 50)


def show_available_users(connection):
    """显示可用的用户（用于测试）"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT username, first_name, last_name, active
            FROM staff 
            ORDER BY staff_id
        """)
        
        users = cursor.fetchall()
        
        print("\n📋 数据库中的用户:")
        print("用户名\t\t姓名\t\t\t状态")
        print("-" * 50)
        for user in users:
            username, first_name, last_name, active = user
            status = "活跃" if active else "禁用"
            print(f"{username:<15}\t{first_name} {last_name:<15}\t{status}")
            
    except psycopg2.Error as e:
        print(f"获取用户列表失败: {e}")


def main():
    """主函数"""
    print("PostgreSQL DVD租赁系统 - 用户登录")
    print("=" * 50)
    
    connection = None
    try:
        # 连接数据库
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库")
            return
        
        # 显示可用用户（用于测试）
        show_available_users(connection)
        
        # 获取用户输入
        user_data = get_user_input()
        if not user_data:
            return
        
        # 验证用户凭据
        print(f"\n正在验证用户凭据...")
        user_info = authenticate_user(connection, user_data['username'], user_data['password'])
        
        if user_info:
            # 登录成功
            display_user_info(user_info)
            
            # 可选：记录登录时间
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE staff 
                    SET last_update = %s 
                    WHERE staff_id = %s
                """, (datetime.now(), user_info['staff_id']))
                connection.commit()
                print("\n✅ 登录时间已更新")
            except psycopg2.Error as e:
                print(f"更新登录时间失败: {e}")
        else:
            # 登录失败
            print("\n❌ 登录失败！")
            print("可能的原因:")
            print("1. 用户名不存在")
            print("2. 密码不正确")
            print("3. 用户账户已被禁用")
            print("\n请检查用户名和密码，然后重试。")
            
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
