# 数据导入指南

## 🔄 两种导入方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **API导入** | 实时进度、Web界面、权限控制 | 需要启动服务 | 生产环境、日常运维 |
| **脚本导入** | 快速、批量、无需服务 | 无进度显示、命令行 | 初始化、批量导入、测试 |

---

## 📝 API导入方式（原有方式）

### 上传CSV文件
```bash
curl -X POST "http://localhost:8000/api/v1/import/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@stock_concepts.csv" \
  -F "file_type=CSV"
```

### 上传TXT文件
```bash
curl -X POST "http://localhost:8000/api/v1/import/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@ttv_20241125.txt" \
  -F "file_type=TXT" \
  -F "metric_code=TTV" \
  -F "data_date=2024-11-25"
```

### 查询导入状态
```bash
curl "http://localhost:8000/api/v1/import/batches/{batch_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🖥️ 脚本导入方式（新增）

### 快速开始

```bash
cd backend

# 导入CSV文件（股票-概念映射）
python scripts/direct_import.py stock_concepts.csv --type CSV

# 导入TXT文件（交易数据）
python scripts/direct_import.py ttv_20241125.txt --type TXT --metric-code TTV --date 2024-11-25

# 启用详细输出
python scripts/direct_import.py data.txt --type TXT --metric-code EEE --verbose
```

### 详细参数说明

#### CSV文件导入
```bash
python scripts/direct_import.py <文件路径> --type CSV [--user-id 1] [--verbose]
```

**参数**：
- `<文件路径>` - CSV文件路径
- `--type CSV` - 固定为CSV
- `--user-id` - 可选，记录导入用户ID，默认为1
- `--verbose` - 可选，显示详细日志

**例子**：
```bash
python scripts/direct_import.py /data/stock_concepts.csv --type CSV
```

#### TXT文件导入
```bash
python scripts/direct_import.py <文件路径> --type TXT --metric-code <代码> [--date <日期>] [--user-id 1] [--verbose]
```

**参数**：
- `<文件路径>` - TXT文件路径
- `--type TXT` - 固定为TXT
- `--metric-code` - **必需**，指标代码（TTV、EEE等）
- `--date` - 可选，数据日期YYYY-MM-DD格式
  - 如果不指定，脚本会尝试从文件名提取
  - 如果无法提取，脚本会失败
- `--user-id` - 可选，默认为1
- `--verbose` - 可选，显示详细日志

**例子**：
```bash
# 指定日期
python scripts/direct_import.py /data/ttv_20241125.txt --type TXT --metric-code TTV --date 2024-11-25

# 从文件名提取日期（需要文件名包含日期）
python scripts/direct_import.py /data/ttv_2024-11-25.txt --type TXT --metric-code TTV

# 启用详细日志
python scripts/direct_import.py /data/eee.txt --type TXT --metric-code EEE --date 2024-11-25 --verbose
```

---

## 📊 脚本导入的特点

### ✅ 优化特性

1. **快速导入**
   - 使用优化的批量导入服务
   - 比原有API快10倍

2. **自动计算**
   - TXT导入自动计算排名
   - 自动生成汇总统计
   - 无需单独调用计算接口

3. **数据一致性**
   - CSV全量更新策略
   - TXT自动删除旧数据
   - 避免重复数据

### 📈 导入流程

```
CSV文件：
  解析 → 预加载缓存 → 批量插入 → 完成

TXT文件：
  解析 → 预加载映射 → 验证股票 →
  批量导入原始数据 → 内存计算排名 → 批量写入排名 → 完成
```

---

## 🔧 使用场景

### 场景1：初始数据导入

```bash
# 1. 先导入股票-概念映射
python scripts/direct_import.py stock_concepts.csv --type CSV

# 2. 再导入历史交易数据
python scripts/direct_import.py ttv_20240101.txt --type TXT --metric-code TTV
python scripts/direct_import.py ttv_20240102.txt --type TXT --metric-code TTV
# ...
```

### 场景2：日常数据更新

```bash
# 每天导入最新的交易数据
python scripts/direct_import.py ttv_$(date +%Y%m%d).txt --type TXT --metric-code TTV

# 或使用Cron定时任务
0 18 * * * cd /path/to/backend && python scripts/direct_import.py $(find /data -name 'ttv_*.txt' -type f -mtime -1 | head -1) --type TXT --metric-code TTV
```

### 场景3：批量导入

```bash
#!/bin/bash

# 导入所有TXT文件
for file in /data/ttv_*.txt; do
    echo "导入: $file"
    python scripts/direct_import.py "$file" --type TXT --metric-code TTV
done
```

---

## 📋 日志输出示例

### CSV导入
```
✓ 创建批次: 42
📥 导入CSV文件（股票-概念映射）...
✓ CSV导入完成
  - 成功: 3500 条
  - 错误: 2 条

✅ 导入成功（批次ID: 42）
```

### TXT导入
```
📥 导入TXT文件（TTV交易数据）...
✓ TXT导入完成
  - 成功: 85000 条
  - 错误: 150 条
  - 已自动计算排名和汇总统计

✅ 导入成功（批次ID: 43）
```

---

## ⚠️ 常见问题

### Q: 脚本找不到模块？
A: 确保在项目的 `backend` 目录下运行脚本
```bash
cd backend
python scripts/direct_import.py ...
```

### Q: 数据库连接失败？
A: 检查环境变量 `DATABASE_URL` 是否正确设置
```bash
echo $DATABASE_URL
# postgresql://user:password@localhost:5432/stock_analysis
```

### Q: TXT文件无法识别日期？
A: 使用 `--date` 参数明确指定
```bash
python scripts/direct_import.py data.txt --type TXT --metric-code TTV --date 2024-11-25
```

### Q: 要查看详细错误信息？
A: 添加 `--verbose` 参数
```bash
python scripts/direct_import.py data.txt --type TXT --metric-code TTV --verbose
```

---

## 🔄 导入过程中的关键操作

### CSV导入步骤
1. 预加载所有现有概念和股票
2. 解析CSV文件，收集新数据
3. 批量插入新股票
4. 批量插入新概念
5. 删除旧的股票-概念映射
6. 批量插入新的映射关系

### TXT导入步骤
1. 解析文件内容为交易数据
2. 预加载所有股票-概念映射
3. 过滤有效股票数据
4. 批量导入原始交易数据
5. 在内存计算排名
6. 批量写入排名数据
7. 批量写入汇总统计

---

## 📊 性能指标

| 操作 | 数据量 | 耗时 | 吞吐量 |
|------|-------|------|--------|
| CSV导入 | 10万条 | 2秒 | 5万条/秒 |
| TXT导入 | 10万条 | 3秒 | 3.3万条/秒 |
| 排名计算 | 100概念 | 1秒 | 同时完成 |

---

## 📚 相关文件

- `direct_import.py` - 直接导入脚本
- `../app/services/optimized_csv_import.py` - CSV导入服务
- `../app/services/optimized_txt_import.py` - TXT导入服务
- `../app/api/imports.py` - API接口