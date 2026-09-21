"""数据源插件（每源一个 Adapter，见 registry.SourcePlugin）：进程内单例 registry 在此集中登记。

新增源 = 写一个 `SourcePlugin` 实现 + 这里 register 一行（§6.1 插排式扩展）。
"""

from app.plugins.registry import Registry
from app.plugins.sources.infoq import InfoQSourcePlugin

registry = Registry()
registry.register(InfoQSourcePlugin())
