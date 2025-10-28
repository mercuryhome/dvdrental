#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职员信息修改程序 (使用 psycopg3)
允许用户输入职员ID，查看当前职员所有信息，并修改指定字段

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


def get_staff_by_id(connection, staff_id):
    """
    根据职员ID获取职员信息 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        staff_id (int): 职员ID
    
    Returns:
        dict: 职员信息（如果存在）或None（如果不存在）
    """
    try:
        with connection.cursor() as cursor:
            # 查询职员信息
            cursor.execute("""
                SELECT staff_id, first_name, last_name, email, username, 
                       address_id, store_id, active, last_update
                FROM staff 
                WHERE staff_id = %s
            """, (staff_id,))
            
            result = cursor.fetchone()
            
            if result:
                # 构建职员信息字典
                staff_info = {
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
                return staff_info
            else:
                return None
                
    except Exception as e:
        print(f"获取职员信息时发生错误: {e}")
        return None


def display_staff_info(staff_info):
    """
    显示职员信息
    
    Args:
        staff_info (dict): 职员信息
    """
    print("\n" + "=" * 50)
    print("职员信息详情")
    print("=" * 50)
    print(f"职员ID: {staff_info['staff_id']}")
    print(f"姓名: {staff_info['first_name']} {staff_info['last_name']}")
    print(f"邮箱: {staff_info['email']}")
    print(f"用户名: {staff_info['username']}")
    print(f"地址ID: {staff_info['address_id']}")
    print(f"店铺ID: {staff_info['store_id']}")
    print(f"状态: {'活跃' if staff_info['active'] else '非活跃'}")
    print(f"最后更新: {staff_info['last_update']}")
    print("=" * 50)


def get_field_choice():
    """
    获取要修改的字段选择
    
    Returns:
        str: 字段名
    """
    print("\n可修改的字段:")
    print("1. first_name - 名字")
    print("2. last_name - 姓氏")
    print("3. email - 邮箱")
    print("4. username - 用户名")
    print("5. address_id - 地址ID")
    print("6. store_id - 店铺ID")
    print("7. active - 状态")
    print("0. 退出")
    
    field_map = {
        '1': 'first_name',
        '2': 'last_name',
        '3': 'email',
        '4': 'username',
        '5': 'address_id',
        '6': 'store_id',
        '7': 'active',
        '0': None
    }
    
    while True:
        try:
            choice = input("\n请选择要修改的字段 (0-7): ").strip()
            if choice in field_map:
                return field_map[choice]
            else:
                print("无效选择，请输入 0-7 之间的数字")
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            return None


def get_new_value(field_name, current_value):
    """
    获取新值
    
    Args:
        field_name (str): 字段名
        current_value: 当前值
    
    Returns:
        新值
    """
    print(f"\n当前 {field_name} 值: {current_value}")
    
    try:
        if field_name in ['address_id', 'store_id']:
            # 整数字段
            while True:
                new_value = input(f"请输入新的 {field_name}: ").strip()
                if not new_value:
                    return current_value
                
                try:
                    new_value = int(new_value)
                    if new_value <= 0:
                        print("值必须大于0")
                        continue
                    return new_value
                except ValueError:
                    print("请输入有效的数字")
        
        elif field_name == 'active':
            # 布尔字段
            while True:
                new_value = input(f"请输入新的 {field_name} (true/false): ").strip().lower()
                if not new_value:
                    return current_value
                
                if new_value in ['true', 't', '1', 'yes', 'y']:
                    return True
                elif new_value in ['false', 'f', '0', 'no', 'n']:
                    return False
                else:
                    print("请输入 true 或 false")
        
        else:
            # 字符串字段
            new_value = input(f"请输入新的 {field_name}: ").strip()
            if not new_value:
                return current_value
            return new_value
            
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        return None


def update_staff_field(connection, staff_id, field_name, new_value):
    """
    更新职员字段 (使用 psycopg3)
    
    Args:
        connection: psycopg3 数据库连接
        staff_id (int): 职员ID
        field_name (str): 字段名
        new_value: 新值
    
    Returns:
        bool: 更新是否成功
    """
    try:
        with connection.cursor() as cursor:
            # 构建更新SQL
            sql = f"""
                UPDATE staff 
                SET {field_name} = %s, last_update = %s 
                WHERE staff_id = %s
            """
            
            cursor.execute(sql, (new_value, datetime.now(), staff_id))
            
            # 检查是否更新了记录
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                return False
                
    except Exception as e:
        print(f"更新字段时发生错误: {e}")
        connection.rollback()
        return False


def modify_staff_interactive():
    """
    交互式职员信息修改主函数 (使用 psycopg3)
    
    提供交互式界面，允许用户修改职员信息
    """
    print("=" * 50)
    print("职员信息修改系统 (psycopg3)")
    print("=" * 50)
    
    # 连接数据库
    connection = connect_to_database()
    if not connection:
        print("无法连接到数据库，修改操作失败")
        return False
    
    try:
        # 获取职员ID
        while True:
            try:
                staff_id = int(input("请输入要修改的职员ID: ").strip())
                if staff_id <= 0:
                    print("职员ID必须大于0")
                    continue
                break
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n操作已取消")
                return False
        
        # 获取职员信息
        staff_info = get_staff_by_id(connection, staff_id)
        
        if not staff_info:
            print(f"职员ID {staff_id} 不存在")
            return False
        
        # 显示当前信息
        display_staff_info(staff_info)
        
        # 修改循环
        while True:
            field_name = get_field_choice()
            
            if field_name is None:  # 用户选择退出
                print("修改操作结束")
                break
            
            # 获取新值
            new_value = get_new_value(field_name, staff_info[field_name])
            
            if new_value is None:  # 用户取消操作
                continue
            
            if new_value == staff_info[field_name]:
                print("新值与当前值相同，无需修改")
                continue
            
            # 确认修改
            confirm = input(f"确认将 {field_name} 从 '{staff_info[field_name]}' 修改为 '{new_value}'? (y/N): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                # 执行更新
                if update_staff_field(connection, staff_id, field_name, new_value):
                    print(f"{field_name} 修改成功")
                    staff_info[field_name] = new_value  # 更新本地信息
                else:
                    print(f"{field_name} 修改失败")
            else:
                print("修改已取消")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n修改操作已取消")
        return False
    except Exception as e:
        print(f"修改过程中发生错误: {e}")
        return False
    finally:
        # 关闭数据库连接
        connection.close()


def main():
    """
    主函数
    """
    try:
        success = modify_staff_interactive()
        
        if success:
            print("\n职员信息修改系统运行完成")
            sys.exit(0)
        else:
            print("\n职员信息修改系统运行失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
