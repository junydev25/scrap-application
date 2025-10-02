import json
import os
import time

import psutil


def get_process_memory(pid):
    try:
        process = psutil.Process(pid)
        children = process.children(recursive=True)
        total_mem = process.memory_info().rss
        for child in children:
            try:
                total_mem += child.memory_info().rss
            except psutil.NoSuchProcess:
                pass
        return total_mem / (1024 * 1024)  # MB
    except psutil.NoSuchProcess:
        pass


def get_network_io():
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent + net_io.bytes_recv


def test(process, tool_name, base_path, pid):
    net_start = get_network_io()
    memory_start = get_process_memory(pid)

    op_start_time = time.time()

    process()

    memory_end = get_process_memory(pid)

    op_time = time.time() - op_start_time
    net_end = get_network_io()

    results = {
        "tool": tool_name,
        "operations_time": op_time,
        "memory_used": memory_end - memory_start,
        "max_memory": memory_end,
        "network_used": (net_end - net_start) / (1024 * 1024),
    }

    with open(base_path / f"logs/{tool_name}_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n[{tool_name} 성능]")
    print(f"작업 시간: {results['operations_time']:.3f}초")
    print(f"메모리: {results['memory_used']:.2f}MB")
    print(f"네트워크: {results['network_used']:.2f}MB")
