"""缓存服务 - 提高查询性能"""
import json
import redis
from typing import Optional, Any, Dict, List
from datetime import date, timedelta
from functools import wraps
import hashlib
import pickle
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis缓存服务"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.default_expire = 3600  # 默认1小时过期

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"缓存获取失败 {key}: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = None):
        """设置缓存值"""
        try:
            expire = expire or self.default_expire
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"缓存设置失败 {key}: {e}")
            return False

    def delete(self, key: str):
        """删除缓存"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"缓存删除失败 {key}: {e}")

    def delete_pattern(self, pattern: str):
        """删除匹配模式的所有缓存"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"删除了{len(keys)}个匹配{pattern}的缓存")
        except Exception as e:
            logger.error(f"批量删除缓存失败 {pattern}: {e}")

    def cache_decorator(
        self,
        key_prefix: str,
        expire: int = None,
        key_builder=None
    ):
        """
        缓存装饰器

        Args:
            key_prefix: 缓存键前缀
            expire: 过期时间（秒）
            key_builder: 自定义键构建函数
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 构建缓存键
                if key_builder:
                    cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
                else:
                    # 默认使用参数哈希作为键
                    key_data = f"{str(args)}:{str(kwargs)}"
                    key_hash = hashlib.md5(key_data.encode()).hexdigest()
                    cache_key = f"{key_prefix}:{key_hash}"

                # 尝试从缓存获取
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"缓存命中: {cache_key}")
                    return cached_value

                # 执行函数
                result = func(*args, **kwargs)

                # 存入缓存
                self.set(cache_key, result, expire)
                logger.debug(f"缓存更新: {cache_key}")

                return result

            # 添加清除缓存的方法
            wrapper.cache_clear = lambda: self.delete_pattern(f"{key_prefix}:*")

            return wrapper
        return decorator


class ConceptRankingCache:
    """概念排名专用缓存"""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.key_prefix = "ranking"

    def get_concept_ranking(
        self,
        concept_id: int,
        metric_type_id: int,
        trade_date: date
    ) -> Optional[List[Dict]]:
        """获取概念排名缓存"""
        key = self._build_key(concept_id, metric_type_id, trade_date)
        return self.cache.get(key)

    def set_concept_ranking(
        self,
        concept_id: int,
        metric_type_id: int,
        trade_date: date,
        ranking_data: List[Dict],
        expire: int = 1800  # 30分钟
    ):
        """设置概念排名缓存"""
        key = self._build_key(concept_id, metric_type_id, trade_date)
        self.cache.set(key, ranking_data, expire)

    def invalidate_concept(self, concept_id: int):
        """失效指定概念的所有缓存"""
        pattern = f"{self.key_prefix}:{concept_id}:*"
        self.cache.delete_pattern(pattern)

    def invalidate_date(self, trade_date: date):
        """失效指定日期的所有缓存"""
        date_str = trade_date.isoformat()
        pattern = f"{self.key_prefix}:*:{date_str}"
        self.cache.delete_pattern(pattern)

    def _build_key(self, concept_id: int, metric_type_id: int, trade_date: date) -> str:
        """构建缓存键"""
        date_str = trade_date.isoformat()
        return f"{self.key_prefix}:{concept_id}:{metric_type_id}:{date_str}"


class ConceptSummaryCache:
    """概念汇总专用缓存"""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.key_prefix = "summary"

    def get_daily_summary(
        self,
        concept_id: int,
        metric_type_id: int,
        trade_date: date
    ) -> Optional[Dict]:
        """获取日汇总缓存"""
        key = f"{self.key_prefix}:daily:{concept_id}:{metric_type_id}:{trade_date.isoformat()}"
        return self.cache.get(key)

    def set_daily_summary(
        self,
        concept_id: int,
        metric_type_id: int,
        trade_date: date,
        summary_data: Dict,
        expire: int = 3600
    ):
        """设置日汇总缓存"""
        key = f"{self.key_prefix}:daily:{concept_id}:{metric_type_id}:{trade_date.isoformat()}"
        self.cache.set(key, summary_data, expire)

    def get_period_summary(
        self,
        concept_id: int,
        metric_type_id: int,
        start_date: date,
        end_date: date
    ) -> Optional[Dict]:
        """获取期间汇总缓存"""
        key = (f"{self.key_prefix}:period:{concept_id}:{metric_type_id}:"
               f"{start_date.isoformat()}:{end_date.isoformat()}")
        return self.cache.get(key)

    def set_period_summary(
        self,
        concept_id: int,
        metric_type_id: int,
        start_date: date,
        end_date: date,
        summary_data: Dict,
        expire: int = 1800
    ):
        """设置期间汇总缓存"""
        key = (f"{self.key_prefix}:period:{concept_id}:{metric_type_id}:"
               f"{start_date.isoformat()}:{end_date.isoformat()}")
        self.cache.set(key, summary_data, expire)


class ImportStatusCache:
    """导入状态缓存"""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.key_prefix = "import_status"

    def set_import_progress(self, batch_id: int, progress: Dict):
        """设置导入进度"""
        key = f"{self.key_prefix}:{batch_id}"
        # 导入进度缓存10分钟
        self.cache.set(key, progress, expire=600)

    def get_import_progress(self, batch_id: int) -> Optional[Dict]:
        """获取导入进度"""
        key = f"{self.key_prefix}:{batch_id}"
        return self.cache.get(key)

    def update_import_progress(
        self,
        batch_id: int,
        current: int,
        total: int,
        status: str = "processing"
    ):
        """更新导入进度"""
        progress = {
            "current": current,
            "total": total,
            "percentage": round(current * 100 / total, 2) if total > 0 else 0,
            "status": status
        }
        self.set_import_progress(batch_id, progress)


class PreloadedDataCache:
    """预加载数据缓存 - 用于频繁访问的映射关系"""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.key_prefix = "preloaded"

    def get_stock_concepts_map(self) -> Optional[Dict[str, List[int]]]:
        """获取股票-概念映射缓存"""
        key = f"{self.key_prefix}:stock_concepts_map"
        return self.cache.get(key)

    def set_stock_concepts_map(self, mapping: Dict[str, List[int]], expire: int = 300):
        """设置股票-概念映射缓存（5分钟）"""
        key = f"{self.key_prefix}:stock_concepts_map"
        self.cache.set(key, mapping, expire)

    def get_concept_stocks_map(self) -> Optional[Dict[int, Set[str]]]:
        """获取概念-股票映射缓存"""
        key = f"{self.key_prefix}:concept_stocks_map"
        return self.cache.get(key)

    def set_concept_stocks_map(self, mapping: Dict[int, Set[str]], expire: int = 300):
        """设置概念-股票映射缓存（5分钟）"""
        key = f"{self.key_prefix}:concept_stocks_map"
        # Set需要转换为List来序列化
        serializable_mapping = {k: list(v) for k, v in mapping.items()}
        self.cache.set(key, serializable_mapping, expire)

    def invalidate_all(self):
        """失效所有预加载缓存"""
        self.cache.delete_pattern(f"{self.key_prefix}:*")