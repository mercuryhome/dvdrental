# PostgreSQL 数据库连接测试程序

这是一个用于测试PostgreSQL数据库连接的Python程序，支持两种不同的PostgreSQL适配器：psycopg2 和 psycopg3。

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

### psycopg2 版本 (传统同步适配器)
```bash
python src/test_db_connect_with_psycopg2.py
```

### psycopg3 版本 (新一代适配器，支持异步)
```bash
python src/test_db_connect_with_psycopg3.py
```

## psycopg2 与 psycopg3 使用差异

### 1. 导入方式
```python
# psycopg2
import psycopg2
from psycopg2 import OperationalError

# psycopg3
import psycopg
from psycopg import OperationalError
```

### 2. 连接参数
```python
# psycopg2
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'dvdrental',  # 使用 'database'
    'client_encoding': 'utf8'
}

# psycopg3
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'dbname': 'dvdrental',    # 使用 'dbname'
    'client_encoding': 'utf8'
}
```

### 3. 连接和游标管理
```python
# psycopg2 - 手动管理资源
connection = psycopg2.connect(**connection_params)
cursor = connection.cursor()
try:
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
finally:
    cursor.close()
    connection.close()

# psycopg3 - 使用上下文管理器自动管理
with psycopg.connect(**connection_params) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
```

### 4. 主要优势对比

| 特性 | psycopg2 | psycopg3 |
|------|----------|----------|
| **性能** | 成熟稳定 | 更快的连接池和查询 |
| **异步支持** | 无 | 原生支持异步操作 |
| **资源管理** | 手动管理 | 自动上下文管理 |
| **类型提示** | 基础支持 | 完整的类型提示 |
| **Unicode支持** | 良好 | 原生UTF-8支持 |
| **API设计** | 传统风格 | 现代化设计 |

## 输出说明

- 连接成功: 输出 "OK" 并显示数据库版本信息
- 连接失败: 输出具体错误信息

## 注意事项

1. 请确保PostgreSQL服务正在运行
2. 请确保数据库 `dvdrental` 已创建; 请 [./data/README.md](./data/README.md) 文件
3. 请根据实际情况修改密码（当前默认为 'postgres'）
4. 确保用户 'postgres' 有访问数据库的权限
