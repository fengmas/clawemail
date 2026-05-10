# ClawEmail 邀请码监控

自动从 [ClawEmail](https://claw.163.com) 获取邀请码，区分**待使用**和**已使用**状态，并提供 API 接口。

## 架构

```
GitHub Actions (每10分钟)
    │
    ▼
generate_api.py ───→ invites_api.json ───→ GitHub Pages Web 页面
                        (API 数据)           (可视化监控)
                        │
                        └──→ raw.githubusercontent.com
                              (外部程序可调用的 API 端点)
```

## API 地址

推送代码到 GitHub 后：

**API 数据接口：**
```
https://raw.githubusercontent.com/你的用户名/clawemail/main/invites_api.json
```

**Web 监控页面 (GitHub Pages)：**
```
https://你的用户名.github.io/clawemail/
```

## API 响应格式

```json
{
  "code": 200,
  "message": "success",
  "success": true,
  "data": {
    "summary": {
      "total": 8,
      "unused": 5,
      "used": 3
    },
    "account": {
      "display_name": "用户名",
      "email": "user@example.com",
      "role": "user"
    },
    "invites": {
      "unused": [
        { "code": "CLAWXXXXXX", "status": "unused", "status_text": "待使用" }
      ],
      "used": [
        { "code": "CLAWXXXXXX", "status": "used", "status_text": "已使用",
          "used_by": "u***@qq.com", "used_at": "2026-05-08T22:23:24" }
      ]
    }
  },
  "timestamp": "2026-05-10T09:30:00+08:00",
  "update_interval": "10分钟"
}
```

## 配置步骤

### 1. 配置 GitHub Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 添加：

| Secret 名称 | 值 |
|-------------|-----|
| `CLAW_SESS` | 浏览器登录后 F12 → Console → `document.cookie` 中的 CLAW_SESS 值 |

### 2. 启用 GitHub Pages

仓库 Settings → Pages → Source 选 **GitHub Actions**

### 3. Workflow 自动运行

- 每 10 分钟自动抓取一次
- 生成 `invites_api.json` 和 `invites_report.md`
- 可在 Actions 页面手动触发

## 本地测试

```bash
# 安装依赖
pip install requests

# 将 Cookie 写入 .cookie 文件
echo "你的CLAW_SESS值" > .cookie

# 运行生成脚本
python generate_api.py
```

> ⚠️ Cookie 会过期，过期后需要在浏览器重新登录获取新的 Cookie 更新 GitHub Secret。
