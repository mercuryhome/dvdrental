#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户密码修改程序 (使用 psycopg2)
修改PostgreSQL数据库中staff表的用户密码

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


def verify_old_password(connection, username, old_password):
    """
    验证旧密码是否正确
    
    Args:
        connection: 数据库连接
        username (str): 用户名
        old_password (str): 旧密码
    
    Returns:
        bool: 密码是否正确
    """
    try:
        cursor = connection.cursor()
        
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
        
    except psycopg2.Error as e:
        print(f"验证密码时发生错误: {e}")
        return False


def update_password(connection, username, new_password):
    """
    更新用户密码
    
    Args:
        connection: 数据库连接
        username (str): 用户名
        new_password (str): 新密码
    
    Returns:
        bool: 更新是否成功
    """
    try:
        cursor = connection.cursor()
        
        # 使用MD5加密新密码
        new_password_hash = hashlib.md5(new_password.encode()).hexdigest()
        
        # 更新密码
        cursor.execute("""
            UPDATE staff 
            SET password = %s, last_update = %s 
            WHERE username = %s
        """, (new_password_hash, datetime.now(), username))
        
        # 检查是否有行被更新
        if cursor.rowcount == 0:
            print("错误: 用户不存在或更新失败")
            return False
        
        # 提交事务
        connection.commit()
        return True
        
    except psycopg2.Error as e:
        print(f"更新密码时发生错误: {e}")
        connection.rollback()
        return False


def get_user_input():
    """获取用户输入"""
    print("=== 密码修改系统 ===")
    print("请输入以下信息:")
    
    try:
        username = input("用户名: ").strip()
        if not username:
            print("错误: 用户名不能为空")
            return None
        
        old_password = input("旧密码: ").strip()
        if not old_password:
            print("错误: 旧密码不能为空")
            return None
        
        new_password = input("新密码: ").strip()
        if not new_password:
            print("错误: 新密码不能为空")
            return None
        
        # 检查新密码是否与旧密码相同
        if old_password == new_password:
            print("错误: 新密码不能与旧密码相同")
            return None
        
        # 检查新密码长度
        if len(new_password) < 6:
            print("错误: 新密码长度至少为6位")
            return None
        
        # 确认新密码
        confirm_password = input("确认新密码: ").strip()
        if new_password != confirm_password:
            print("错误: 两次输入的新密码不一致")
            return None
        
        return {
            'username': username,
            'old_password': old_password,
            'new_password': new_password
        }
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return None
    except Exception as e:
        print(f"输入错误: {e}")
        return None


def show_user_info(connection, username):
    """显示用户信息"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT staff_id, first_name, last_name, email, active
            FROM staff 
            WHERE username = %s
        """, (username,))
        
        result = cursor.fetchone()
        if result:
            staff_id, first_name, last_name, email, active = result
            print(f"\n用户信息:")
            print(f"员工ID: {staff_id}")
            print(f"姓名: {first_name} {last_name}")
            print(f"邮箱: {email}")
            print(f"状态: {'活跃' if active else '非活跃'}")
            return True
        else:
            print("错误: 用户不存在")
            return False
            
    except psycopg2.Error as e:
        print(f"获取用户信息失败: {e}")
        return False


def main():
    """主函数"""
    print("PostgreSQL DVD租赁系统 - 密码修改")
    print("=" * 50)
    
    # 获取用户输入
    user_data = get_user_input()
    if not user_data:
        return
    
    connection = None
    try:
        # 连接数据库
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库")
            return
        
        # 显示用户信息
        if not show_user_info(connection, user_data['username']):
            return
        
        # 验证旧密码
        print(f"\n正在验证旧密码...")
        if not verify_old_password(connection, user_data['username'], user_data['old_password']):
            print("错误: 用户名或旧密码不正确")
            return
        
        print("✅ 旧密码验证成功")
        
        # 确认修改
        print(f"\n即将修改用户 '{user_data['username']}' 的密码")
        confirm = input("确认修改密码? (y/n): ").strip().lower()
        if confirm != 'y':
            print("密码修改已取消")
            return
        
        # 更新密码
        print("正在更新密码...")
        if update_password(connection, user_data['username'], user_data['new_password']):
            print("✅ 密码修改成功!")
            print(f"用户 '{user_data['username']}' 的密码已更新")
        else:
            print("❌ 密码修改失败!")
            
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
