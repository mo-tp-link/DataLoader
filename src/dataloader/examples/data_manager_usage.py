"""
DataManager 使用示例

展示如何使用 DataManager 作为数据仓库层进行数据管理。
"""

from dataloader import DataManager


def basic_usage():
    """基础用法：按名称加载数据"""
    # 初始化 DataManager
    dm = DataManager(data_dir="./data")

    # 方式 1: 使用 get() 方法
    stock_result = dm.get("stock")

    # 方式 2: 使用字典式访问
    inv_result = dm["inv"]

    # 方式 3: 使用属性访问
    price_result = dm.price

    # 获取 DataFrame（收集 LazyFrame）
    stock_df = stock_result.frame.collect()
    print(f"Stock data shape: {stock_df.shape}")

    # 直接获取 DataFrame 的快捷方式
    pos_df = dm.collect("pos")
    print(f"POS data shape: {pos_df.shape}")


def dependency_resolution():
    """依赖解析：自动加载依赖项"""
    dm = DataManager()

    # bo 依赖 inv 和 stock，会自动加载
    bo_result = dm.get("bo")

    # trans 依赖 stock，会自动加载
    trans_result = dm.get("trans")

    # 查看缓存状态
    print(f"Cached sources: {dm.cached}")


def caching_example():
    """缓存示例：避免重复加载"""
    dm = DataManager()

    # 第一次加载（从文件读取）
    stock1 = dm.get("stock")

    # 第二次加载（从缓存读取）
    stock2 = dm.get("stock")

    # 强制刷新
    stock3 = dm.get("stock", refresh=True)

    # 失效缓存
    dm.invalidate("stock")

    # 失效所有缓存
    dm.invalidate_all()


def configuration_example():
    """配置示例：自定义加载参数"""
    dm = DataManager()

    # 配置特定数据源的参数
    dm.configure("stock", path="./data/custom_stock.csv")

    # 链式调用
    result = dm.configure("price", path="./data/new_price.xlsx").get("price")

    # 一次性覆盖参数（不影响配置）
    custom_result = dm.get("stock", path="./data/another_stock.csv")


def preload_example():
    """预加载示例：批量加载数据"""
    dm = DataManager()

    # 预加载指定数据源
    dm.preload("stock", "inv", "price")

    # 预加载所有数据源
    dm.preload()

    print(f"All sources loaded: {dm.cached}")


def schema_access():
    """访问 Schema"""
    dm = DataManager()

    # 获取 schema 对象
    stock_schema = dm.schema("stock")
    print(f"Stock columns: {stock_schema.all_cols}")


def inject_into_class():
    """依赖注入示例：将 DataManager 注入其他类"""

    class SalesAnalyzer:
        """销售分析类，使用 DataManager 获取数据"""

        def __init__(self, data_manager: DataManager):
            self.dm = data_manager

        def analyze_stock_vs_sales(self):
            stock_df = self.dm.collect("stock")
            pos_df = self.dm.collect("pos")

            # 进行分析...
            return {"stock_count": len(stock_df), "pos_count": len(pos_df)}

        def get_backorder_status(self):
            # bo 会自动加载其依赖 (inv, stock)
            bo_result = self.dm.get("bo")
            return bo_result.frame.collect()

    # 使用
    dm = DataManager()
    analyzer = SalesAnalyzer(dm)
    result = analyzer.analyze_stock_vs_sales()
    print(result)


def status_inspection():
    """状态检查：查看数据源信息"""
    dm = DataManager()

    # 查看可用数据源
    print(f"Available: {dm.available}")

    # 查看缓存状态
    print(f"Cached: {dm.cached}")

    # 查看详细状态
    for name, info in dm.status().items():
        print(f"{name}:")
        print(f"  - cached: {info['cached']}")
        print(f"  - dependencies: {info['dependencies']}")
        print(f"  - loader: {info['loader']}")
        print(f"  - processor: {info['processor']}")


if __name__ == "__main__":
    # 运行示例
    status_inspection()
