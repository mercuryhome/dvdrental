# DVD Rental 数据库导入指南

本目录包含 DVD 租赁店示例数据库文件，用于 PostgreSQL 数据库学习和测试。

## 文件说明

- `dvdrental.zip` - 压缩的数据库文件

## 导入步骤

### 1. 解压缩数据库文件

```bash
# 解压缩 zip 文件
unzip dvdrental.zip

# 解压缩 tar 文件
tar xvf dvdrental.tar
```

### 2. 创建数据库

```bash
# 创建名为 dvdrental 的数据库
createdb -h localhost -p 5432 -U postgres dvdrental
```

### 3. 恢复数据库

```bash
# 使用 pg_restore 恢复数据库
pg_restore -h localhost -p 5432 -U postgres -d dvdrental dvdrental.tar
```

### 4. 验证导入

```bash
# 连接到数据库验证导入是否成功
psql -h localhost -p 5432 -U postgres -d dvdrental

# 在 psql 中查看表列表
\dt

# 查看数据库版本
SELECT version();

# 退出 psql
\q
```

## 注意事项

1. **确保 PostgreSQL 服务正在运行**
2. **确保用户 postgres 有创建数据库的权限**
3. **如果数据库已存在，需要先删除：**
   ```bash
   dropdb -h localhost -p 5432 -U postgres dvdrental
   ```

## 数据库结构

dvdrental 数据库包含以下主要表：
- `actor` - 演员信息
- `film` - 电影信息
- `customer` - 客户信息
- `rental` - 租赁记录
- `payment` - 支付记录
- `inventory` - 库存信息
- `staff` - 员工信息
- `store` - 店铺信息

## 测试连接

导入完成后，可以使用项目根目录的测试程序验证连接：

```bash
# 从项目根目录运行
python src/test_db_connection.py
```

## 数据来源

- 官方教程：https://neon.com/postgresqltutorial/dvdrental.zip
