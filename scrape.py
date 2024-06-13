import requests
import os
from bs4 import BeautifulSoup


def scrape_img(manga_name, chap_no):

    # Get Entire HTML of the Chapter
    response = requests.get(f'https://www.mangaread.org/manga/{manga_name}/chapter-{chap_no}/')
    html = response.text
    soup = BeautifulSoup(html, 'lxml')

    # To Retrieve the first option (highest chapter avail)
    """
    max_chapter = soup.find('option', class_='short').text
    max_chapter = max_chapter.split('Chapter ')
    print(int(max_chapter[1]))
    """

    images = soup.find_all('img', class_='wp-manga-chapter-img')
    img_urls = [img['src'].strip() for img in images if 'src' in img.attrs]
    print(f'Starting Chapter {chap_no}')
    return img_urls






# Function to download and save images
def download_images(image_urls, manga_name, chapter):

    # Determine directory
    directory_path = os.path.join(manga_name, f'Chapter-{chapter}')

    # Create Determined Directory if not exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True) 

        # Chapter.no appends
        with open('martial-peak/success.txt', 'a') as f:
            f.write(f'Chapter-{chapter}:\n')

    # Save all the Url's in the list to the manga_name
    for i, url in enumerate(image_urls):

        response = requests.get(url)
        if response.status_code == 200:
            
            # Save path & file name
            image_path = os.path.join(directory_path, f'{manga_name}_{chapter}_pg{i+1}.png')

            if not os.path.exists(image_path):
                
                # Save image to the path
                with open(image_path, 'wb') as f:
                    f.write(response.content)

                # Logs(appends) all the success
                with open('martial-peak/success.txt', 'a') as f:
                    f.write(f'Page {i+1} Successfully downloaded {url}\n')

                # print(f'Successfully downloaded {url}')
            
            else: print(f'Already Exists {url}')

        else:
            
            # logs all the errors
            with open('martial-peak/failedlog.txt', 'a') as f:
                f.write(f'Error {url}\n page{i+1}')

            print(f'Failed to download {url}')


if __name__ == '__main__':

    start_ch = 2
    end_ch = 282
    
    for i in range(start_ch, end_ch):

        img_url_list = scrape_img('my-wife-is-from-a-thousand-years-ago', str(i))
        download_images(img_url_list, 'my-wife-is-from-a-thousand-years-ago', str(i))
