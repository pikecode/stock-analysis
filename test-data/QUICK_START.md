# 快速开始（5分钟）

## ⚡ 最快路径

### 1. 确保后端运行

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. 确保前端运行

```bash
cd frontend
npm run dev
```

### 3. 导入 CSV 文件

1. 打开 http://127.0.0.1:5173/admin/import
2. 选择文件类型：**CSV**
3. 选择文件：`test-data/test_import_stocks_concepts.csv`
4. 点击"开始导入"
5. 等待完成 ✅

### 4. 导入一个 EEE 文件（快速测试）

1. 选择文件类型：**TXT**
2. 选择指标：**EEE**
3. 选择文件：`test-data/EEE_2025-11-03.txt`
4. 点击"开始导入"
5. 等待排名计算完成 ✅

### 5. 查看结果

进入"导入记录"页面查看导入历史和状态。

---

## 📊 数据量速览

| 项目 | 数量 |
|------|------|
| 股票 | 50 |
| 概念 | 21 |
| 映射 | 209 |
| EEE 文件 | 20 |
| TTV 文件 | 20 |
| 总 TXT 行数 | 2000 |

---

## ✅ 验证（2分钟）

导入 CSV 后运行一条 SQL：

```sql
SELECT COUNT(*) FROM stock_concepts;
-- 应返回：209
```

导入 1 个 EEE 文件后：

```sql
SELECT COUNT(*) FROM concept_stock_daily_rank
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE');
-- 应返回：100+ (具体数值取决于关联的概念数)
```

---

## 🚀 完整流程（30分钟）

想要完整测试所有功能？

1. **导入 CSV**（1分钟）
2. **逐日导入所有 EEE 文件**（20个文件，约5分钟）
3. **逐日导入所有 TTV 文件**（20个文件，约5分钟）
4. **验证数据**（SQL查询，5分钟）
5. **API 测试**（10分钟）

---

**更多信息见**: `README.md`
