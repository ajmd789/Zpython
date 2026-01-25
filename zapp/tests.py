from django.test import TestCase, Client
import os
import tempfile
import zipfile
import io
from zapp.services.stock_code_service import stock_code_service

class StockCodeDownloadTest(TestCase):
    def setUp(self):
        """设置测试环境，创建测试数据"""
        self.client = Client()
        
        # 创建测试目录和测试文件
        self.test_dir = tempfile.mkdtemp()
        self.original_data_dir = stock_code_service.data_dir
        
        # 将服务的数据目录切换到测试目录
        stock_code_service.data_dir = self.test_dir
        
        # 创建测试文件
        self.test_codes = ['000001', '000002', '000003']
        for code in self.test_codes:
            with open(os.path.join(self.test_dir, f'{code}.txt'), 'w', encoding='utf-8') as f:
                f.write(f'Test data for {code}')
    
    def tearDown(self):
        """清理测试环境"""
        # 恢复原始数据目录
        stock_code_service.data_dir = self.original_data_dir
        
        # 删除测试目录和文件
        for filename in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, filename))
        os.rmdir(self.test_dir)
    
    def test_download_all_code_data(self):
        """测试全量数据下载功能"""
        # 调用全量数据下载接口
        response = self.client.get('/api/downloadAllCodeData/')
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证响应头
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        
        # 验证响应内容是有效的zip文件
        zip_content = b''.join(response.streaming_content)
        zip_file = io.BytesIO(zip_content)
        
        # 检查zip文件是否有效
        self.assertTrue(zipfile.is_zipfile(zip_file))
        
        # 验证zip文件包含所有测试文件
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zip_file_list = zf.namelist()
            for code in self.test_codes:
                self.assertIn(f'{code}.txt', zip_file_list)
                # 验证文件内容
                file_content = zf.read(f'{code}.txt').decode('utf-8')
                self.assertEqual(file_content, f'Test data for {code}')
