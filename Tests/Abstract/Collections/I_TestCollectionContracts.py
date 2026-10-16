from abc import ABC, abstractmethod


# 验证影像、顶点、字段和截面集合的查询契约及数据隔离。
class I_TestCollectionContracts(ABC):
    # 验证数量、索引及指纹查询保持导入顺序和去重语义。
    @abstractmethod
    def test_image_queries_preserve_order_and_deduplication(self) -> None: ...

    # 验证影像集合不再提供暴露内部列表或指纹字典的接口。
    @abstractmethod
    def test_image_collection_does_not_expose_storage(self) -> None: ...

    # 修改原始点输入，验证只读顶点快照保持顺序和数值精度。
    @abstractmethod
    def test_points_are_ordered_independent_snapshots(self) -> None: ...

    # 修改原字段列表，核验字段快照仍保持名称、顺序和索引边界。
    @abstractmethod
    def test_record_fields_are_read_only_and_ordered(self) -> None: ...

    # 核验顶点接口序列化后仍使用历史 JSON 字段和坐标数组。
    @abstractmethod
    def test_polygon_serialization_preserves_existing_schema(self) -> None: ...

    # 验证封装后的多边形仍拒绝不足三个点或非有限坐标。
    @abstractmethod
    def test_polygon_validation_is_preserved(self) -> None: ...

    # 验证 LP、PS、SL 具名查询保留既定轴定义与配色。
    @abstractmethod
    def test_planes_have_named_getters_and_original_axes(self) -> None: ...

    # 验证单层轮廓通过索引读取、替换和删除，而不取得内部列表。
    @abstractmethod
    def test_slice_polygons_are_accessed_and_modified_by_index(self) -> None: ...
