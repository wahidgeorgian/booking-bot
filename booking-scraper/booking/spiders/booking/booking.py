from scrapy import Spider
from scrapy import Request

from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time


class BookingSpider(Spider):
    name = "booking"
    start_urls = ["https://www.booking.com/"]
    driver = None

    def parse(self, response):
        # urls_list = []
        cities = ["Riyadh"]
        for city in cities:
            urls_list = []
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-geolocation")
            options.page_load_strategy = "normal"
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            self.driver.get(self.start_urls[0])
            self.driver.implicitly_wait(5)

            try:
                popup_xpath = "//button[@class='a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 deab83296e f4552b6561']"
                popup = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, popup_xpath))
                )
                popup.click()
            except Exception as e:
                print(e)
                pass
            self.driver.implicitly_wait(5)
            place = self.driver.find_element(By.CLASS_NAME, "eb46370fe1")
            place.send_keys(city)
            time.sleep(5)
            search_xpath = "//button[@class='a83ed08757 c21c56c305 a4c1805887 f671049264 d2529514af c082d89982 cceeb8986b']"
            search = self.driver.find_element(By.XPATH, search_xpath)
            search.click()
            self.driver.implicitly_wait(2000)

            four_star_xpath = "(//div[@data-filters-item='class:class=4']/input)[1]"
            fourstars = self.driver.find_element(By.XPATH, four_star_xpath)
            fourstars.click()
            time.sleep(5)
            five_star_xpath = "(//div[@data-filters-item='class:class=5']/input)[1]"
            fivestar = self.driver.find_element(By.XPATH, five_star_xpath)
            fivestar.click()
            time.sleep(5)
            
            while True:
                try:
                    current_url = self.driver.current_url
                    urls_list.append(current_url)
                    print(f"Current URL: {current_url}")

                    next_page = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[@aria-label='Next page']")
                        )
                    )
                    next_page.click()
                except TimeoutException:
                    print(
                        "TimeoutException: Unable to find the 'Next page' button or it is not clickable."
                    )
                    break
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    break
            self.driver.quit()

            for url in urls_list:
                yield Request(url=url, callback=self.parse_items, dont_filter=True)

    def parse_items(self, response):
        for item in response.xpath("//div[@class='c066246e13']"):
            hotel_name = item.xpath(".//h3/a/div[@data-testid='title']/text()").get()
            hotel_url = item.xpath(".//h3/a/@href").get()
            neighbourhood_name = ""
            neighbourhood = item.xpath(".//span[@data-testid='address']/text()").get()
            if neighbourhood != "Riyadh":
                neighbourhood_name = neighbourhood.split(",")[0]
            place = neighbourhood.split(",")[-1]
            yield Request(
                url=hotel_url,
                callback=self.parse_hotel,
                meta={
                    "hotel_name": hotel_name,
                    "place": place,
                    "neighbourhood_name": neighbourhood_name,
                },
            )

    def parse_hotel(self, response):
        hotel_name = response.meta["hotel_name"]
        place = response.meta["place"]
        neighbourhood_name = response.meta["neighbourhood_name"]
        Loyality_Program_Group = ""
        loyality = response.xpath(
            "//p[@class ='summary hotel_meta_style']/text()"
        ).get()
        if loyality:
            Loyality_Program_Group = loyality.split(":")[-1].strip()
        yield {
            "Hotel Name": hotel_name,
            "Area": place,
            "Neighbourhood Name": neighbourhood_name,
            "Loyality Program Group": Loyality_Program_Group,
        }
