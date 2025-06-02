import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin
import argparse
import sys
import csv
from datetime import datetime

class GooglePatentDownloader:
    def __init__(self):
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
        self.base_url = "https://patents.google.com/patent/"
        self.downloaded_patents = []  # Store downloaded patent information
    
        # Create directories if they don't exist
        for directory in ['patents', 'reports']:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def check_existing_files(self, patent_number):
        """
        Check if the patent files already exist
        
        Args:
            patent_number (str): The patent number to check
        Returns:
            tuple: (bool, bool) - (pdf_exists, info_exists)
        """
        pdf_path = os.path.join('patents', f"{patent_number}.pdf")
        info_path = os.path.join('patents', f"{patent_number}_info.txt")
        
        pdf_exists = os.path.exists(pdf_path)
        info_exists = os.path.exists(info_path)
        
        if pdf_exists:
            # Verify PDF file is not empty or corrupted
            try:
                file_size = os.path.getsize(pdf_path)
                if file_size < 1024:  # If file is smaller than 1KB, consider it invalid
                    pdf_exists = False
                    os.remove(pdf_path)  # Remove invalid file
                    print(f"Removed invalid PDF file: {pdf_path}")
            except OSError:
                pdf_exists = False
        
        return pdf_exists, info_exists
    
    def read_existing_info(self, patent_number):
        """
        Read existing patent information from file
        
        Args:
            patent_number (str): The patent number to read
            
        Returns:
            dict: Patent information if exists, None otherwise
        """
        info_path = os.path.join('patents', f"{patent_number}_info.txt")
        try:
            patent_info = {'patent_number': patent_number}
            with open(info_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 使用更安全的方式提取信息
                def extract_field(pattern, default='N/A'):
                    match = re.search(pattern, content)
                    return match.group(1) if match else default
                
                # 提取各个字段
                patent_info['title'] = extract_field(r'Title: (.+)')
                patent_info['filing_date'] = extract_field(r'Filing Date: (.+)')
                patent_info['publication_date'] = extract_field(r'Publication Date: (.+)')
                
                # 处理发明人
                inventors_match = re.search(r'Inventors: (.+)', content)
                patent_info['inventors'] = (
                    inventors_match.group(1).split(', ') if inventors_match 
                    else []
                )
                
                # 处理摘要 - 使用更宽松的模式
                abstract_match = re.search(r'Abstract:\n([\s\S]+)$', content)
                patent_info['abstract'] = (
                    abstract_match.group(1).strip() if abstract_match 
                    else 'N/A'
                )
                
                return patent_info
                
        except Exception as e:
            print(f"Error reading existing info file for {patent_number}: {str(e)}")
            print("Will download fresh information.")
            return None
    
    def download_pdf(self, patent_number):
        """
        Download PDF version of the patent
        
        Args:
            patent_number (str): The patent number
        
        Returns:
            bool: True if download successful, False otherwise
        """
        # Check if PDF already exists
        pdf_exists, _ = self.check_existing_files(patent_number)
        if pdf_exists:
            print(f">>>> PDF for patent {patent_number} already exists, skipping download.")
            return True
            
        try:
            # First get the patent page
            url = urljoin(self.base_url, patent_number)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Find PDF link
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_link = soup.find('a', {'href': re.compile(r'.*\.pdf$')})
            
            if not pdf_link:
                # Try alternative method - direct PDF URL construction
                pdf_url = f"https://patentimages.storage.googleapis.com/pdfs/{patent_number}.pdf"
            else:
                pdf_url = urljoin(url, pdf_link['href'])
            
            # Download PDF
            pdf_response = requests.get(pdf_url, headers=self.headers, stream=True)
            pdf_response.raise_for_status()
            
            pdf_path = os.path.join('patents', f"{patent_number}.pdf")
            
            # Save PDF file
            total_size = int(pdf_response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            print(f"Downloading PDF for {patent_number}...")
            with open(pdf_path, 'wb') as pdf_file:
                for chunk in pdf_response.iter_content(chunk_size=block_size):
                    if chunk:
                        pdf_file.write(chunk)
                        downloaded += len(chunk)
                        # Show download progress
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            sys.stdout.write(f"\rProgress: {percent:.1f}%")
                            sys.stdout.flush()
            
            print(f"\nPDF successfully downloaded to: {pdf_path}")
            return True
            
        except requests.RequestException as e:
            print(f"Error downloading PDF for patent {patent_number}: {str(e)}")
            return False

    def download_patent_info(self, patent_number):
        """
        Download patent information from Google Patents
        
        Args:
            patent_number (str): The patent number to download
        
        Returns:
            dict: Patent information including title, abstract, and other details
        """
        # Check if files already exist
        pdf_exists, info_exists = self.check_existing_files(patent_number)
        
        # If both files exist, try to read existing info
        if pdf_exists and info_exists:
            print(f"Patent {patent_number} files found, attempting to read existing information...")
            patent_info = self.read_existing_info(patent_number)
            if patent_info:
                print(f"Successfully read existing information for patent {patent_number}")
                self.downloaded_patents.append(patent_info)
                return patent_info
            else:
                print(f"Could not read existing information for patent {patent_number}, will download fresh data")
        
        url = urljoin(self.base_url, patent_number)
        
        try:
            print(f"Fetching information for patent {patent_number}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract patent information
            patent_info = {
                'patent_number': patent_number,
                'title': soup.find('span', {'itemprop': 'title'}).text.strip() if soup.find('span', {'itemprop': 'title'}) else 'N/A',
                'abstract': soup.find('div', {'class': 'abstract'}).text.strip() if soup.find('div', {'class': 'abstract'}) else 'N/A',
                'inventors': [inv.text.strip() for inv in soup.find_all('span', {'itemprop': 'inventor'})],
                'filing_date': soup.find('time', {'itemprop': 'filingDate'}).text if soup.find('time', {'itemprop': 'filingDate'}) else 'N/A',
                'publication_date': soup.find('time', {'itemprop': 'publicationDate'}).text if soup.find('time', {'itemprop': 'publicationDate'}) else 'N/A',
            }
            
            # Add to downloaded patents list
            self.downloaded_patents.append(patent_info)
            
            # Save metadata to file if it doesn't exist
            if not info_exists:
                self.save_patent_info(patent_info)
            
            # Download PDF if it doesn't exist
            if not pdf_exists:
                self.download_pdf(patent_number)
            
            return patent_info
            
        except requests.RequestException as e:
            print(f"Error downloading patent {patent_number}: {str(e)}")
            return None

    def save_patent_info(self, patent_info):
        """
        Save patent information to a text file
        
        Args:
            patent_info (dict): Patent information to save
        """
        filename = f"patents/{patent_info['patent_number']}_info.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Patent Number: {patent_info['patent_number']}\n")
            f.write(f"Title: {patent_info['title']}\n")
            f.write(f"Filing Date: {patent_info['filing_date']}\n")
            f.write(f"Publication Date: {patent_info['publication_date']}\n")
            f.write(f"Inventors: {', '.join(patent_info['inventors'])}\n")
            f.write(f"\nAbstract:\n{patent_info['abstract']}\n")
        
        print(f"Patent information saved to: {filename}")
    def generate_summary_report(self):
        """
        Generate a summary report of downloaded patents
        """
        if not self.downloaded_patents:
            print("No patents were downloaded.")
            return

        # Generate report filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'reports/patent_summary_{timestamp}.csv'
        report_file = f'reports/patent_summary.csv'
        
        # Write CSV report
        with open(report_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Patent Number', 'Publication Date', 'Abstract'])
            
            # Write patent information
            for patent in self.downloaded_patents:
                writer.writerow([
                    patent['patent_number'],
                    patent['publication_date'],
                    patent['abstract'].replace('\n', ' ')  # Remove newlines from abstract
                ])
        
        print(f"\nSummary report generated: {report_file}")

def read_patent_numbers_from_file(file_path):
    """
    Read patent numbers from a file
    
    Args:
        file_path (str): Path to the file containing patent numbers
    
    Returns:
        list: List of patent numbers
    """
    patent_numbers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Remove whitespace and skip empty lines
                patent_number = line.strip()
                if patent_number:
                    patent_numbers.append(patent_number)
        return patent_numbers
    except Exception as e:
        print(f"Error reading patent numbers from file: {str(e)}")
        return []

def main():
    # Check if input.txt exists
    default_input_file = 'input.txt'
    if os.path.exists(default_input_file) and len(sys.argv) == 1:  # No command line arguments provided
        print(f"Found {default_input_file}, using it as input...")
        patent_numbers = read_patent_numbers_from_file(default_input_file)
        if not patent_numbers:
            print("No valid patent numbers found in input.txt.")
            return
        delay = 2  # Default delay
    else:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Download patents from Google Patents')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--patents', nargs='+', help='One or more patent numbers to download')
        group.add_argument('--file', type=str, help='Path to file containing patent numbers (one per line)')
        parser.add_argument('--delay', type=int, default=2, help='Delay between downloads in seconds (default: 2)')
        
        # Parse arguments
        args = parser.parse_args()
        
        # Get list of patent numbers
        patent_numbers = []
        if args.patents:
            patent_numbers = args.patents
        elif args.file:
            patent_numbers = read_patent_numbers_from_file(args.file)
            if not patent_numbers:
                print("No valid patent numbers found in file.")
                return
        delay = args.delay
    
    print("Google Patent Downloader")
    print("-----------------------")
    
    downloader = GooglePatentDownloader()
    
    # Process each patent number
    for i, patent_number in enumerate(patent_numbers):
        print(f"\nProcessing patent {i+1} of {len(patent_numbers)}")
        patent_info = downloader.download_patent_info(patent_number)
        
        if patent_info:
            print(f"Successfully processed patent: {patent_info['title']}")
            print(f"Files in patents/ directory:")
            print(f"- {patent_number}.pdf")
            print(f"- {patent_number}_info.txt")
        
        # Add delay between downloads if there are more patents to process
        if i < len(patent_numbers) - 1:
            print(f"\nWaiting {delay} seconds before next patent...")
            time.sleep(delay)
    
    # Generate summary report
    downloader.generate_summary_report()

if __name__ == "__main__":
    main()