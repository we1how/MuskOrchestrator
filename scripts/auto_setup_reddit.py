#!/usr/bin/env python3
"""
Reddit API 自动配置 - 使用 Playwright 模拟浏览器
授权：用户已提供账号信息并开放权限
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def setup_reddit_api():
    """自动登录 Reddit 并创建应用获取 API 凭证"""

    # 用户凭证
    REDDIT_USERNAME = "linyoujia0886"
    REDDIT_PASSWORD = "13580lwh"
    GOOGLE_EMAIL = "linyoujia0886@gmail.com"

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 可视化便于调试
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            print("步骤 1: 访问 Reddit...")
            await page.goto("https://www.reddit.com")
            await asyncio.sleep(2)

            # 点击登录
            print("步骤 2: 点击登录按钮...")
            login_btn = await page.query_selector('a[href*="login"]')
            if login_btn:
                await login_btn.click()
            else:
                # 尝试其他选择器
                await page.click('text=Log In')

            await asyncio.sleep(2)

            # 查找 Google 登录按钮
            print("步骤 3: 查找 Google 登录选项...")

            # 可能需要切换到登录 iframe 或弹出窗口
            # 等待页面加载
            await page.wait_for_load_state('networkidle')

            # 查找 Continue with Google 按钮
            google_btn = await page.query_selector('button:has-text("Continue with Google")')
            if not google_btn:
                google_btn = await page.query_selector('text=Continue with Google')
            if not google_btn:
                google_btn = await page.query_selector('[data-testid="google-auth"]')

            if google_btn:
                print("  ✓ 找到 Google 登录按钮")
                await google_btn.click()
                await asyncio.sleep(3)
            else:
                print("  ✗ 未找到 Google 登录按钮，可能需要手动操作")
                print("  请手动完成登录流程，按 Enter 继续...")
                input()

            # 处理 Google 登录弹窗
            print("步骤 4: 处理 Google 登录...")

            # 等待新页面或弹窗
            await asyncio.sleep(3)

            # 检查是否有 Google 登录页面
            pages = context.pages
            google_page = None
            for p in pages:
                url = p.url
                if 'accounts.google.com' in url or 'google.com/signin' in url:
                    google_page = p
                    break

            if google_page:
                print("  ✓ 找到 Google 登录页面")

                # 输入邮箱
                await google_page.wait_for_selector('input[type="email"]')
                await google_page.fill('input[type="email"]', GOOGLE_EMAIL)
                await google_page.click('#identifierNext, button:has-text("Next")')

                await asyncio.sleep(2)

                # 输入密码
                await google_page.wait_for_selector('input[type="password"]')
                await google_page.fill('input[type="password"]', GOOGLE_PASSWORD)
                await google_page.click('#passwordNext, button:has-text("Next")')

                await asyncio.sleep(5)

                print("  ✓ Google 登录完成")
            else:
                print("  ! 未检测到 Google 登录页面，可能已在其他页面完成")

            # 等待回到 Reddit
            print("步骤 5: 等待 Reddit 登录完成...")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)

            # 验证登录状态
            user_menu = await page.query_selector('[data-testid="user-menu-button"]')
            if user_menu:
                print("  ✓ Reddit 登录成功!")
            else:
                print("  ! 可能需要手动完成登录")
                print("  完成后按 Enter 继续...")
                input()

            # 访问应用创建页面
            print("步骤 6: 访问应用创建页面...")
            await page.goto("https://www.reddit.com/prefs/apps")
            await asyncio.sleep(3)

            # 点击创建应用
            print("步骤 7: 创建新应用...")
            create_btn = await page.query_selector('button:has-text("create another app")')
            if create_btn:
                await create_btn.click()
            else:
                await page.click('text=create another app')

            await asyncio.sleep(2)

            # 填写应用信息
            print("步骤 8: 填写应用信息...")

            # 选择类型为 script
            await page.click('input[value="script"]')

            # 填写名称
            await page.fill('input[name="name"]', 'MuskOrchestrator')

            # 填写描述
            await page.fill('textarea[name="description"]', 'Personal information aggregator for learning')

            # 填写 Redirect URI
            await page.fill('input[name="redirect_uri"]', 'http://localhost:8080')

            await asyncio.sleep(1)

            # 提交
            print("步骤 9: 提交创建...")
            await page.click('button[type="submit"]')

            await asyncio.sleep(3)

            # 提取凭证
            print("步骤 10: 提取 API 凭证...")

            # 查找刚创建的应用
            app_section = await page.query_selector('.developed-app')
            if app_section:
                # 提取 client_id
                client_id_elem = await app_section.query_selector('h3')
                if client_id_elem:
                    client_id = await client_id_elem.text_content()
                    print(f"  ✓ Client ID: {client_id}")

                # 提取 client_secret
                secret_elem = await app_section.query_selector('td:has-text("secret") + td')
                if secret_elem:
                    client_secret = await secret_elem.text_content()
                    print(f"  ✓ Client Secret: {client_secret[:10]}...")

                # 保存配置
                config = {
                    "client_id": client_id.strip() if client_id else "",
                    "client_secret": client_secret.strip() if client_secret else "",
                    "user_agent": "MuskOrchestrator/1.0 (by /u/linyoujia0886)",
                    "username": "linyoujia0886",
                    "password": GOOGLE_PASSWORD,
                    "login_method": "google",
                    "google_email": GOOGLE_EMAIL
                }

                config_path = Path("/Users/linweihao/project/MuskOrchestrator/config/reddit_config.json")
                config_path.parent.mkdir(parents=True, exist_ok=True)

                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)

                print(f"\n✓ 配置已保存到: {config_path}")

            else:
                print("  ✗ 未找到应用信息，请手动复制")
                print("  完成后按 Enter 关闭浏览器...")
                input()

            # 保持浏览器打开以便查看
            print("\n按 Enter 关闭浏览器...")
            input()

        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            print("按 Enter 关闭浏览器...")
            input()

        finally:
            await browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Reddit API 自动配置")
    print("=" * 60)
    print()
    print("此脚本将:")
    print("1. 打开 Reddit 登录页面")
    print("2. 使用 Google 账号登录")
    print("3. 创建 API 应用")
    print("4. 自动提取并保存凭证")
    print()
    print("请确保已安装 Playwright:")
    print("  pip install playwright")
    print("  playwright install chromium")
    print()

    confirm = input("是否开始? (y/n): ")
    if confirm.lower() == 'y':
        asyncio.run(setup_reddit_api())
    else:
        print("已取消")
