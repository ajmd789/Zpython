# stock_api_utils.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Callable, Optional, Dict, Any
from urllib.parse import urlencode

# 常用 Android 风格 User-Agent，模拟来自移动端的请求以降低被识别为爬虫的风险
ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/86.0.4240.198 Mobile Safari/537.36"
)

class StockApiUtils:
    """
    股票API工具类，用于获取股票数据
    封装了对百度金融API的请求
    """
    
    BASE_URL = "https://finance.pae.baidu.com/"
    
    def __init__(self, stock_code: str):
        """
        初始化StockApiUtils实例
        
        Args:
            stock_code: 股票代码（如：sh600519, sz000001）
        """
        self.stock_code = stock_code
    
    def _build_request_url(self) -> str:
        """构建股票数据请求URL"""
        params = {
            'srcid': '5353',
            'all': '1',
            'pointType': 'string',
            'group': 'quotation_kline_ab',
            'market_type': 'ab',
            'newFormat': '1',
            'finClientType': 'pc',
            'query': self.stock_code,
            'code': self.stock_code,
            'ktype': 'day'
        }
        return f"{self.BASE_URL}vapi/v1/getquotation?{urlencode(params)}"
    
    def fetch_stock_data(self, 
                        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                        timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        发送股票数据请求（同步方法）
        
        Args:
            callback: 可选的回调函数，接收响应字典作为参数
            timeout: 请求超时时间（秒），默认30秒
            
        Returns:
            如果未提供回调函数，则直接返回响应字典；
            如果提供了回调函数，则返回None，通过回调返回数据
        """
        url = self._build_request_url()
        
        # 使用 requests Session 并配置重试，以提高稳定性
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            'User-Agent': ANDROID_UA,
            'Referer': 'https://finance.baidu.com/',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }

        try:
            response = session.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {'success': False, 'error': str(e)}
        
        if callback:
            callback(data)
            return None
        return data


