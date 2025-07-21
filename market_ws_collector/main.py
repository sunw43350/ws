import asyncio
from connectors import ascendex

async def main():
    # 可传入 symbols 或使用默认 config.py 中配置
    connector = ascendex.Connector()
    await connector.run()

if __name__ == "__main__":
    asyncio.run(main())
