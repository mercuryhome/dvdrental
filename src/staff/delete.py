#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户删除程序
从PostgreSQL数据库中删除staff表的指定用户
"""

import psycopg2
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


def check_user_exists(connection, username):
    """
    检查用户是否存在
    
    Args:
        connection: 数据库连接
        username (str): 用户名
    
    Returns:
        dict: 用户信息（如果存在）或None（如果不存在）
    """
    try:
        cursor = connection.cursor()
        
        # 查询用户信息
        cursor.execute("""
            SELECT staff_id, first_name, last_name, email, username, 
                   address_id, store_id, active, last_update
            FROM staff 
            WHERE username = %s
        """, (username,))
        
        result = cursor.fetchone()
        
        if result:
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
        print(f"检查用户时发生错误: {e}")
        return None


def delete_user(connection, username):
    """
    删除用户
    
    Args:
        connection: 数据库连接
        username (str): 用户名
    
    Returns:
        bool: 删除是否成功
    """
    try:
        cursor = connection.cursor()
        
        # 删除用户
        cursor.execute("DELETE FROM staff WHERE username = %s", (username,))
        
        # 检查是否有行被删除
        if cursor.rowcount == 0:
            print("错误: 用户不存在或删除失败")
            return False
        
        # 提交事务
        connection.commit()
        return True
        
    except psycopg2.Error as e:
        print(f"删除用户时发生错误: {e}")
        connection.rollback()
        return False


def get_user_input():
    """获取用户输入"""
    print("=== 用户删除系统 ===")
    print("⚠️  警告: 此操作将永久删除用户数据，无法恢复！")
    print("请输入要删除的用户信息:")
    
    try:
        username = input("用户名: ").strip()
        if not username:
            print("错误: 用户名不能为空")
            return None
        
        return {
            'username': username
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
    print("📋 用户信息:")
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
    """显示可用的用户"""
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


def confirm_deletion(username):
    """确认删除操作"""
    print(f"\n⚠️  您即将删除用户: {username}")
    print("此操作将永久删除用户的所有数据，包括:")
    print("- 用户基本信息")
    print("- 登录凭据")
    print("- 关联的地址和店铺信息")
    print("\n此操作无法撤销！")
    
    # 第一次确认
    confirm1 = input("\n确认要删除此用户吗? (输入 'DELETE' 确认): ").strip()
    if confirm1 != 'DELETE':
        print("删除操作已取消")
        return False
    
    # 第二次确认
    confirm2 = input("请再次确认删除操作 (输入 'YES' 确认): ").strip()
    if confirm2 != 'YES':
        print("删除操作已取消")
        return False
    
    return True


def main():
    """主函数"""
    print("PostgreSQL DVD租赁系统 - 用户删除")
    print("=" * 50)
    
    connection = None
    try:
        # 连接数据库
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库")
            return
        
        # 显示可用用户
        show_available_users(connection)
        
        # 获取用户输入
        user_data = get_user_input()
        if not user_data:
            return
        
        username = user_data['username']
        
        # 检查用户是否存在
        print(f"\n正在检查用户 '{username}'...")
        user_info = check_user_exists(connection, username)
        
        if not user_info:
            print(f"❌ 用户 '{username}' 不存在")
            print("请检查用户名是否正确")
            return
        
        # 显示用户信息
        display_user_info(user_info)
        
        # 确认删除操作
        if not confirm_deletion(username):
            return
        
        # 执行删除
        print(f"\n正在删除用户 '{username}'...")
        if delete_user(connection, username):
            print("✅ 用户删除成功!")
            print(f"用户 '{username}' 已从数据库中永久删除")
        else:
            print("❌ 用户删除失败!")
            
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
