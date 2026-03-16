# 微信指数替代方案

> 由于微信指数没有官方开放 API，以下是可行的替代数据获取方案

---

## 一、方案对比

| 方案 | 难度 | 稳定性 | 合规性 | 推荐度 |
|------|------|--------|--------|--------|
| **新榜/清博大数据** | ⭐⭐ 低 | ⭐⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐⭐ 完全合规 | ⭐⭐⭐⭐⭐ 首选 |
| **微信广告 API** | ⭐⭐⭐ 中 | ⭐⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐⭐ 合规 | ⭐⭐⭐⭐ 次选 |
| **小程序逆向** | ⭐⭐⭐⭐ 高 | ⭐⭐ 低 | ⭐⭐ 有风险 | ⭐⭐ 不推荐 |
| **手动+OCR** | ⭐ 极低 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 合规 | ⭐⭐⭐ 小规模 |

---

## 二、推荐方案：新榜 API

### 2.1 新榜数据平台

**网址**: https://www.newrank.cn

**提供数据**:
- 微信公众号文章阅读量/点赞/在看
- 公众号排名和影响力指数
- 文章传播趋势
- 行业热点话题

**API 文档**: https://www.newrank.cn/public/product.html

### 2.2 接入示例

```python
import requests
import hashlib
import time

class NewRankAPI:
    """新榜数据 API 接入示例"""

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api.newrank.cn/api"

    def _generate_sign(self, params: dict) -> str:
        """生成请求签名"""
        # 按key排序并拼接
        sorted_params = sorted(params.items())
        sign_str = self.app_secret + ''.join([f"{k}{v}" for k, v in sorted_params]) + self.app_secret
        return hashlib.md5(sign_str.encode()).hexdigest().upper()

    def get_account_info(self, account: str):
        """获取公众号信息"""
        params = {
            'account': account,
            'app_key': self.app_key,
            'timestamp': str(int(time.time()))
        }
        params['sign'] = self._generate_sign(params)

        response = requests.get(
            f"{self.base_url}/account/info",
            params=params
        )
        return response.json()

    def get_hot_articles(self, category: str = "tech", days: int = 7):
        """获取热门文章"""
        params = {
            'category': category,
            'days': days,
            'app_key': self.app_key,
            'timestamp': str(int(time.time()))
        }
        params['sign'] = self._generate_sign(params)

        response = requests.get(
            f"{self.base_url}/article/hot",
            params=params
        )
        return response.json()

# 使用示例
# api = NewRankAPI(app_key="your_key", app_secret="your_secret")
# hot_articles = api.get_hot_articles(category="finance", days=7)
```

---

## 三、次选方案：微信广告服务商 API

### 3.1 微信广告 API

如果你有微信广告投放需求，可以通过广告服务商获取部分趋势数据：

**申请地址**: https://ad.qq.com/guide/22

**可获得数据**:
- 广告关键词热度趋势
- 行业投放趋势
- 受众兴趣分布

---

## 四、技术方案：小程序逆向（不推荐）

### 4.1 技术原理

通过微信小程序抓包获取请求参数：

```
请求端点: https://search.weixin.qq.com/cgi-bin/wxaweb/wxindex
请求方式: POST
```

### 4.2 实现步骤

1. **安装抓包工具**: Charles 或 Fiddler
2. **配置手机代理**: 手机与电脑同一WiFi，设置代理
3. **安装 SSL 证书**: 手机信任抓包工具的证书
4. **打开微信指数小程序**: 搜索关键词，观察抓包
5. **提取参数**: 记录 openid 和 search_key

### 4.3 Python 代码示例

```python
import requests
import urllib3

urllib3.disable_warnings()

class WeChatIndexCrawler:
    """
    微信指数数据获取（需手动抓取参数）
    注意：此方式可能违反微信服务协议，仅供技术研究
    """

    def __init__(self, openid: str, search_key: str):
        self.openid = openid
        self.search_key = search_key
        self.url = "https://search.weixin.qq.com/cgi-bin/wxaweb/wxindex"

    def get_index(self, keyword: str, start_date: str, end_date: str):
        """
        获取关键词指数

        Args:
            keyword: 搜索关键词
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        headers = {
            'Host': 'search.weixin.qq.com',
            'Referer': 'https://servicewechat.com/wxc026e7662ec26a3a/42/page-frame.html',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'Connection': 'keep-alive'
        }

        data = {
            "openid": self.openid,           # 从小程序抓包获取
            "search_key": self.search_key,   # 从小程序抓包获取
            "cgi_name": "GetMultiChannel",
            "query": [keyword],
            "start_ymd": start_date.replace("-", ""),
            "end_ymd": end_date.replace("-", "")
        }

        try:
            response = requests.post(
                self.url,
                json=data,
                headers=headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching index for {keyword}: {e}")
            return None

    def parse_index_data(self, raw_data: dict):
        """解析指数数据"""
        if not raw_data or 'data' not in raw_data:
            return []

        results = []
        for item in raw_data['data'].get('results', []):
            keyword = item.get('query', '')
            index_data = item.get('index', [])

            for point in index_data:
                results.append({
                    'keyword': keyword,
                    'date': point.get('date', ''),
                    'index': point.get('index', 0),
                    'channel': point.get('channel', '')
                })

        return results

# 使用示例（需要先抓包获取参数）
# crawler = WeChatIndexCrawler(
#     openid="从抓包获取",
#     search_key="从抓包获取"
# )
# data = crawler.get_index("人工智能", "2025-01-01", "2025-03-01")
# parsed = crawler.parse_index_data(data)
```

### 4.4 风险提示

⚠️ **法律风险**: 逆向工程可能违反《微信软件许可及服务协议》

⚠️ **稳定性风险**:
- Token 有效期短（通常几小时）
- 频繁请求会触发风控
- 接口随时可能变更

⚠️ **数据限制**:
- 仅支持7/30/90天数据
- 每小时有请求配额限制

---

## 五、人工方案：截图+OCR

对于小规模、低频需求：

1. **微信小程序搜索关键词**
2. **截图保存趋势图**
3. **使用 OCR 提取数据**

```python
import pytesseract
from PIL import Image

def extract_chart_data(image_path: str):
    """从截图中提取指数数据"""
    img = Image.open(image_path)
    # 预处理图像（二值化、去噪）
    # 使用 OCR 识别文字
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    return text
```

---

## 六、推荐集成方案

### 6.1 第一阶段：新榜 API（立即可用）

```python
# scripts/sources/wechat_trend.py
from .base import BaseFetcher, ContentItem

class WeChatTrendFetcher(BaseFetcher):
    """
    微信生态趋势数据获取（基于新榜 API）
    """

    def __init__(self, cache_dir=None, cache_ttl_hours=6):
        super().__init__(cache_dir, cache_ttl_hours)
        # 需要配置新榜 API Key
        self.api_key = None  # 从环境变量或配置文件读取

    def fetch(self, days: int = 7, limit: int = 20) -> List[ContentItem]:
        """获取微信生态热门话题"""
        # 实现新榜 API 调用
        pass
```

### 6.2 配置步骤

1. **注册新榜账号**: https://www.newrank.cn
2. **申请 API 权限**: 联系新榜商务获取 API Key
3. **配置到系统**:
   ```bash
   # config/newrank_config.json
   {
     "app_key": "your_app_key",
     "app_secret": "your_app_secret",
     "categories": ["tech", "finance", "business"]
   }
   ```

---

## 七、其他中文数据源

| 平台 | 数据类型 | API 可用性 |
|------|----------|-----------|
| **百度指数** | 搜索趋势 | 需申请，有限制 |
| **微博指数** | 社交热度 | 开放平台 API |
| **抖音热点** | 短视频趋势 | 字节跳动开放平台 |
| **知乎热榜** | 问答热度 | 可直接抓取 |
| **今日头条** | 资讯热度 | 需申请 API |

---

## 八、决策建议

### 如果预算充足（推荐）
**选择新榜/清博大数据 API**
- 稳定可靠
- 数据全面
- 完全合规
- 成本：约 ¥500-2000/月

### 如果预算有限
**选择知乎热榜 + 微博指数**
- 知乎热榜：可直接抓取
- 微博指数：开放平台 API
- 组合使用可覆盖大部分需求

### 如果需要精准微信数据
**手动查询 + 记录**
- 每周手动查询关键指标
- 记录到电子表格
- 适合小规模监测

---

## 九、下一步行动

1. **高优先级**: 注册新榜账号，申请 API 试用
2. **中优先级**: 集成知乎热榜作为补充
3. **可选**: 评估是否需要微信指数精准数据

---

*文档更新时间: 2026-03-16*
*状态: 待接入新榜 API*
