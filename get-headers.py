import os
import sys
import time
import threading
import shutil
import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://developer.limneos.net/index.php'
HEADER_URL = 'http://developer.limneos.net/headers'

def generate_headers(version: str):
    if not os.path.exists(version):
        os.mkdir(version)

    ios_param = '?ios='
    response = requests.get(BASE_URL + ios_param + version)
    soup = BeautifulSoup(response.content, 'html.parser')
    framework_links = soup.find(id='container').find_all('a')
    # cont = False
    for framework_link in framework_links:
        # if framework_link.text.strip() == 'VideoSubscriberAccount':
        #     cont = True

        # if not cont:
        #     continue

        print(' Getting headers for framework: '  + framework_link.text.strip())

        framework_dir = os.path.join(version, framework_link.text.strip())
        if not os.path.exists(framework_dir):
            os.mkdir(framework_dir)

        framework_url = BASE_URL + framework_link['href']
        framework_name = framework_link.text.strip()
        if framework_name != 'SpringBoard':
            framework_name += '.framework'

        response = requests.get(framework_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        header_links = soup.find(id='container').find_all('a')
        for header_link in header_links:
            header_file_name = header_link.text.strip()
            header_file_url = f'{HEADER_URL}/{version}/{framework_name}/Headers/{header_file_name}'
            # response = requests.get(BASE_URL + header_link['href'])
            # soup = BeautifulSoup(response.content, 'html.parser')
            response = requests.get(header_file_url);
            with open(os.path.join(framework_dir, header_link.text.strip()), 'w') as fp:
                # fp.write(soup.find('pre').text)
                fp.write(response.text)

def animated_loading():
    chars = r'/—\|'
    for char in chars:
        sys.stdout.write('\r' + 'Downloading headers ' + char)
        time.sleep(.1)
        sys.stdout.flush()


if __name__ == "__main__":
    try:
        r = requests.get(BASE_URL)
        current_version = r.url.split('ios=')[-1]

        home_soup = BeautifulSoup(r.content, 'html.parser')
        version_links = home_soup.find(
            'span', {'class': 'indexText'}).find_all('a')
        version_list = [link.text.strip() for link in version_links]
        version_list.insert(0, current_version)
        print(f"💡 Available versions: {', '.join(version_list)}")

        while 1:
            input_version = input('iOS version: ')
            if input_version and input_version.strip() in version_list:
                break

            print(f'❌ Version "{input_version}" not available')

        if os.path.exists(input_version):
            reply = input(f'⚠️ "{input_version}" directory already exists. Overwrite? [y/n] (Default: n): ')
            if reply != 'y':
                exit(1)

            shutil.rmtree(input_version)

        process = threading.Thread(target=generate_headers, args=(input_version,))
        process.start()
        while process.isAlive():
            animated_loading()

    except KeyboardInterrupt:
        exit(0)
