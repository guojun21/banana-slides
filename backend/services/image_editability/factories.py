"""
工厂类 - 负责创建和配置具体的提取器和Inpaint提供者
"""
import logging
from typing import List, Optional, Any
from pathlib import Path

from .extractors import ElementExtractor, MinerUElementExtractor, BaiduOCRElementExtractor, ExtractorRegistry
from .inpaint_providers import InpaintProvider, DefaultInpaintProvider, GenerativeEditInpaintProvider, InpaintProviderRegistry

logger = logging.getLogger(__name__)


class ExtractorFactory:
    """元素提取器工厂"""
    
    @staticmethod
    def create_default_extractors(
        parser_service: Any,
        upload_folder: Path,
        baidu_table_ocr_provider: Optional[Any] = None
    ) -> List[ElementExtractor]:
        """
        创建默认的元素提取器列表
        
        Args:
            parser_service: MinerU解析服务实例
            upload_folder: 上传文件夹路径
            baidu_table_ocr_provider: 百度表格OCR Provider实例（可选）
        
        Returns:
            提取器列表（按优先级排序）
        
        Note:
            推荐使用 create_extractor_registry() 方法，它提供更清晰的类型到提取器映射
        """
        extractors: List[ElementExtractor] = []
        
        # 1. 百度OCR提取器（用于表格）
        if baidu_table_ocr_provider is None:
            try:
                from services.ai_providers.ocr import create_baidu_table_ocr_provider
                baidu_provider = create_baidu_table_ocr_provider()
                if baidu_provider:
                    extractors.append(BaiduOCRElementExtractor(baidu_provider))
                    logger.info("✅ 百度表格OCR提取器已启用")
            except Exception as e:
                logger.warning(f"无法初始化百度表格OCR: {e}")
        else:
            extractors.append(BaiduOCRElementExtractor(baidu_table_ocr_provider))
            logger.info("✅ 百度表格OCR提取器已启用")
        
        # 2. MinerU提取器（默认通用提取器）
        mineru_extractor = MinerUElementExtractor(parser_service, upload_folder)
        extractors.append(mineru_extractor)
        logger.info("✅ MinerU提取器已启用")
        
        return extractors
    
    @staticmethod
    def create_extractor_registry(
        parser_service: Any,
        upload_folder: Path,
        baidu_table_ocr_provider: Optional[Any] = None
    ) -> ExtractorRegistry:
        """
        创建元素类型到提取器的注册表
        
        默认配置：
        - 表格类型（table, table_cell）→ 百度OCR（如果可用），否则MinerU
        - 图片类型（image, figure, chart）→ MinerU
        - 其他类型 → MinerU（默认）
        
        Args:
            parser_service: MinerU解析服务实例
            upload_folder: 上传文件夹路径
            baidu_table_ocr_provider: 百度表格OCR Provider实例（可选）
        
        Returns:
            配置好的ExtractorRegistry实例
        """
        # 创建MinerU提取器
        mineru_extractor = MinerUElementExtractor(parser_service, upload_folder)
        logger.info("✅ MinerU提取器已创建")
        
        # 尝试创建百度OCR提取器
        baidu_ocr_extractor = None
        if baidu_table_ocr_provider is None:
            try:
                from services.ai_providers.ocr import create_baidu_table_ocr_provider
                baidu_provider = create_baidu_table_ocr_provider()
                if baidu_provider:
                    baidu_ocr_extractor = BaiduOCRElementExtractor(baidu_provider)
                    logger.info("✅ 百度表格OCR提取器已创建")
            except Exception as e:
                logger.warning(f"无法初始化百度表格OCR: {e}")
        else:
            baidu_ocr_extractor = BaiduOCRElementExtractor(baidu_table_ocr_provider)
            logger.info("✅ 百度表格OCR提取器已创建")
        
        # 使用注册表的工厂方法创建默认配置
        return ExtractorRegistry.create_default(
            mineru_extractor=mineru_extractor,
            baidu_ocr_extractor=baidu_ocr_extractor
        )


class InpaintProviderFactory:
    """Inpaint提供者工厂"""
    
    @staticmethod
    def create_default_provider(inpainting_service: Optional[Any] = None) -> Optional[InpaintProvider]:
        """
        创建默认的Inpaint提供者（使用Volcengine Inpainting服务）
        
        Args:
            inpainting_service: InpaintingService实例（可选）
        
        Returns:
            InpaintProvider实例，失败返回None
        """
        if inpainting_service is not None:
            logger.info("使用提供的InpaintingService")
            return DefaultInpaintProvider(inpainting_service)
        
        # 尝试自动初始化
        try:
            from services.inpainting_service import get_inpainting_service
            inpainting_service = get_inpainting_service()
            logger.info("自动初始化DefaultInpaintProvider")
            return DefaultInpaintProvider(inpainting_service)
        except Exception as e:
            logger.warning(f"无法初始化Inpainting服务: {e}")
            return None
    
    @staticmethod
    def create_generative_edit_provider(
        ai_service: Optional[Any] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "2K"
    ) -> Optional[InpaintProvider]:
        """
        创建基于生成式大模型的Inpaint提供者
        
        使用生成式大模型（如Gemini图片编辑）通过自然语言指令移除图片中的文字和图标。
        适用于不需要精确bbox的场景，大模型自动理解并移除相关元素。
        
        Args:
            ai_service: AIService实例（可选，如果不提供则自动获取）
            aspect_ratio: 目标宽高比
            resolution: 目标分辨率
        
        Returns:
            GenerativeEditInpaintProvider实例，失败返回None
        """
        if ai_service is not None:
            logger.info("使用提供的AIService创建GenerativeEditInpaintProvider")
            return GenerativeEditInpaintProvider(ai_service, aspect_ratio, resolution)
        
        # 尝试自动获取AI服务
        try:
            from services.ai_service_manager import get_ai_service
            ai_service = get_ai_service()
            logger.info("自动初始化GenerativeEditInpaintProvider")
            return GenerativeEditInpaintProvider(ai_service, aspect_ratio, resolution)
        except Exception as e:
            logger.warning(f"无法初始化生成式编辑服务: {e}")
            return None
    
    @staticmethod
    def create_inpaint_registry(
        mask_provider: Optional[InpaintProvider] = None,
        generative_provider: Optional[InpaintProvider] = None,
        default_provider_type: str = "generative"
    ) -> InpaintProviderRegistry:
        """
        创建重绘方法注册表
        
        支持动态注册新元素类型，不限于预定义类型。
        
        Args:
            mask_provider: 基于mask的重绘提供者（可选，自动创建）
            generative_provider: 生成式重绘提供者（可选，自动创建）
            default_provider_type: 默认使用的提供者类型 ("mask" 或 "generative")
        
        Returns:
            配置好的InpaintProviderRegistry实例
        """
        # 自动创建提供者
        if mask_provider is None:
            mask_provider = InpaintProviderFactory.create_default_provider()
        
        if generative_provider is None:
            generative_provider = InpaintProviderFactory.create_generative_edit_provider()
        
        # 创建注册表
        registry = InpaintProviderRegistry()
        
        # 设置默认提供者
        if default_provider_type == "generative" and generative_provider:
            registry.register_default(generative_provider)
        elif mask_provider:
            registry.register_default(mask_provider)
        elif generative_provider:
            registry.register_default(generative_provider)
        
        # 注册类型映射（可通过registry.register()动态扩展）
        if mask_provider:
            # 文本和表格使用mask-based精确移除
            registry.register_types(['text', 'title', 'paragraph'], mask_provider)
            registry.register_types(['table', 'table_cell'], mask_provider)
        
        if generative_provider:
            # 图片和图表使用生成式重绘
            registry.register_types(['image', 'figure', 'chart', 'diagram'], generative_provider)
        
        logger.info(f"创建InpaintProviderRegistry: 默认={default_provider_type}, "
                   f"mask={mask_provider is not None}, generative={generative_provider is not None}")
        
        return registry


class ServiceConfig:
    """服务配置类 - 纯配置，不持有具体服务引用"""
    
    def __init__(
        self,
        upload_folder: Path,
        extractor_registry: ExtractorRegistry,
        inpaint_registry: InpaintProviderRegistry,
        max_depth: int = 1,
        min_image_size: int = 200,
        min_image_area: int = 40000
    ):
        """
        初始化服务配置
        
        Args:
            upload_folder: 上传文件夹路径
            extractor_registry: 元素类型到提取器的注册表
            inpaint_registry: 元素类型到重绘方法的注册表
            max_depth: 最大递归深度（默认1）
            min_image_size: 最小图片尺寸
            min_image_area: 最小图片面积
        """
        self.upload_folder = upload_folder
        self.extractor_registry = extractor_registry
        self.inpaint_registry = inpaint_registry
        self.max_depth = max_depth
        self.min_image_size = min_image_size
        self.min_image_area = min_image_area
    
    @classmethod
    def from_defaults(
        cls,
        mineru_token: str,
        mineru_api_base: str = "https://mineru.net",
        upload_folder: str = "./uploads",
        ai_service: Optional[Any] = None,
        **kwargs
    ) -> 'ServiceConfig':
        """
        从默认参数创建配置
        
        默认配置（推荐用于导出PPTX）：
        - 元素提取：MinerU通用版面分割
        - 背景生成：GenerativeEdit（生成式大模型）
        - 递归深度：1
        
        支持动态注册新的元素类型到不同的提取器/重绘方法。
        
        Args:
            mineru_token: MinerU API token
            mineru_api_base: MinerU API base URL
            upload_folder: 上传文件夹路径
            ai_service: AI服务实例（可选，用于生成式重绘）
            **kwargs: 其他配置参数
                - max_depth: 最大递归深度（默认1）
                - min_image_size: 最小图片尺寸（默认200）
                - min_image_area: 最小图片面积（默认40000）
        
        Returns:
            ServiceConfig实例
        """
        from services.file_parser_service import FileParserService
        
        # 解析upload_folder路径
        upload_path = Path(upload_folder)
        if not upload_path.is_absolute():
            current_file = Path(__file__).resolve()
            backend_dir = current_file.parent.parent
            project_root = backend_dir.parent
            upload_path = project_root / upload_folder.lstrip('./')
        
        logger.info(f"Upload folder resolved to: {upload_path}")
        
        # 创建MinerU解析服务
        parser_service = FileParserService(
            mineru_token=mineru_token,
            mineru_api_base=mineru_api_base
        )
        
        # 创建MinerU提取器（通用分割）
        mineru_extractor = MinerUElementExtractor(parser_service, upload_path)
        logger.info("✅ MinerU提取器已创建（通用分割）")
        
        # 创建提取器注册表 - 使用MinerU作为通用提取器
        extractor_registry = ExtractorRegistry()
        extractor_registry.register_default(mineru_extractor)
        # 可通过 extractor_registry.register('新类型', 新提取器) 动态扩展
        logger.info("✅ 提取器注册表已创建（MinerU通用）")
        
        # 创建生成式重绘提供者
        generative_provider = InpaintProviderFactory.create_generative_edit_provider(
            ai_service=ai_service
        )
        
        # 创建重绘注册表 - 使用生成式重绘作为默认
        inpaint_registry = InpaintProviderRegistry()
        if generative_provider:
            inpaint_registry.register_default(generative_provider)
            logger.info("✅ 重绘注册表已创建（GenerativeEdit通用）")
        else:
            logger.warning("⚠️ 未能创建生成式重绘提供者")
        # 可通过 inpaint_registry.register('新类型', 新重绘方法) 动态扩展
        
        return cls(
            upload_folder=upload_path,
            extractor_registry=extractor_registry,
            inpaint_registry=inpaint_registry,
            max_depth=kwargs.get('max_depth', 1),  # 默认递归深度1
            min_image_size=kwargs.get('min_image_size', 200),
            min_image_area=kwargs.get('min_image_area', 40000)
        )

