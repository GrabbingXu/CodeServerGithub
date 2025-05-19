#!/usr/bin python3
# github_hosts.py

import subprocess
import re
import sys
import requests
from typing import List, Tuple, Dict
import questionary

# 配置参数
PING_COUNT = 4
TIMEOUT_PER_PING = 2
HOSTS_URL = "https://github-hosts.tinsfox.com/hosts"
HOSTS_PATH = "/etc/hosts"
MARKER_START = "# ===== GitHub Hosts Start ====="
MARKER_END = "# ===== GitHub Hosts End ====="

# ANSI 颜色代码
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_MAGENTA = "\033[95m"
COLOR_RED = "\033[91m"

# 丢包率着色方案
def get_loss_color(loss: float) -> str:
    if loss <= 0.1:
        return COLOR_GREEN
    elif loss <= 1.0:
        return COLOR_YELLOW
    elif loss <= 5.0:
        return COLOR_MAGENTA
    else:
        return COLOR_RED

# 网络延迟着色方案
def get_latency_color(latency: float) -> str:
    if latency <= 100:
        return COLOR_GREEN
    elif latency <= 1000:
        return COLOR_YELLOW
    elif latency <= 2000:
        return COLOR_MAGENTA
    else:
        return COLOR_RED

# 丢包率&网络延迟有效数字
def parse_ping(output: str) -> Tuple[float, float]:
    packet_loss = 100.0
    avg_latency = 9999.0

    loss_match = re.search(r"(\d+)% packet loss", output)
    if loss_match:
        packet_loss = float(loss_match.group(1))

    latency_match = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/", output)
    if latency_match:
        avg_latency = float(latency_match.group(1))

    return packet_loss, avg_latency

def ping_ip(ip: str) -> Tuple[float, float]:
    try:
        result = subprocess.run(
            ["ping", "-c", str(PING_COUNT), "-W", str(TIMEOUT_PER_PING), ip],
            capture_output=True,
            text=True,
            timeout=PING_COUNT * (TIMEOUT_PER_PING + 1),
            check=True
        )
        return parse_ping(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return (100.0, 9999.0)

def fetch_and_parse_hosts() -> List[Tuple[str, str]]:
    try:
        response = requests.get(HOSTS_URL)
        response.raise_for_status()
        entries = []
        for line in response.text.splitlines():
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                for domain in parts[1:]:
                    if domain != '#':
                        entries.append((ip, domain))
        return entries
    except requests.RequestException as e:
        print(f"获取 Hosts 文件失败: {e}")
        sys.exit(1)

def main():
    entries = fetch_and_parse_hosts()
    if not entries:
        print("未找到有效的 IP 和域名")
        sys.exit(1)

    # 提取唯一 IP 并测试
    unique_ips = {ip for ip, _ in entries}
    ip_results: Dict[str, Tuple[float, float]] = {}
    for ip in unique_ips:
        print(f"测试 {ip}...", end=" ", flush=True)
        loss, latency = ping_ip(ip)
        ip_results[ip] = (loss, latency)
        print("完成")

    # 关联结果
    results = []
    for ip, domain in entries:
        loss, latency = ip_results.get(ip, (100.0, 9999.0))
        results.append((ip, domain, loss, latency))

    # 排序：丢包率 ↑，延迟 ↑
    sorted_results = sorted(results, key=lambda x: (x[2], x[3]))

    # 打印彩色结果
    print("\n===== 最佳 IP 排序（丢包率 ↑ -> 延迟 ↑）=====")
    print(f"{'IP':<16} {'域名':<30} {'丢包率':<8} {'平均延迟':<10}")
    for ip, domain, loss, latency in sorted_results:
        loss_color = get_loss_color(loss)
        latency_color = get_latency_color(latency)
        print(
            f"{ip:<16} {domain:<30} "
            f"{loss_color}{loss:>6.1f}%{COLOR_RESET} "
            f"{latency_color}{latency:>9.1f} ms{COLOR_RESET}"
        )

    # 图例
    print("\n图例：")
    print(f"{COLOR_GREEN}绿色[优秀]{COLOR_RESET} {COLOR_YELLOW}黄色[良好]{COLOR_RESET} "
        f"{COLOR_MAGENTA}品红色[一般]{COLOR_RESET} {COLOR_RED}红色[差劲]{COLOR_RESET}")

    # 询问是否更新 Hosts
    update = questionary.confirm("是否更新 Hosts 文件？").ask()
    if not update:
        sys.exit(0)

    # 读取现有 Hosts
    try:
        with open(HOSTS_PATH, 'r') as f:
            hosts_content = f.read().splitlines()
    except PermissionError:
        print("错误：需要 sudo 权限访问 Hosts 文件")
        sys.exit(1)

    # 查找标记位置
    try:
        start_idx = hosts_content.index(MARKER_START)
        end_idx = hosts_content.index(MARKER_END)
    except ValueError:
        start_idx = end_idx = None

    # 用户选择激活条目
    choices = [
        questionary.Choice(
            title=f"{ip} {domain} [{loss:.1f}%] [{latency:.1f}ms]",
            value=(ip, domain)
        ) for ip, domain, loss, latency in sorted_results
    ]
    selected = questionary.checkbox("选择要激活的条目（空格选择，回车确认）:", choices=choices).ask()

    # 生成新内容
    new_lines = [MARKER_START]
    for ip, domain, _, _ in sorted_results:
        if (ip, domain) in selected:
            new_lines.append(f"{ip} {domain}")
        else:
            new_lines.append(f"# {ip} {domain}")
    new_lines.append(MARKER_END)

    # 合并内容
    if start_idx is not None and end_idx is not None:
        final_content = hosts_content[:start_idx] + new_lines + hosts_content[end_idx+1:]
    else:
        final_content = hosts_content + [''] + new_lines

    # 预览
    print("\n===== 新的 Hosts 内容预览 =====")
    print('\n'.join(new_lines))

    # 确认写入
    confirm = questionary.confirm("确认更新吗？").ask()
    if not confirm:
        print("操作取消")
        sys.exit(0)

    # 写入文件（需要 sudo）
    try:
        # 尝试直接写入
        with open(HOSTS_PATH, 'w') as f:
            f.write('\n'.join(final_content))
    except PermissionError:
        # 若失败，使用 sudo 重试
        try:
            subprocess.run(
                ["sudo", "tee", HOSTS_PATH],
                input='\n'.join(final_content).encode(),
                check=True
            )
            print("\nHosts 文件已更新（通过 sudo）")
        except subprocess.CalledProcessError:
            print(f"{COLOR_RED}错误：sudo 权限被拒绝{COLOR_RESET}")
            sys.exit(1)

if __name__ == "__main__":
    main()