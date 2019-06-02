import subprocess
import re
import asyncio

mac_address = re.compile(
    rb'[1234567890abcdf]{2}-[1234567890abcdf]{2}-[1234567890abcdf]{2}-[1234567890abcdf]{2}-[1234567890abcdf]{2}-[1234567890abcdf]{2}')


async def get_mac_address(ip):
    p = await asyncio.create_subprocess_exec(
        'arp', '-a', ip,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, )

    stdout, stderr = await p.communicate()
    return mac_address.search(stdout).group(0).decode('charmap')


async def get_mac_address_in_thread(ip):
    def _arp_request():
        p = subprocess.run(['arp', '-a', ip], stdout=subprocess.PIPE)
        return p.stdout

    loop = asyncio.get_event_loop()
    out = await loop.run_in_executor(None, _arp_request)
    try:
        return mac_address.search(out).group(0).decode('charmap')
    except:
        return '00-00-00-00-00-00'


if __name__ == '__main__':
    _loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(_loop)
    # _loop = asyncio.get_event_loop()
    print(_loop.run_until_complete(get_mac_address_in_thread('192.168.0.92')))
