# ClawEmail 邀请码监控

自动从 [ClawEmail](https://claw.163.com) 获取邀请码，区分**待使用**和**已使用**状态，并提供多种预过滤的 API 接口。

## 架构

```
GitHub Actions (每10分钟)
    │
    ▼
generate_api.py ──→ invites_api.json        ──→ GitHub Pages Web 页面
                    invites_api_getone.json  ──→ 取1个待使用邀请码
                    invites_api_unused.json  ──→ 仅待使用（卡片格式）
                    invites_api_card.json    ──→ 全部（卡片格式）
                    invites_api_used.json    ──→ 已使用
                    invites_report.md        ──→ Markdown 报告
                              │
                              └──→ raw.githubusercontent.com (外部程序调用的 API 端点)
```

## API 地址

推送代码到 GitHub 后可用。选择适合你场景的接口：

| 场景 | API 地址 |
|------|----------|
| ✅ **取1个待使用邀请码** | `https://raw.githubusercontent.com/fengmas/clawemail/main/invites_api_getone.json` |
| 仅待使用（卡片列表） | `https://raw.githubusercontent.com/fengmas/clawemail/main/invites_api_unused.json` |
| 全部（卡片列表） | `https://raw.githubusercontent.com/fengmas/clawemail/main/invites_api_card.json` |
| 已使用 | `https://raw.githubusercontent.com/fengmas/clawemail/main/invites_api_used.json` |
| 全部（完整数据） | `https://raw.githubusercontent.com/fengmas/clawemail/main/invites_api.json` |
| Web 监控页面 | `https://fengmas.github.io/clawemail/` |

## API 响应格式

### `invites_api_getone.json` — 取1个待使用邀请码（最常用 ⭐）

```json
{
  "code": 200,
  "success": true,
  "message": "success",
  "data": {
    "code": "CLAWE776C1CAC8B1",
    "available": true,
    "total_unused": 5
  },
  "timestamp": "2026-05-10T10:18:47+08:00"
}
```

直接取 `data.code` 即为可用的邀请码，`data.available` 判断是否还有余量。

### `invites_api_unused.json` — 仅待使用

```json
{
  "code": 200,
  "success": true,
  "message": "success",
  "data": {
    "cards": [
      { "code": "CLAWE776C1CAC8B1", "status": "unused", "status_text": "待使用" },
      { "code": "CLAWCCDA0930083F", "status": "unused", "status_text": "待使用" }
    ],
    "total": 5,
    "returned": 5
  },
  "timestamp": "2026-05-10T10:18:47+08:00"
}
```

### `invites_api.json` — 完整数据

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

> ⚠️ 数据中**不包含任何账号个人信息**（不包含用户名、邮箱等），可放心公开使用。

## 配置步骤

### 1. 将仓库设为公开（必须）

仓库 Settings → Danger Zone → Change visibility → **Public**

这是为了让 `raw.githubusercontent.com` 能正常返回数据。

### 2. 配置 GitHub Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 添加：

| Secret 名称 | 值 |
|-------------|-----|
| `CLAW_SESS` | 浏览器登录后 F12 → Console → `document.cookie` 中的 CLAW_SESS 值 |

### 3. 启用 GitHub Pages

仓库 Settings → Pages → Source 选 **GitHub Actions**

### 4. Workflow 自动运行

- 每 10 分钟自动抓取一次
- 生成 5 个预过滤的 JSON 文件 + Markdown 报告
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