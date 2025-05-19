#!/usr/bin python3
# ping_test.py

import subprocess
import re
import sys
from typing import List, Tuple

# 配置参数
PING_COUNT = 4      # 每个IP的ping次数
TIMEOUT_PER_PING = 2  # 单次ping超时时间（秒）
IP_FILE = "github_ips.txt"
OUTPUT_FILE = "ping_results.txt"

def parse_ping(output: str) -> Tuple[float, float]:
    """解析ping命令输出，返回 (丢包率, 平均延迟)"""
    packet_loss = 100.0
    avg_latency = 9999.0

    # 匹配丢包率模式
    loss_match = re.search(r"(\d+)% packet loss", output)
    if loss_match:
        packet_loss = float(loss_match.group(1))

    # 匹配延迟统计模式
    latency_match = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/", output)
    if latency_match:
        avg_latency = float(latency_match.group(1))

    return packet_loss, avg_latency

def ping_ip(ip: str) -> Tuple[float, float]:
    """执行ping命令并返回结果"""
    try:
        result = subprocess.run(
            ["ping", "-c", str(PING_COUNT), "-W", str(TIMEOUT_PER_PING), ip],
            capture_output=True,
            text=True,
            timeout=PING_COUNT * (TIMEOUT_PER_PING + 1),  # 总超时时间
            check=True
        )
        return parse_ping(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return (100.0, 9999.0)

def main():
    # 读取IP列表
    try:
        with open(IP_FILE) as f:
            ips = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"错误：找不到文件 {IP_FILE}")
        sys.exit(1)

    results = []
    
    # 执行ping测试
    for ip in ips:
        print(f"测试 {ip}...", end=" ", flush=True)
        loss, latency = ping_ip(ip)
        results.append((ip, loss, latency))
        print("完成")

    # 按丢包率（升序）和延迟（升序）排序
    sorted_results = sorted(results, key=lambda x: (x[1], x[2]))

    # 写入文件
    with open(OUTPUT_FILE, "w") as f:
        for ip, loss, latency in sorted_results:
            f.write(f"{ip}\t{loss:.1f}%\t{latency:.1f} ms\n")

    # 打印格式化结果
    print("\n===== 最佳IP排序（丢包率 ↑ -> 延迟 ↓）=====")
    print(f"{'IP':<16} {'丢包率':<8} {'平均延迟':<10}")
    for ip, loss, latency in sorted_results:
        print(f"{ip:<16} {loss:>6.1f}% {latency:>9.1f} ms")

if __name__ == "__main__":
    main()