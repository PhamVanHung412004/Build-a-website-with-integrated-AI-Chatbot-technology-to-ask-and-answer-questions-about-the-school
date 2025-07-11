import asyncio
from btec_crawler import BTECCrawler

async def main():
    # Sử dụng cấu hình mặc định
    async with BTECCrawler() as crawler:
        report = await crawler.crawl_website()
        print(f"Đã crawl {report['summary']['total_pages_crawled']} trang")

if __name__ == "__main__":
    asyncio.run(main())
