# PostgreSQL 数据库连接测试程序

这是一个用于测试PostgreSQL数据库连接的Python程序。

## 连接参数

- 主机: localhost
- 端口: 5432
- 用户: postgres
- 数据库: dvdrental

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

```bash
python src/test_db_connection.py
```

## 输出说明

- 连接成功: 输出 "OK" 并显示数据库版本信息
- 连接失败: 输出具体错误信息

## 注意事项

1. 请确保PostgreSQL服务正在运行
2. 请确保数据库 `dvdrental` 已创建; 请 [./data/README.md](./data/README.md) 文件
3. 请根据实际情况修改密码（当前默认为 'postgres'）
4. 确保用户 'postgres' 有访问数据库的权限
