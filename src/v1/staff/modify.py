#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职员信息修改程序 (使用 psycopg2)
允许用户输入职员ID，查看当前职员所有信息，并修改指定字段

本模块使用 psycopg2 进行数据库操作，这是传统的同步PostgreSQL适配器
psycopg2 是Python中最流行的PostgreSQL数据库适配器之一

依赖库:
    - psycopg2: PostgreSQL 数据库适配器 (传统同步版本)
    - sys: 系统相关功能
    - datetime: 日期时间处理

作者: Database Staff Management System
版本: 1.0
"""

import psycopg2
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
            host="127.0.0.1",
            port="5432",
            database="dvdrental",  # psycopg2 使用 'database'
            user="postgres",
            password="postgres"  # 请根据实际情况修改密码
        )
        return connection
    except psycopg2.Error as e:
        print(f"数据库连接失败: {e}")
        return None


def get_staff_by_id(connection, staff_id):
    """
    根据职员ID获取职员信息
    
    Args:
        connection: 数据库连接
        staff_id (int): 职员ID
    
    Returns:
        dict: 职员信息（如果存在）或None（如果不存在）
    """
    try:
        cursor = connection.cursor()
        
        # 查询职员信息
        cursor.execute("""
            SELECT staff_id, first_name, last_name, email, username, 
                   address_id, store_id, active, last_update
            FROM staff 
            WHERE staff_id = %s
        """, (staff_id,))
        
        result = cursor.fetchone()
        
        if result:
            # 返回职员信息
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
            
    except psycopg2.Error as e:
        print(f"查询职员信息时发生错误: {e}")
        return None


def display_staff_info(staff_info):
    """显示职员信息"""
    print("\n" + "=" * 60)
    print("📋 职员信息详情")
    print("=" * 60)
    print(f"职员ID: {staff_info['staff_id']}")
    print(f"姓名: {staff_info['first_name']} {staff_info['last_name']}")
    print(f"邮箱: {staff_info['email']}")
    print(f"用户名: {staff_info['username']}")
    print(f"地址ID: {staff_info['address_id']}")
    print(f"店铺ID: {staff_info['store_id']}")
    print(f"状态: {'活跃' if staff_info['active'] else '非活跃'}")
    print(f"最后更新: {staff_info['last_update']}")
    print("=" * 60)


def get_available_fields():
    """获取可修改的字段列表"""
    return {
        '1': {'name': 'first_name', 'display': '名字', 'type': 'str'},
        '2': {'name': 'last_name', 'display': '姓氏', 'type': 'str'},
        '3': {'name': 'email', 'display': '邮箱', 'type': 'str'},
        '4': {'name': 'address_id', 'display': '地址ID', 'type': 'int'},
        '5': {'name': 'store_id', 'display': '店铺ID', 'type': 'int'},
        '6': {'name': 'active', 'display': '状态', 'type': 'bool'}
    }


def display_available_fields():
    """显示可修改的字段"""
    fields = get_available_fields()
    print("\n可修改的字段:")
    print("-" * 30)
    for key, field in fields.items():
        print(f"{key}. {field['display']} ({field['name']})")


def validate_field_value(field_name, value, field_type):
    """验证字段值"""
    try:
        if field_type == 'int':
            return int(value)
        elif field_type == 'bool':
            if value.lower() in ['true', '1', 'yes', 'y', '活跃']:
                return True
            elif value.lower() in ['false', '0', 'no', 'n', '非活跃']:
                return False
            else:
                print("错误: 状态值无效，请输入 true/false 或 活跃/非活跃")
                return None
        else:  # str
            if not value.strip():
                print("错误: 字段值不能为空")
                return None
            return value.strip()
    except ValueError:
        print(f"错误: {field_name} 的值格式不正确")
        return None


def update_staff_field(connection, staff_id, field_name, new_value):
    """
    更新职员字段
    
    Args:
        connection: 数据库连接
        staff_id (int): 职员ID
        field_name (str): 字段名
        new_value: 新值
    
    Returns:
        bool: 更新是否成功
    """
    try:
        cursor = connection.cursor()
        
        # 构建更新SQL
        update_query = f"""
            UPDATE staff 
            SET {field_name} = %s, last_update = %s 
            WHERE staff_id = %s
        """
        
        cursor.execute(update_query, (new_value, datetime.now(), staff_id))
        
        # 检查是否有行被更新
        if cursor.rowcount == 0:
            print("错误: 更新失败，职员不存在")
            return False
        
        # 提交事务
        connection.commit()
        return True
        
    except psycopg2.Error as e:
        print(f"更新字段时发生错误: {e}")
        connection.rollback()
        return False


def validate_foreign_keys(connection, field_name, value):
    """验证外键约束"""
    try:
        cursor = connection.cursor()
        
        if field_name == 'address_id':
            cursor.execute("SELECT address_id FROM address WHERE address_id = %s", (value,))
            if not cursor.fetchone():
                print(f"错误: 地址ID {value} 不存在")
                return False
        elif field_name == 'store_id':
            cursor.execute("SELECT store_id FROM store WHERE store_id = %s", (value,))
            if not cursor.fetchone():
                print(f"错误: 店铺ID {value} 不存在")
                return False
        
        return True
        
    except psycopg2.Error as e:
        print(f"验证外键时发生错误: {e}")
        return False


def get_user_input():
    """获取用户输入"""
    print("=== 职员信息修改系统 ===")
    print("请输入职员ID:")
    
    try:
        staff_id = input("职员ID: ").strip()
        if not staff_id:
            print("错误: 职员ID不能为空")
            return None
        
        try:
            staff_id = int(staff_id)
        except ValueError:
            print("错误: 职员ID必须是数字")
            return None
        
        return staff_id
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return None
    except Exception as e:
        print(f"输入错误: {e}")
        return None


def get_field_modification():
    """获取字段修改信息"""
    fields = get_available_fields()
    
    # 显示可修改字段
    display_available_fields()
    
    try:
        # 选择字段
        field_choice = input("\n请选择要修改的字段 (输入数字): ").strip()
        if field_choice not in fields:
            print("错误: 无效的字段选择")
            return None
        
        field_info = fields[field_choice]
        field_name = field_info['name']
        field_display = field_info['display']
        field_type = field_info['type']
        
        # 获取新值
        if field_type == 'bool':
            print(f"\n请输入新的{field_display} (true/false 或 活跃/非活跃):")
        else:
            print(f"\n请输入新的{field_display}:")
        
        new_value = input("新值: ").strip()
        
        # 验证值
        validated_value = validate_field_value(field_name, new_value, field_type)
        if validated_value is None:
            return None
        
        return {
            'field_name': field_name,
            'field_display': field_display,
            'new_value': validated_value
        }
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return None
    except Exception as e:
        print(f"输入错误: {e}")
        return None


def show_available_addresses(connection):
    """显示可用的地址ID"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT address_id, address, district FROM address ORDER BY address_id LIMIT 10")
        addresses = cursor.fetchall()
        
        print("\n可用的地址ID (前10个):")
        print("ID\t地址\t\t\t\t地区")
        print("-" * 60)
        for addr in addresses:
            print(f"{addr[0]}\t{addr[1][:30]}\t{addr[2]}")
            
    except psycopg2.Error as e:
        print(f"获取地址信息失败: {e}")


def show_available_stores(connection):
    """显示可用的店铺ID"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT store_id, manager_staff_id FROM store ORDER BY store_id")
        stores = cursor.fetchall()
        
        print("\n可用的店铺ID:")
        print("店铺ID\t管理员员工ID")
        print("-" * 20)
        for store in stores:
            print(f"{store[0]}\t{store[1]}")
            
    except psycopg2.Error as e:
        print(f"获取店铺信息失败: {e}")


def main():
    """主函数"""
    print("PostgreSQL DVD租赁系统 - 职员信息修改")
    print("=" * 50)
    
    connection = None
    try:
        # 连接数据库
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库")
            return
        
        # 获取职员ID
        staff_id = get_user_input()
        if not staff_id:
            return
        
        # 查询职员信息
        print(f"\n正在查询职员ID {staff_id} 的信息...")
        staff_info = get_staff_by_id(connection, staff_id)
        
        if not staff_info:
            print(f"❌ 错误: 职员ID {staff_id} 不存在")
            return
        
        # 显示职员信息
        display_staff_info(staff_info)
        
        # 获取修改信息
        modification = get_field_modification()
        if not modification:
            return
        
        # 验证外键约束
        if modification['field_name'] in ['address_id', 'store_id']:
            if not validate_foreign_keys(connection, modification['field_name'], modification['new_value']):
                return
        
        # 显示修改预览
        print(f"\n修改预览:")
        print(f"字段: {modification['field_display']}")
        print(f"原值: {staff_info[modification['field_name']]}")
        print(f"新值: {modification['new_value']}")
        
        # 确认修改
        print(f"\n确认修改职员ID {staff_id} 的 {modification['field_display']}?")
        confirm = input("确定保存? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # 执行更新
            print("正在保存修改...")
            if update_staff_field(connection, staff_id, modification['field_name'], modification['new_value']):
                print("✅ 修改成功!")
                
                # 显示更新后的信息
                print("\n更新后的职员信息:")
                updated_info = get_staff_by_id(connection, staff_id)
                if updated_info:
                    display_staff_info(updated_info)
            else:
                print("❌ 修改失败!")
        else:
            print("修改已取消")
            
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
