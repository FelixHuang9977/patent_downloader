import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin
import argparse
import sys

class GooglePatentDownloader:
    def __init__(self):
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
        self.base_url = "https://patents.google.com/patent/"
    
    def download_pdf(self, patent_number):
        """
        Download PDF version of the patent
        
    Args:
            patent_number (str): The patent number
        
        Returns:
            bool: True if download successful, False otherwise
        """
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
            
            # Create patents directory if it doesn't exist
            if not os.path.exists('patents'):
                os.makedirs('patents')
            
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
            
            # Save metadata to file
            self.save_patent_info(patent_info)
            
            # Download PDF
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
        if not os.path.exists('patents'):
            os.makedirs('patents')
            
        filename = f"patents/{patent_info['patent_number']}_info.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Patent Number: {patent_info['patent_number']}\n")
            f.write(f"Title: {patent_info['title']}\n")
            f.write(f"Filing Date: {patent_info['filing_date']}\n")
            f.write(f"Publication Date: {patent_info['publication_date']}\n")
            f.write(f"Inventors: {', '.join(patent_info['inventors'])}\n")
            f.write(f"\nAbstract:\n{patent_info['abstract']}\n")
        
        print(f"Patent information saved to: {filename}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download patents from Google Patents')
    parser.add_argument('patent_numbers', nargs='+', help='One or more patent numbers to download')
    parser.add_argument('--delay', type=int, default=2, help='Delay between downloads in seconds (default: 2)')
    
    # Parse arguments
    args = parser.parse_args()
    
    print("Google Patent Downloader")
    print("-----------------------")
    
    downloader = GooglePatentDownloader()
    
    # Process each patent number
    for i, patent_number in enumerate(args.patent_numbers):
        print(f"\nProcessing patent {i+1} of {len(args.patent_numbers)}")
        patent_info = downloader.download_patent_info(patent_number)
        
        if patent_info:
            print(f"Successfully downloaded patent: {patent_info['title']}")
            print(f"Files saved in patents/ directory:")
            print(f"- {patent_number}.pdf")
            print(f"- {patent_number}_info.txt")
        
        # Add delay between downloads if there are more patents to process
        if i < len(args.patent_numbers) - 1:
            print(f"\nWaiting {args.delay} seconds before next download...")
            time.sleep(args.delay)
if __name__ == "__main__":
    main()