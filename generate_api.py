#!/usr/bin/env python3
"""
ClawEmail 邀请码 API 数据生成器
每 10 分钟由 GitHub Actions 自动运行
生成 invites_api.json 可通过 raw.githubusercontent.com 或 GitHub Pages 访问
"""

import os
import sys
import json
import hmac
import hashlib
from datetime import datetime, timezone, timedelta

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests

API_BASE = "https://claw.163.com/mailserv-claw-dashboard"
INVITES_API = f"{API_BASE}/api/v1/invites"
COOKIE_NAME = "CLAW_SESS"


TZ = timezone(timedelta(hours=8))


def get_cookie() -> str:
    cookie = os.environ.get("CLAW_SESS")
    if not cookie:
        cookie_file = os.path.join(os.path.dirname(__file__), ".cookie")
        if os.path.exists(cookie_file):
            with open(cookie_file) as f:
                cookie = f.read().strip()
    if not cookie:
        print("错误: 未找到 CLAW_SESS", file=sys.stderr)
        sys.exit(1)
    return cookie


def sign_data(data: dict, secret: str) -> str:
    if not secret:
        return ""
    sorted_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hmac.new(
        secret.encode("utf-8"),
        sorted_json.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def fetch_invites(cookie: str) -> dict:
    """仅获取邀请码数据，不获取账号个人信息"""
    session = requests.Session()
    session.trust_env = False
    session.headers.update({
        "Cookie": f"{COOKIE_NAME}={cookie}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    resp = session.get(INVITES_API, timeout=15, verify=False)
    data = resp.json()

    if not data.get("success"):
        raise Exception(f"API 请求失败: {data.get('message', '未知错误')}")

    return data



def format_api_data(raw_data: dict, api_token: str) -> dict:
    """格式化邀请码数据，不包含任何账号个人信息"""
    result = raw_data.get("result", [])
    unused = []
    used = []

    for item in result:
        if item["status"] == 0:
            unused.append({
                "code": item["code"],
                "status": "unused",
                "status_text": "待使用"
            })
        else:
            used.append({
                "code": item["code"],
                "status": "used",
                "status_text": "已使用",
                "used_by": item.get("inviteeEmailMasked", "未知"),
                "used_at": item.get("activeTime", "未知")
            })

    now = datetime.now(TZ)
    api_data = {
        "code": 200,
        "message": "success",
        "success": True,
        "data": {
            "summary": {
                "total": len(result),
                "unused": len(unused),
                "used": len(used)
            },
            "invites": {
                "unused": unused,
                "used": used
            }
        },
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "update_interval": "10分钟"
    }

    if api_token:
        api_data["signature"] = sign_data(api_data["data"], api_token)

    return api_data


def generate_markdown(api_data: dict) -> str:
    d = api_data["data"]
    s = d["summary"]
    unused = d["invites"]["unused"]
    used = d["invites"]["used"]

    lines = []
    lines.append("# ClawEmail 邀请码状态\n")
    lines.append(f"> 更新时间: {api_data['timestamp']}  |  更新间隔: {api_data['update_interval']}\n")
    lines.append("---\n")
    lines.append("## 统计\n")
    lines.append(f"- 总计: {s['total']} 个")
    lines.append(f"- 待使用: {s['unused']} 个")
    lines.append(f"- 已使用: {s['used']} 个\n")

    if unused:
        lines.append("## 待使用邀请码\n")
        lines.append("| 邀请码 |")
        lines.append("|--------|")
        for item in unused:
            lines.append(f"| `{item['code']}` |")
        lines.append("")

    if used:
        lines.append("## 已使用邀请码\n")
        lines.append("| 邀请码 | 被谁使用 | 使用时间 |")
        lines.append("|--------|----------|----------|")
        for item in used:
            lines.append(f"| `{item['code']}` | {item['used_by']} | {item['used_at']} |")
        lines.append("")

    lines.append("---\n")
    lines.append("_自动生成 | ClawEmail 邀请码监控_")
    return "\n".join(lines)


def main():
    cookie = get_cookie()
    api_token = os.environ.get("API_TOKEN", "")
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("正在获取邀请码数据...")
    raw_data = fetch_invites(cookie)

    print("生成 API 数据...")
    api_data = format_api_data(raw_data, api_token)

    json_path = os.path.join(base_dir, "invites_api.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    print(f"API 数据已写入: invites_api.json")

    md_path = os.path.join(base_dir, "invites_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown(api_data))
    print(f"报告已写入: invites_report.md")

    s = api_data["data"]["summary"]
    print(f"\n统计: 总计 {s['total']} | 待使用 {s['unused']} | 已使用 {s['used']}")



if __name__ == "__main__":
    main()
