# Reddit API 配置指南

> 用于 MuskOrchestrator 信息聚合系统

---

## 步骤1：创建 Reddit 应用

1. 访问 https://www.reddit.com/prefs/apps
2. 登录你的 Reddit 账号
3. 点击 "create another app..."
4. 填写信息：
   - **Name**: `MuskOrchestrator`
   - **Type**: `script`
   - **Description**: `Personal information aggregator for learning`
   - **About URL**: (留空或填你的个人网站)
   - **Redirect URI**: `http://localhost:8080` (script类型必需但不会被使用)
5. 点击 "create app"

---

## 步骤2：获取凭证

创建后会看到：

```
MuskOrchestrator
----------------
personal use script
ID: xxxxxxxxxxxxxx  ← 这是 client_id
Secret: yyyyyyyyyyyyyyyyyyyyyyyyyyyy  ← 这是 client_secret
```

---

## 步骤3：配置到系统

编辑 `config/reddit_config.json`：

```json
{
  "client_id": "xxxxxxxxxxxxxx",
  "client_secret": "yyyyyyyyyyyyyyyyyyyyyyyyyyyy",
  "user_agent": "MuskOrchestrator/1.0 (by /u/YOUR_USERNAME)",
  "username": "YOUR_REDDIT_USERNAME",
  "password": "YOUR_REDDIT_PASSWORD"
}
```

---

## 步骤4：测试

```bash
python -c "
from scripts.sources.reddit_fetcher import RedditFetcher
fetcher = RedditFetcher()
posts = fetcher.fetch(subreddit='entrepreneur', limit=5)
print(f'成功获取 {len(posts)} 条帖子')
for p in posts[:3]:
    print(f'- {p[\"title\"][:50]}...')
"
```

---

## 安全提示

⚠️ **不要将 `reddit_config.json` 提交到 Git！**

已添加到 `.gitignore`：
```
config/reddit_config.json
```

如需分享配置模板，使用：
```bash
cp config/reddit_config.json config/reddit_config.json.example
```

---

## 权限说明

Reddit API 限制：
- 未认证：10 requests/minute
- 已认证：60 requests/minute (OAuth)
- 脚本类型：适合只读数据抓取

我们的配置：
- 每分钟最多30次请求
- 只读取公开帖子
- 不发布/不评论/不投票

---

## 故障排除

| 错误 | 原因 | 解决 |
|------|------|------|
| `401 Unauthorized` | 凭证错误 | 检查 client_id/client_secret |
| `403 Forbidden` | 用户代理被屏蔽 | 更新 user_agent 格式 |
| `429 Too Many Requests` | 速率限制 | 减少请求频率 |
| `404 Not Found` | Subreddit不存在 | 检查 subreddit 名称拼写 |

---

## 相关文件

- `scripts/sources/reddit_fetcher.py` - Reddit 抓取模块
- `scripts/daily_aggregator.py` - 主聚合脚本
- `config/reddit_config.json` - 配置文件（本地）

---

*配置完成后，信息聚合系统将自动包含 Reddit 内容*