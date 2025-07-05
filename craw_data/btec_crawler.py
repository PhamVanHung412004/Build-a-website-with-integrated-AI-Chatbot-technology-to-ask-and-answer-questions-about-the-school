import asyncio
import aiohttp
import logging
import json
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from dataclasses import dataclass, asdict
import re

# Third-party libraries
from bs4 import BeautifulSoup
import weasyprint
from weasyprint import HTML, CSS
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pdfkit
import requests
from playwright.async_api import async_playwright
import asyncpg
from urllib.robotparser import RobotFileParser

@dataclass
class PageContent:
    """Data class for storing page content and metadata"""
    url: str
    title: str
    content: str
    text_content: str
    links: List[str]
    pdf_links: List[str]
    images: List[str]
    metadata: Dict[str, any]
    timestamp: datetime
    content_type: str = "text/html"

class BTECCrawler:
    """
    Comprehensive web crawler for BTEC FPT website
    Handles Vietnamese content, multi-campus structure, PDF generation, and robust error handling
    """
    
    def __init__(self, config: Dict = None):
        """Initialize the crawler with configuration"""
        self.config = self._load_config(config)
        self.session = None
        self.browser = None
        self.playwright = None
        
        # URL management
        self.visited_urls: Set[str] = set()
        self.url_queue: List[str] = []
        self.failed_urls: List[Dict] = []
        self.pdf_urls: Set[str] = set()
        
        # Content management
        self.content_hashes: Set[str] = set()
        self.crawled_content: List[PageContent] = []
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Setup directories
        self._setup_directories()
        
        # Statistics
        self.stats = {
            'pages_crawled': 0,
            'pdfs_generated': 0,
            'pdfs_downloaded': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _load_config(self, config: Dict = None) -> Dict:
        """Load crawler configuration with defaults"""
        default_config = {
            'base_url': 'https://btec.fpt.edu.vn/',
            'max_concurrent_requests': 5,
            'delay_between_requests': 1.0,
            'max_retries': 3,
            'timeout': 30,
            'user_agent': 'BTEC-FPT-Crawler/1.0 (Educational Purpose)',
            'respect_robots_txt': True,
            'max_depth': 10,
            'output_dir': './btec_crawl_output',
            'pdf_engine': 'weasyprint',  # 'weasyprint', 'pdfkit', 'playwright'
            'include_images': True,
            'download_existing_pdfs': True,
            'languages': ['vi', 'en'],
            'campus_domains': ['btec.fpt.edu.vn'],
            'pdf_options': {
                'page_size': 'A4',
                'margin': '1in',
                'orientation': 'Portrait',
                'encoding': 'UTF-8'
            }
        }
        
        if config:
            default_config.update(config)
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('BTECCrawler')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/btec_crawler.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_directories(self):
        """Create necessary directories for output"""
        base_dir = Path(self.config['output_dir'])
        directories = [
            base_dir,
            base_dir / 'pages_pdf',
            base_dir / 'downloaded_pdfs',
            base_dir / 'images',
            base_dir / 'raw_html',
            base_dir / 'campus_hanoi',
            base_dir / 'campus_hcm',
            base_dir / 'campus_danang',
            base_dir / 'reports'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def __aenter__(self):
        """Async context manager entry"""
        # Initialize aiohttp session
        timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'User-Agent': self.config['user_agent']},
            connector=aiohttp.TCPConnector(limit=100)
        )
        
        # Initialize Playwright if needed
        if self.config['pdf_engine'] == 'playwright':
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to handle duplicates"""
        parsed = urlparse(url)
        
        # Remove session parameters and tracking codes
        query_params = parse_qs(parsed.query)
        filtered_params = {k: v for k, v in query_params.items() 
                          if k not in ['sessionid', 'utm_source', 'utm_medium', 'ref', 'fbclid']}
        
        normalized_query = urlencode(filtered_params, doseq=True)
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        if normalized_query:
            normalized_url += f"?{normalized_query}"
        
        return normalized_url.rstrip('/')
    
    def _is_duplicate_url(self, url: str) -> bool:
        """Check if URL has been visited"""
        normalized = self._normalize_url(url)
        return normalized in self.visited_urls
    
    def _is_duplicate_content(self, content: str) -> bool:
        """Check if content is duplicate using hash"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.content_hashes:
            return True
        self.content_hashes.add(content_hash)
        return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and within scope"""
        parsed = urlparse(url)
        
        # Check domain
        if not any(domain in parsed.netloc for domain in self.config['campus_domains']):
            return False
        
        # Skip certain file types
        skip_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.ico', '.xml', '.rss'}
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip admin/login pages
        skip_patterns = ['login', 'admin', 'logout', 'auth', 'signin', 'signup']
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        return True
    
    def _extract_campus_info(self, url: str) -> str:
        """Extract campus information from URL"""
        url_lower = url.lower()
        if 'hanoi' in url_lower or 'hn' in url_lower:
            return 'hanoi'
        elif 'hcm' in url_lower or 'hochiminh' in url_lower:
            return 'hcm'
        elif 'danang' in url_lower or 'dn' in url_lower:
            return 'danang'
        return 'general'
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _fetch_page(self, url: str) -> Tuple[str, int]:
        """Fetch page content with retry logic"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                return content, response.status
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            raise
    
    async def _extract_content(self, html: str, url: str) -> PageContent:
        """Extract content and metadata from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else urlparse(url).path
        
        # Extract main content
        content_selectors = [
            'main', '.content', '.main-content', '.page-content',
            '#content', '#main', 'article', '.article'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        # Clean content
        if main_content:
            # Remove scripts and styles
            for script in main_content.find_all(['script', 'style']):
                script.decompose()
            
            content_html = str(main_content)
            text_content = main_content.get_text().strip()
        else:
            content_html = html
            text_content = soup.get_text().strip()
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            if self._is_valid_url(absolute_url):
                links.append(absolute_url)
        
        # Extract PDF links
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                pdf_links.append(urljoin(url, href))
        
        # Extract images
        images = []
        if self.config['include_images']:
            for img in soup.find_all('img', src=True):
                src = img['src']
                absolute_url = urljoin(url, src)
                images.append(absolute_url)
        
        # Extract metadata
        metadata = {
            'description': '',
            'keywords': '',
            'author': '',
            'language': 'vi',
            'campus': self._extract_campus_info(url)
        }
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '')
        
        # Language detection
        html_lang = soup.find('html')
        if html_lang and html_lang.get('lang'):
            metadata['language'] = html_lang.get('lang')
        
        return PageContent(
            url=url,
            title=title_text,
            content=content_html,
            text_content=text_content,
            links=links,
            pdf_links=pdf_links,
            images=images,
            metadata=metadata,
            timestamp=datetime.now()
        )
    
    async def _generate_pdf_weasyprint(self, content: PageContent) -> bytes:
        """Generate PDF using WeasyPrint"""
        try:
            # Create HTML template
            html_template = f"""
            <!DOCTYPE html>
            <html lang="{content.metadata.get('language', 'vi')}">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{content.title}</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }}
                    .header {{
                        border-bottom: 2px solid #0066cc;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}
                    .title {{
                        color: #0066cc;
                        font-size: 24px;
                        font-weight: bold;
                        margin: 0;
                    }}
                    .url {{
                        color: #666;
                        font-size: 12px;
                        margin: 5px 0;
                    }}
                    .content {{
                        max-width: 100%;
                        overflow-wrap: break-word;
                    }}
                    .content img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 10px;
                        border-top: 1px solid #ccc;
                        font-size: 10px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1 class="title">{content.title}</h1>
                    <p class="url">URL: {content.url}</p>
                    <p class="url">Crawled: {content.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="content">
                    {content.content}
                </div>
                <div class="footer">
                    <p>Generated by BTEC FPT Crawler | Campus: {content.metadata.get('campus', 'general')}</p>
                </div>
            </body>
            </html>
            """
            
            # Generate PDF
            html_doc = HTML(string=html_template)
            pdf_bytes = html_doc.write_pdf()
            
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"Error generating PDF with WeasyPrint for {content.url}: {e}")
            raise
    
    async def _generate_pdf_playwright(self, content: PageContent) -> bytes:
        """Generate PDF using Playwright"""
        try:
            page = await self.browser.new_page()
            
            # Set content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{content.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
                    .content {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{content.title}</h1>
                    <p>URL: {content.url}</p>
                    <p>Generated: {content.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="content">
                    {content.content}
                </div>
            </body>
            </html>
            """
            
            await page.set_content(html_content, wait_until='networkidle')
            
            # Generate PDF
            pdf_bytes = await page.pdf(
                format='A4',
                margin={
                    'top': '1in',
                    'right': '1in',
                    'bottom': '1in',
                    'left': '1in'
                },
                print_background=True
            )
            
            await page.close()
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"Error generating PDF with Playwright for {content.url}: {e}")
            raise
    
    async def _generate_pdf(self, content: PageContent) -> bytes:
        """Generate PDF using configured engine"""
        if self.config['pdf_engine'] == 'weasyprint':
            return await self._generate_pdf_weasyprint(content)
        elif self.config['pdf_engine'] == 'playwright':
            return await self._generate_pdf_playwright(content)
        else:
            raise ValueError(f"Unknown PDF engine: {self.config['pdf_engine']}")
    
    def _save_pdf(self, pdf_bytes: bytes, filename: str, subfolder: str = '') -> str:
        """Save PDF to disk"""
        base_path = Path(self.config['output_dir'])
        
        if subfolder:
            save_path = base_path / subfolder
        else:
            save_path = base_path / 'pages_pdf'
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_filename = safe_filename[:200]  # Limit length
        
        if not safe_filename.endswith('.pdf'):
            safe_filename += '.pdf'
        
        file_path = save_path / safe_filename
        
        # Handle duplicate filenames
        counter = 1
        original_path = file_path
        while file_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            file_path = save_path / f"{stem}_{counter}{suffix}"
            counter += 1
        
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return str(file_path)
    
    async def _download_pdf(self, pdf_url: str) -> Optional[str]:
        """Download existing PDF files"""
        try:
            async with self.session.get(pdf_url) as response:
                if response.status == 200:
                    pdf_content = await response.read()
                    
                    # Generate filename from URL
                    filename = pdf_url.split('/')[-1]
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'
                    
                    # Save PDF
                    file_path = self._save_pdf(pdf_content, filename, 'downloaded_pdfs')
                    self.logger.info(f"Downloaded PDF: {pdf_url} -> {file_path}")
                    return file_path
                else:
                    self.logger.warning(f"Failed to download PDF {pdf_url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error downloading PDF {pdf_url}: {e}")
            return None
    
    async def _process_page(self, url: str, depth: int = 0) -> Optional[PageContent]:
        """Process a single page"""
        if depth > self.config['max_depth']:
            return None
        
        if self._is_duplicate_url(url):
            return None
        
        try:
            # Mark as visited
            self.visited_urls.add(self._normalize_url(url))
            
            # Fetch page
            html, status_code = await self._fetch_page(url)
            
            if status_code != 200:
                self.logger.warning(f"Non-200 status for {url}: {status_code}")
                return None
            
            # Extract content
            content = await self._extract_content(html, url)
            
            # Check for duplicate content
            if self._is_duplicate_content(content.text_content):
                self.logger.info(f"Duplicate content detected for {url}")
                return None
            
            # Generate PDF
            try:
                pdf_bytes = await self._generate_pdf(content)
                
                # Save PDF
                campus = content.metadata.get('campus', 'general')
                filename = f"{content.title}_{int(time.time())}"
                pdf_path = self._save_pdf(pdf_bytes, filename, f'campus_{campus}')
                
                self.logger.info(f"Generated PDF: {url} -> {pdf_path}")
                self.stats['pdfs_generated'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to generate PDF for {url}: {e}")
            
            # Download existing PDFs
            if self.config['download_existing_pdfs']:
                for pdf_url in content.pdf_links:
                    if pdf_url not in self.pdf_urls:
                        self.pdf_urls.add(pdf_url)
                        await self._download_pdf(pdf_url)
                        self.stats['pdfs_downloaded'] += 1
            
            # Add new URLs to queue
            new_urls = []
            for link in content.links:
                if not self._is_duplicate_url(link) and self._is_valid_url(link):
                    new_urls.append(link)
            
            self.url_queue.extend(new_urls)
            self.stats['pages_crawled'] += 1
            
            # Add delay between requests
            await asyncio.sleep(self.config['delay_between_requests'])
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error processing page {url}: {e}")
            self.stats['errors'] += 1
            self.failed_urls.append({
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return None
    
    async def _crawl_with_concurrency(self, urls: List[str]) -> List[PageContent]:
        """Crawl URLs with controlled concurrency"""
        semaphore = asyncio.Semaphore(self.config['max_concurrent_requests'])
        results = []
        
        async def crawl_single(url):
            async with semaphore:
                return await self._process_page(url)
        
        tasks = [crawl_single(url) for url in urls]
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in completed_results:
            if isinstance(result, PageContent):
                results.append(result)
        
        return results
    
    async def crawl_website(self, seed_urls: List[str] = None) -> Dict:
        """Main crawling method"""
        self.logger.info("Starting BTEC FPT website crawl...")
        self.stats['start_time'] = datetime.now()
        
        # Use default seed URLs if none provided
        if seed_urls is None:
            seed_urls = [
                self.config['base_url'],
                f"{self.config['base_url']}courses",
                f"{self.config['base_url']}site",
            ]
        
        # Initialize queue
        self.url_queue = list(seed_urls)
        processed_urls = set()
        
        try:
            while self.url_queue:
                # Get batch of URLs to process
                batch_size = min(self.config['max_concurrent_requests'], len(self.url_queue))
                batch_urls = []
                
                for _ in range(batch_size):
                    if self.url_queue:
                        url = self.url_queue.pop(0)
                        if url not in processed_urls:
                            batch_urls.append(url)
                            processed_urls.add(url)
                
                if not batch_urls:
                    continue
                
                # Process batch
                self.logger.info(f"Processing batch of {len(batch_urls)} URLs")
                batch_results = await self._crawl_with_concurrency(batch_urls)
                
                # Store results
                self.crawled_content.extend(batch_results)
                
                # Log progress
                self.logger.info(f"Progress: {len(processed_urls)} URLs processed, {len(self.url_queue)} remaining")
                
                # Safety check to prevent infinite crawling
                if len(processed_urls) > 1000:  # Adjust limit as needed
                    self.logger.warning("Reached maximum URL limit, stopping crawl")
                    break
        
        except KeyboardInterrupt:
            self.logger.info("Crawl interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error during crawl: {e}")
        finally:
            self.stats['end_time'] = datetime.now()
            
            # Generate final report
            report = await self._generate_report()
            return report
    
    async def _generate_report(self) -> Dict:
        """Generate comprehensive crawl report"""
        report = {
            'summary': {
                'total_pages_crawled': self.stats['pages_crawled'],
                'total_pdfs_generated': self.stats['pdfs_generated'],
                'total_pdfs_downloaded': self.stats['pdfs_downloaded'],
                'total_errors': self.stats['errors'],
                'crawl_duration': str(self.stats['end_time'] - self.stats['start_time']) if self.stats['end_time'] else 'N/A',
                'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else 'N/A',
                'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else 'N/A'
            },
            'campus_breakdown': {},
            'failed_urls': self.failed_urls,
            'content_summary': []
        }
        
        # Campus breakdown
        campus_stats = {}
        for content in self.crawled_content:
            campus = content.metadata.get('campus', 'general')
            if campus not in campus_stats:
                campus_stats[campus] = 0
            campus_stats[campus] += 1
        
        report['campus_breakdown'] = campus_stats
        
        # Content summary
        for content in self.crawled_content[:10]:  # Top 10 pages
            report['content_summary'].append({
                'url': content.url,
                'title': content.title,
                'campus': content.metadata.get('campus', 'general'),
                'timestamp': content.timestamp.isoformat()
            })
        
        # Save report
        report_path = Path(self.config['output_dir']) / 'reports' / f'crawl_report_{int(time.time())}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved to: {report_path}")
        return report

# Usage example and configuration
async def main():
    """Main function demonstrating usage"""
    
    # Configuration
    config = {
        'base_url': 'https://btec.fpt.edu.vn/',
        'max_concurrent_requests': 3,  # Be respectful to the server
        'delay_between_requests': 2.0,  # 2 seconds between requests
        'max_retries': 3,
        'timeout': 30,
        'output_dir': './btec_crawl_output',
        'pdf_engine': 'weasyprint',  # Options: 'weasyprint', 'playwright'
        'download_existing_pdfs': True,
        'max_depth': 5,
        'respect_robots_txt': True
    }
    
    # Seed URLs for different campus sections
    seed_urls = [
        'https://btec.fpt.edu.vn/',
        'https://btec.fpt.edu.vn/courses',
        'https://btec.fpt.edu.vn/site'
    ]
    
    # Run crawler
    async with BTECCrawler(config) as crawler:
        try:
            report = await crawler.crawl_website(seed_urls)
            print("\n" + "="*50)
            print("CRAWL COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Pages crawled: {report['summary']['total_pages_crawled']}")
            print(f"PDFs generated: {report['summary']['total_pdfs_generated']}")
            print(f"PDFs downloaded: {report['summary']['total_pdfs_downloaded']}")
            print(f"Errors: {report['summary']['total_errors']}")
            print(f"Duration: {report['summary']['crawl_duration']}")
            print("\nCampus breakdown:")
            for campus, count in report['campus_breakdown'].items():
                print(f"  {campus}: {count} pages")
            print(f"\nOutput directory: {config['output_dir']}")
            
        except Exception as e:
            print(f"Crawl failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())