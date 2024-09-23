import requests
import os
import time
import re
import img2pdf
import shutil
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options

# Returns a list of links to the chapters
def getChapters(manga_name, Ch_Start, Ch_End):

    # Set up the Edge WebDriver
    options = Options()

    options.add_argument("--headless")  # Run in headless mode (no browser UI)
    options.add_argument("--disable-gpu")  # Disable GPU rendering for increased performance

    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)

    # Open the manga page
    url = f'https://www.mangaread.org/manga/{manga_name}/'
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    # Locate the "Show more" button by its class name and click it
    show_more_button = driver.find_element(By.CLASS_NAME, 'chapter-readmore')
    show_more_button.click()
    time.sleep(2)  # Give it a short pause to load new content

    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all chapters in the loaded page
    chapters = soup.find_all('li', class_='wp-manga-chapter')
    chapter_links = []


    # Loop through the chapters and print the title and link
    for chapter in chapters:
        ch_link = chapter.find('a')['href']
        nums = int(re.findall(r'\d+', ch_link)[0])

        if nums>=Ch_Start and nums<= Ch_End:
            chapter_links.append(ch_link)

    # Close the browser
    driver.quit()

    # print("Completed GetChapters Function!/n", chapter_links)
    chapter_links.reverse()

    return chapter_links

# Returns Urls for Images of a chapter
def scrape_img(ch_link):

    # Get Entire HTML of the Chapter
    response = requests.get(ch_link)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')

    images = soup.find_all('img', class_='wp-manga-chapter-img')

    img_urls = [img['src'].strip() for img in images if 'src' in img.attrs]
    print(f'Starting Chapter {re.findall(r'\d+', ch_link)[0]}')

    return img_urls

# Function to download and save images
def download_images(image_urls, manga_name, ch_link, base_dir):

    # Determine directory
    chFolder = f'Chapter-{ch_link.split('chapter-')[1].split('/')[0]}'
    manga_directory = os.path.join(base_dir, manga_name)
    directory_path = os.path.join(manga_directory, chFolder)


    # Create Determined Directory if not exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True) 


    # Save all the Url's in the list to the manga_name
    for i, url in enumerate(image_urls):

        response = requests.get(url)
        if response.status_code == 200:
            
            # Save path & file name
            image_path = os.path.join(directory_path, f'{manga_name}_{chFolder}_pg{i+1}.png')

            if not os.path.exists(image_path):
                
                # Save image to the path
                with open(image_path, 'wb') as f:
                    f.write(response.content)

            else: print(f'Already Exists {url}')
    print(f"Downloaded {chFolder}")

def convertPDF(mangaDirectory):
    chaptersList = os.listdir(mangaDirectory)
    
    for chapter in chaptersList:
        chapter_path = os.path.join(mangaDirectory, chapter)

        # Skip if chapter is not a directory
        if not os.path.isdir(chapter_path):
            continue

        if chapter + '.pdf' in chaptersList:
            continue
        
        # Gets List of all the images in the Chapter
        imgsDir = os.path.join(mangaDirectory, chapter)
        imgsList = os.listdir(imgsDir)

        # Ensure imgsList contains only files
        imgsList = [os.path.join(imgsDir, img) for img in imgsList if os.path.isfile(os.path.join(imgsDir, img))]

        # Sort images by page number
        imgsList.sort(key=lambda x: int(re.findall(r'\d+', x.split('_pg')[-1])[0]))

        # Convert images to PDF
        with open(os.path.join(mangaDirectory, f'{chapter}.pdf'), 'wb') as f:
            f.write(img2pdf.convert(imgsList))      #type: ignore
        
        # Delete the images and chapter directory
        shutil.rmtree(chapter_path)

        print(f'Converted {chapter} to PDF')

    print("Executed convertPDF Function")

if __name__ == '__main__':

    start_ch = 1
    end_ch = 269
    manga_name = 'a-returners-magic-should-be-special-manga'
    base_dir = 'C:/Users/user/Documents/Code/Projects/Project 03 - Manga Reader'

    # Get Links of all chapters
    links = getChapters(manga_name, start_ch, end_ch)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        for ch_link in links:
            img_url_list = scrape_img(ch_link)
            executor.submit(download_images, img_url_list, manga_name, ch_link, base_dir)

    print('Scrape Completed')

    convertPDF(os.path.join(base_dir, manga_name))
    print('Conversions Completed')
