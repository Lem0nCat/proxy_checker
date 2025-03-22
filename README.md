
# Proxy Tools Suite

## 1. Proxy Checker (proxy_checker.py)

### Automated Proxy Validation and Testing Tool

#### Features
- Automatically detects proxy type (HTTP/SOCKS4/SOCKS5)
- Supports IP:PORT input format
- Speed testing with latency measurement
- AsyncIO implementation for high-performance checking
- Progress bar visualization
- Sorting by connection speed
- Duplicate removal
- Supports IPv4 and IPv6 addresses

#### Installation
```bash
pip install aiohttp aiohttp-socks tqdm
```

#### Usage
```bash
python proxy_checker.py -i input.txt -o results.txt -t 15 -m 200
```

**Arguments**:
- `-i/--input-file`: Input file with proxies (IP:PORT format)
- `-o/--output-file`: Output file (default: working_proxies.txt)
- `-t/--timeout`: Connection timeout in seconds (default: 10)
- `-m/--max-connections`: Maximum concurrent connections (default: 100)

#### Input Format
```
188.125.169.67:8080
203.19.38.114:1080
92.222.153.172:4145
```

#### Output Format
```
http://188.125.169.67:8080
socks5://203.19.38.114:1080
socks4://92.222.153.172:4145
```

---

## 2. Proxy Extractor (proxy_filter.py)

### Text Filter for IP:PORT Patterns

#### Features
- Extracts proxies from messy/unstructured text
- Supports multiple formats and separators (: or #)
- Validates IP addresses and port numbers
- Removes duplicates
- Preserves original case
- Handles both IPv4 and IPv6 addresses
- Error-tolerant reading

#### Requirements
- Python 3.6+ (no additional dependencies)

#### Usage
```bash
python proxy_filter.py input.txt cleaned_proxies.txt
```

**Arguments**:
- `input`: Path to messy input file
- `output`: Path for cleaned output file

#### Supported Patterns
```
Valid examples:
192.168.1.1:8080
2001:db8::1#1234
[2001:db8::1]:8080
127.0.0.1#54321
```

#### Output Features
- Sorted list of unique proxies
- Standardized IP:PORT format
- Validated addresses and ports
- Clean UTF-8 encoding

---

## Combined Workflow

1. **Extract proxies** from raw data:
```bash
python proxy_filter.py raw_data.txt potential_proxies.txt
```

2. **Check and classify** working proxies:
```bash
python proxy_checker.py -i potential_proxies.txt -o working_proxies.txt
```

3. Use cleaned, verified proxies in your applications:
```
http://12.34.56.78:8080
socks5://[2001:db8::1]:1080
```
