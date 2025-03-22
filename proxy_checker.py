import argparse
import aiohttp
import asyncio
import socket
from tqdm import tqdm
from datetime import datetime
from aiohttp_socks import ProxyConnector, ProxyType

class ProxyChecker:
    def __init__(self, args):
        self.args = args
        self.working_proxies = []
        self.semaphore = asyncio.Semaphore(args.max_connections)
        self.progress = None
        self.checked = 0

    async def load_proxies(self):
        try:
            with open(self.args.input_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise Exception(f"File {self.args.input_file} not found")

        valid_proxies = []
        for proxy in proxies:
            if self.validate_proxy_format(proxy):
                valid_proxies.append(proxy)
        return valid_proxies

    def validate_proxy_format(self, proxy):
        if '://' in proxy:
            return False
        if proxy.count(':') != 1:
            return False
        ip, port = proxy.split(':', 1)
        try:
            socket.inet_aton(ip)
            if not 1 <= int(port) <= 65535:
                return False
            return True
        except (socket.error, ValueError):
            return False

    async def test_proxy_type(self, session, proxy, proxy_type):
        test_url = "http://httpbin.org/ip"
        connector_map = {
            'http': None,
            'socks4': ProxyConnector(proxy_type=ProxyType.SOCKS4, host=proxy.split(':')[0], port=int(proxy.split(':')[1])),
            'socks5': ProxyConnector(proxy_type=ProxyType.SOCKS5, host=proxy.split(':')[0], port=int(proxy.split(':')[1]))
        }

        start_time = datetime.now()
        try:
            if proxy_type == 'http':
                async with session.get(
                    test_url,
                    proxy=f"http://{proxy}",
                    timeout=self.args.timeout
                ) as response:
                    if response.status == 200:
                        return ('http', (datetime.now() - start_time).total_seconds())
            else:
                async with aiohttp.ClientSession(connector=connector_map[proxy_type]) as s:
                    async with s.get(
                        test_url,
                        timeout=self.args.timeout
                    ) as response:
                        if response.status == 200:
                            return (proxy_type, (datetime.now() - start_time).total_seconds())
        except Exception:
            return None

    async def check_proxy(self, proxy):
        async with aiohttp.ClientSession() as session:
            for proxy_type in ['http', 'socks5', 'socks4']:
                result = await self.test_proxy_type(session, proxy, proxy_type)
                if result:
                    return (proxy, result[0], result[1])
        return None

    async def run_checks(self, proxies):
        tasks = [self.check_proxy_wrapper(proxy) for proxy in proxies]
        self.progress = tqdm(total=len(tasks), desc="Checking proxies", unit="proxy")
        results = await asyncio.gather(*tasks)
        self.progress.close()
        
        self.working_proxies = [result for result in results if result]

    async def check_proxy_wrapper(self, proxy):
        async with self.semaphore:
            result = await self.check_proxy(proxy)
            self.progress.update(1)
            return result

    def save_results(self):
        if not self.working_proxies:
            print("No working proxies found")
            return

        # Сортировка по скорости
        self.working_proxies.sort(key=lambda x: x[2])
        
        with open(self.args.output_file, 'w') as f:
            for proxy, ptype, speed in self.working_proxies:
                f.write(f"{ptype}://{proxy}\n")
        
        print(f"\nFound {len(self.working_proxies)} working proxies")
        print(f"Results saved to {self.args.output_file}")

async def main():
    parser = argparse.ArgumentParser(description="Async Proxy Checker")
    parser.add_argument("-i", "--input-file", required=True, help="Input proxies file")
    parser.add_argument("-o", "--output-file", default="working_proxies.txt", help="Output file")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout in seconds")
    parser.add_argument("-m", "--max-connections", type=int, 
                      default=100, help="Max concurrent connections")
    
    args = parser.parse_args()
    
    checker = ProxyChecker(args)
    
    try:
        proxies = await checker.load_proxies()
        if not proxies:
            print("No valid proxies found in input file")
            return
            
        print(f"Loaded {len(proxies)} proxies for checking")
        await checker.run_checks(proxies)
        checker.save_results()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())