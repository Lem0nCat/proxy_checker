import re
import argparse
from ipaddress import ip_address, IPv4Address, IPv6Address

def is_valid_ip(ip):
    try:
        return isinstance(ip_address(ip), (IPv4Address, IPv6Address))
    except ValueError:
        return False

def is_valid_port(port):
    try:
        return 1 <= int(port) <= 65535
    except ValueError:
        return False

def extract_proxies(line):
    # Ищем все совпадения IP:PORT с разными разделителями
    patterns = [
        r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3}|\[?[0-9a-fA-F:]+\]?)'  # IPv4/IPv6
        r'[:#]'                                                  # разделитель
        r'(?P<port>\d{1,5})'                                     # порт
    ]
    
    proxies = set()
    for pattern in patterns:
        matches = re.finditer(pattern, line)
        for match in matches:
            ip = match.group('ip').strip('[]')
            port = match.group('port')
            
            if is_valid_ip(ip) and is_valid_port(port):
                proxies.add(f"{ip}:{port}")
    
    return proxies

def process_file(input_file, output_file):
    found_proxies = set()
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    found_proxies.update(extract_proxies(line))
                    
    except FileNotFoundError:
        print(f"Ошибка: Файл {input_file} не найден")
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for proxy in sorted(found_proxies):
            f.write(f"{proxy}\n")
    
    print(f"Найдено прокси: {len(found_proxies)}")
    print(f"Результат сохранен в: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Фильтр IP:PORT из текстового файла')
    parser.add_argument('input', help='Входной файл')
    parser.add_argument('output', help='Выходной файл')
    args = parser.parse_args()
    
    process_file(args.input, args.output)