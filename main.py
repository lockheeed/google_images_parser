from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import shutil
import requests
import time
import os
import secrets


def Banner():
    os.system("cls")
    print(r"""  ________                     .__           __________
 /  _____/  ____   ____   ____ |  |   ____   \______   \_____ _______  ______ ___________
/   \  ___ /  _ \ /  _ \ / ___\|  | _/ __ \   |     ___/\__  \\_  __ \/  ___// __ \_  __ \
\    \_\  (  <_> |  <_> ) /_/  >  |_\  ___/   |    |     / __ \|  | \/\___ \\  ___/|  | \/
 \______  /\____/ \____/\___  /|____/\___  >  |____|    (____  /__|  /____  >\___  >__|
        \/             /_____/           \/                  \/           \/     \/
 [ * ] https://github.com/lockheeed""")


class Parser(object):
    def update_driver(self):
        chrome_options = Options()
        chrome_options.headless = True
        chrome_options.add_argument("--ignore-certificate-error")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")

        self.driver = webdriver.Chrome(options=chrome_options)

    def __get_images_by_query(self, query, scroll_times):
        start_time = time.time()

        query_link = f"https://www.google.com/search?q={query.replace(' ', '+')}&safe=off&espv=2&biw=1599&bih=726&source=lnms&tbm=isch&sa=X"

        self.driver.get(query_link)
        self.__scroll(scroll_times)

        images_table = []

        ISV_R = self.driver.find_elements_by_class_name("isv-r")
        for element in ISV_R:
            print(f"\r [ ~ ] Processing images table...{round(ISV_R.index(element)/len(ISV_R)*100, 2)}%", end="", flush=True)
            try:
                element.find_element_by_class_name("islib").click()
                soup = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')

                if soup.span.text != "Товар":
                    try:
                        images_table.append(soup.a['href'])
                    except KeyError:
                        pass

            except Exception:
                pass
        print(f"\r [ ~ ] Processing images table...COMPLETED")
        print(f" [ + ] Images table Processing completed in: {time.time() - start_time}. Total images parsed: {len(images_table)}\n")

        images = []

        for link_part in images_table:
            print(f"\r [ ~ ] Parsing images links...{round((images_table.index(link_part)/len(images_table))*100, 2)}%", end="")
            page = requests.get("https://google.com" + link_part).text
            try:
                images.append(page.split("var imageUrl='")[1].split("'")[0])
            except IndexError:
                pass
        print(f"\r [ ~ ] Parsing images links...COMPLETED\n", end="\n")
        return images

    def __scroll(self, scroll_times):
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(scroll_times):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scrape(self, query, scroll_times, close_driver=False):
        self.update_driver()
        images_urls = self.__get_images_by_query(query, scroll_times)

        if os.path.isdir('images'):
            shutil.rmtree('images')
        os.mkdir('images')

        for url in images_urls:
            print(f"\r [ ~ ] Downloading images...{round(images_urls.index(url)/len(images_urls)*100, 2)}", end="", flush=True)
            images_format = ["jpg", "jpeg", "png", "gif", "bmp", "raw"]
            if url.split(".")[-1] not in images_format:
                continue

            try:
                image = requests.get(url, stream=True).content
            except Exception:
                pass
            else:
                if len(image) > 4096:
                    with open(f'images/{secrets.token_hex(12)}.{url.split(".")[-1]}', 'wb') as f:
                        f.write(image)
                        f.close()

        print("\r [ ~ ] Downloading images...COMPLETED")

        if close_driver:
            self.driver.close()


if __name__ == '__main__':
    Banner()
    parser = Parser()
    parser.update_driver()

    query = input(" [ >> ] Enter searching query: ")
    scroll_times = int(input(" [ >> ] Enter page's scroll count: "))

    parser.scrape(query, scroll_times, close_driver=True)
