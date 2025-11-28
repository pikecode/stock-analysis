# 测试数据使用指南

**生成时间**: 2025-11-28
**数据规模**: 中等规模（适合完整功能测试）
**生成脚本**: `generate_test_data.py`

---

## 📊 数据概览

### CSV 文件（股票-概念映射）

**文件**: `test_import_stocks_concepts.csv`

**数据规模**:
- 股票数：50个
- 概念数：21个
- 映射关系：209行（平均每股4个概念）

**包含的股票**:
- 上海交易所（SH）：20个股票
  - 600000 浦发银行
  - 600004 白云机场
  - 600006 东方集团
  - ... 等17个
- 深圳交易所（SZ）：30个股票
  - 000001 平安银行
  - 000002 万科A
  - 000004 国农科技
  - ... 等27个

**包含的概念**（21个）:
```
银行、房地产、汽车、电力、航运、保险、钢铁、化工、机械、电子、医药、
食品饮料、纺织服装、采矿、建筑、深圳板块、上海板块、沿海概念、国企改革、
绿色能源、新基建
```

### TXT 文件（日期特定的指标数据）

**EEE 指标**（行业活跃度）
- 文件数：20个
- 日期范围：2025-11-03 ~ 2025-11-28（20个交易日）
- 每日数据：50个股票 × 1个指标值 = 50行/文件
- 总数据量：1000行
- 指标值范围：100,000 ~ 5,000,000

**TTV 指标**（交易交易量）
- 文件数：20个
- 日期范围：2025-11-03 ~ 2025-11-28（20个交易日）
- 每日数据：50个股票 × 1个指标值 = 50行/文件
- 总数据量：1000行
- 指标值范围：1,000,000 ~ 100,000,000

---

## 📋 导入步骤

### 步骤1：准备工作

1. **启动后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **启动前端开发服务**
   ```bash
   cd frontend
   npm run dev
   ```

3. **确保数据库已初始化**
   - 表结构已创建
   - `metric_types` 表已包含 EEE 和 TTV 类型

### 步骤2：导入 CSV 文件（股票-概念关系）

#### 方式A：通过Web UI导入

1. 打开浏览器：http://127.0.0.1:5173/admin/import
2. 选择文件类型：**CSV (股票-概念关系)**
3. 点击"拖拽或点击选择文件"，选择：`test-data/test_import_stocks_concepts.csv`
4. 点击"开始导入"按钮
5. 观察进度条和状态提示
6. 导入完成后应显示：
   ```
   导入成功
   成功: 209 / 失败: 0 / 总计: 209
   ```

#### 验证 CSV 导入

导入完成后，检查数据库：

```sql
-- 检查股票数
SELECT COUNT(*) FROM stocks;
-- 预期结果：50

-- 检查概念数
SELECT COUNT(*) FROM concepts;
-- 预期结果：21

-- 检查映射关系数
SELECT COUNT(*) FROM stock_concepts;
-- 预期结果：209

-- 查看某股票的概念
SELECT c.concept_name
FROM stock_concepts sc
JOIN concepts c ON sc.concept_id = c.id
WHERE sc.stock_code = '600000'
ORDER BY c.concept_name;
```

### 步骤3：导入 TXT 文件（指标数据）

#### 导入 EEE 指标

1. 打开浏览器：http://127.0.0.1:5173/admin/import
2. 选择文件类型：**TXT (指标数据)**
3. 选择指标类型：**EEE** (行业活跃度)
4. 选择第一个文件：`test-data/EEE_2025-11-03.txt`
5. 点击"开始导入"
6. 等待完成（包括排名计算）：
   ```
   导入成功
   成功: 50 / 失败: 0 / 总计: 50
   排名计算: 已完成
   ```

7. **重复上述步骤**，逐日导入其余19个 EEE 文件（2025-11-04 ~ 2025-11-28）

#### 导入 TTV 指标

1. 打开浏览器：http://127.0.0.1:5173/admin/import
2. 选择文件类型：**TXT (指标数据)**
3. 选择指标类型：**TTV** (交易交易量)
4. 选择第一个文件：`test-data/TTV_2025-11-03.txt`
5. 点击"开始导入"
6. 等待完成

7. **重复上述步骤**，逐日导入其余19个 TTV 文件

#### 快速导入（批量脚本）

如果手工逐文件导入过于繁琐，可以编写导入脚本（见 §4）。

### 步骤4：验证导入结果

#### 检查原始数据

```sql
-- 检查 EEE 指标的原始数据
SELECT COUNT(*) FROM stock_metric_data_raw
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE');
-- 预期结果：1000 (50 股票 × 20 日期)

-- 检查 TTV 指标的原始数据
SELECT COUNT(*) FROM stock_metric_data_raw
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'TTV');
-- 预期结果：1000 (50 股票 × 20 日期)

-- 查看某日期的 EEE 数据
SELECT stock_code, trade_value, trade_date
FROM stock_metric_data_raw
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE')
  AND trade_date = '2025-11-03'
ORDER BY trade_value DESC
LIMIT 10;
```

#### 检查排名数据

```sql
-- 检查 EEE 指标的排名数据
SELECT COUNT(*) FROM concept_stock_daily_rank
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE');
-- 预期结果：2000+ (取决于概念数和股票关联)

-- 查看某概念在某日期的排名 Top 10
SELECT c.concept_name, csr.rank, s.stock_code, s.stock_name, csr.trade_value
FROM concept_stock_daily_rank csr
JOIN concepts c ON csr.concept_id = c.id
JOIN stocks s ON csr.stock_code = s.stock_code
WHERE csr.metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE')
  AND csr.trade_date = '2025-11-03'
  AND c.concept_name = '银行'
ORDER BY csr.rank ASC
LIMIT 10;
```

#### 检查汇总数据

```sql
-- 检查 EEE 指标的汇总数据
SELECT COUNT(*) FROM concept_daily_summary
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE');
-- 预期结果：420 (21 概念 × 20 日期)

-- 查看某概念的日汇总数据
SELECT trade_date, total_value, avg_value, max_value, min_value,
       stocks_total, stocks_with_data
FROM concept_daily_summary
WHERE metric_type_id = (SELECT id FROM metric_types WHERE code = 'EEE')
  AND concept_id = (SELECT id FROM concepts WHERE concept_name = '银行')
ORDER BY trade_date ASC;
```

---

## 🔧 高级使用

### 批量导入脚本（可选）

如果需要快速导入所有文件，可以使用 API 的批量导入功能：

```python
#!/usr/bin/env python3
"""批量导入测试数据"""
import requests
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"
ADMIN_TOKEN = "your_admin_token_here"  # 替换为实际的管理员token

def import_csv():
    """导入CSV文件"""
    file_path = "test-data/test_import_stocks_concepts.csv"

    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"file_type": "CSV"}
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

        response = requests.post(
            f"{BASE_URL}/admin/import/upload",
            files=files,
            data=data,
            headers=headers
        )

        print(f"CSV Import: {response.json()}")

def import_txt_files(metric_code, dir_pattern):
    """导入TXT文件"""
    txt_dir = "test-data"
    txt_files = sorted(Path(txt_dir).glob(f"{metric_code}_*.txt"))

    for file_path in txt_files:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "file_type": "TXT",
                "metric_code": metric_code
            }
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

            response = requests.post(
                f"{BASE_URL}/admin/import/upload",
                files=files,
                data=data,
                headers=headers
            )

            print(f"{file_path.name}: {response.json()}")

if __name__ == "__main__":
    print("开始批量导入...")
    import_csv()
    import_txt_files("EEE", "EEE_*.txt")
    import_txt_files("TTV", "TTV_*.txt")
    print("导入完成！")
```

### 数据清理（回滚测试）

如果需要清理测试数据重新开始：

```sql
-- 警告：这会删除所有导入的测试数据！

-- 1. 删除排名和汇总数据
DELETE FROM concept_stock_daily_rank;
DELETE FROM concept_daily_summary;

-- 2. 删除原始指标数据
DELETE FROM stock_metric_data_raw;

-- 3. 删除导入批次记录
DELETE FROM import_batches;

-- 4. 删除概念映射关系
DELETE FROM stock_concepts;

-- 5. 删除股票（可选）
DELETE FROM stocks;
DELETE FROM concepts;
```

---

## 📈 预期测试覆盖

使用这份测试数据，可以验证以下功能：

### CSV 导入功能
- [x] 文件上传和格式验证
- [x] 列名识别（自动检测列）
- [x] 股票和概念的创建
- [x] 多对多映射关系的建立
- [x] 无效行业值的过滤
- [x] 重复映射的处理

### TXT 导入功能
- [x] 文件上传和编码检测
- [x] Tab 分隔符解析
- [x] 股票代码前缀处理（SH/SZ → 标准代码）
- [x] 日期解析和验证
- [x] 交易值的转换
- [x] 有效性过滤（基于 stock_concepts）

### 排名计算功能
- [x] 按概念分组
- [x] 按指标值排序
- [x] 排名分配（DENSE_RANK）
- [x] 日排名的生成

### 汇总计算功能
- [x] 总值计算（SUM）
- [x] 平均值计算（AVG）
- [x] 最大值计算（MAX）
- [x] 最小值计算（MIN）
- [x] 股票计数

### UI 功能
- [x] 文件选择和预览
- [x] 进度条显示
- [x] 状态提示（等待处理、处理中、成功/失败）
- [x] 错误信息展示
- [x] 轮询机制

### API 功能
- [x] 文件上传端点
- [x] 批次查询端点
- [x] 批次详情端点
- [x] 排名查询（通过 API）
- [x] 汇总查询（通过 API）

---

## 🐛 常见问题

### Q1：某些TXT文件导入后显示"invalid rows"过多

**原因**：CSV中的股票还没导入，或stock_concepts为空

**解决**：
1. 确保CSV先导入
2. 检查导入结果：`SELECT COUNT(*) FROM stock_concepts`
3. 如果为0，重新导入CSV

### Q2：排名计算一直未完成

**原因**：
- 导入的TXT数据格式错误
- 日期不匹配
- 数据库错误

**检查**：
1. 查看 import_batches 表中的 error_message
2. 检查 stock_metric_data_raw 表是否有该批次的数据
3. 查看后端日志

### Q3：如何重新生成测试数据？

**重新生成**：
```bash
# 删除旧文件
rm test-data/*.csv test-data/EEE_*.txt test-data/TTV_*.txt

# 运行生成脚本
python3 test-data/generate_test_data.py
```

**自定义参数**：
编辑 `generate_test_data.py` 中的配置部分：
```python
# 修改股票列表
STOCKS = [...]

# 修改概念列表
CONCEPTS = [...]

# 修改日期范围
start_date = "2025-11-01"
num_days = 20
```

---

## 📝 文件清单

### 生成的文件

```
test-data/
├── generate_test_data.py ................. 生成脚本
├── README.md ............................ 本文件
├── test_import_stocks_concepts.csv ...... CSV测试文件
├── EEE_2025-11-03.txt ................... EEE指标（11月3日）
├── EEE_2025-11-04.txt
├── ... (18个更多EEE文件)
├── EEE_2025-11-28.txt
├── TTV_2025-11-03.txt ................... TTV指标（11月3日）
├── TTV_2025-11-04.txt
├── ... (18个更多TTV文件)
└── TTV_2025-11-28.txt
```

**总计**：
- 1个脚本文件
- 1个CSV文件
- 40个TXT文件（20个EEE + 20个TTV）
- 1个文档文件

---

## ✅ 验证检查清单

导入完成后，用这个清单验证数据完整性：

- [ ] CSV 导入成功，无错误
- [ ] 股票表有 50 条记录
- [ ] 概念表有 21 条记录
- [ ] stock_concepts 表有 209 条映射
- [ ] EEE 原始数据有 1000 行
- [ ] TTV 原始数据有 1000 行
- [ ] EEE 排名数据已生成
- [ ] TTV 排名数据已生成
- [ ] EEE 汇总数据已生成
- [ ] TTV 汇总数据已生成
- [ ] 查询 API 能返回排名数据
- [ ] 查询 API 能返回汇总数据
- [ ] Web UI 能显示导入记录

---

## 📚 相关文档

- `.spec-workflow/data-import-workflow.md` - 导入工作流程完整设计
- `.claude/IMPORT_QUICK_REFERENCE.md` - 导入快速参考指南
- `.claude/IMPORT_LOGIC_ANALYSIS.md` - 基于实际文件的分析

---

**最后更新**: 2025-11-28
**作者**: Claude Code
**版本**: 1.0
