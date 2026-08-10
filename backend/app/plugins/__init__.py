"""插件实现（数据源 / 处理步骤 / 筛选规则）。

新增能力 = 新增插件，不改核心：
- 新数据源：plugins/sources/ 写 Adapter + config/sources/ 一条配置
- 新处理步骤：plugins/processors/ 写 Stage + config/pipeline.yaml 声明
"""

from app.plugins import processors, registry, sources

__all__ = ["processors", "registry", "sources"]
