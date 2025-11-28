-- ============================================================================
-- 清理股票相关数据脚本
-- ============================================================================
-- 用途: 清空数据库中的所有股票相关数据，保留表结构
-- 说明: 按照外键依赖关系删除数据，避免违反约束
-- 使用: psql -U peak -d stock_analysis -f clean_stock_data.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- 第1步: 清理分析结果表（依赖于其他表）
-- ============================================================================

-- 删除排名数据（依赖于 stocks, concepts, metric_types）
DELETE FROM concept_stock_daily_rank;

-- 删除汇总数据（依赖于 concepts, metric_types）
DELETE FROM concept_daily_summary;

-- ============================================================================
-- 第2步: 清理原始导入数据
-- ============================================================================

-- 删除原始指标数据（依赖于 stocks, metric_types）
DELETE FROM stock_metric_data_raw;

-- 删除原始 CSV 导入数据（依赖于 import_batches）
DELETE FROM stock_concept_mapping_raw;

-- 删除导入批次记录（记录所有导入操作）
DELETE FROM import_batches;

-- ============================================================================
-- 第3步: 清理关系映射表
-- ============================================================================

-- 删除股票行业关系（依赖于 stocks, industries）
DELETE FROM stock_industries;

-- 删除股票-概念关系（依赖于 stocks, concepts）
DELETE FROM stock_concepts;

-- ============================================================================
-- 第4步: 清理主数据表
-- ============================================================================

-- 删除股票（依赖关系最多）
DELETE FROM stocks;

-- 删除概念（用于分类）
DELETE FROM concepts;

-- 删除行业（用于分类）
DELETE FROM industries;

COMMIT;

-- ============================================================================
-- 验证: 确认所有表都已清空
-- ============================================================================

SELECT
  '股票表 (stocks)' as 项目,
  COUNT(*) as 记录数
FROM stocks

UNION ALL

SELECT
  '概念表 (concepts)',
  COUNT(*)
FROM concepts

UNION ALL

SELECT
  '行业表 (industries)',
  COUNT(*)
FROM industries

UNION ALL

SELECT
  '股票-概念关系表 (stock_concepts)',
  COUNT(*)
FROM stock_concepts

UNION ALL

SELECT
  '股票行业关系表 (stock_industries)',
  COUNT(*)
FROM stock_industries

UNION ALL

SELECT
  '原始指标数据表 (stock_metric_data_raw)',
  COUNT(*)
FROM stock_metric_data_raw

UNION ALL

SELECT
  '排名数据表 (concept_stock_daily_rank)',
  COUNT(*)
FROM concept_stock_daily_rank

UNION ALL

SELECT
  '汇总数据表 (concept_daily_summary)',
  COUNT(*)
FROM concept_daily_summary

UNION ALL

SELECT
  '导入批次表 (import_batches)',
  COUNT(*)
FROM import_batches

UNION ALL

SELECT
  '原始 CSV 数据表 (stock_concept_mapping_raw)',
  COUNT(*)
FROM stock_concept_mapping_raw

ORDER BY 项目;
