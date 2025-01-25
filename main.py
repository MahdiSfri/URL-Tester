import pandas as pd
import os
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    """
    """
    parsed_url = urlparse(url)
    # حذف `/` از انتهای مسیر و نرمال‌سازی query و fragment
    normalized_path = parsed_url.path.rstrip('/')
    normalized_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        normalized_path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    return normalized_url

def test_links(csv_file_path, output_file_path):
    # بررسی وجود فایل CSV ورودی
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"فایل CSV ورودی یافت نشد: {csv_file_path}")
    
    if not os.path.dirname(output_file_path):
        output_file_path = os.path.join(os.getcwd(), output_file_path)
    
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    df = pd.read_csv(csv_file_path)
    
    failed_results = []
    
    with sync_playwright() as p:
        Chromium
        browser = p.chromium.launch(headless=True)  # headless=True برای اجرای بدون نمایش مرورگر
        context = browser.new_context()
        page = context.new_page()
        
        for index, row in df.iterrows():
            source_url = row['link']  
            expected_destination = row['jim'] 
            
            try:
                page.goto(source_url, wait_until="networkidle")
                final_url = page.url  # آدرس نهایی پس از ریدایرکت
                
                normalized_final_url = normalize_url(final_url)
                normalized_expected_destination = normalize_url(expected_destination)
                
                if normalized_final_url == normalized_expected_destination:
                    status = "Success"
                elif "404" in page.title().lower():
                    status = "Failed (404 Not Found)"
                else:
                    status = f"Failed (Final URL: {final_url})"
                
                if status != "Success":
                    failed_results.append({
                        'Source URL': source_url,
                        'Expected Destination': expected_destination,
                        'Final Destination': final_url,
                        'Status': status
                    })
                
                print(f"Tested: {source_url} -> {final_url} (Status: {status})")
            except Exception as e:
                failed_results.append({
                    'Source URL': source_url,
                    'Expected Destination': expected_destination,
                    'Final Destination': str(e),
                    'Status': 'Error'
                })
                print(f"Error testing {source_url}: {str(e)}")
        
        browser.close()
    
    failed_results_df = pd.DataFrame(failed_results)
    
    failed_results_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
    print(f"نتایج ناموفق در فایل {output_file_path} ذخیره شد.")

csv_file_path = '/home/jamshid/Mabani/input.csv'  # آدرس فایل CSV ورودی
output_file_path = 'failed_links.csv'  # آدرس فایل CSV خروجی (مسیر نسبی)

test_links(csv_file_path, output_file_path)
