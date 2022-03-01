import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

HOST = os.environ["SCRAPING_TARGET_URL"]


def main():
    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    path = "/sp/restaurant/list/"
    target_date = "20220415"
    param = f"useDate={target_date}&" \
            f"mealDivInform=&" \
            f"adultNum=2&" \
            f"childNum=0&" \
            f"childAgeInform=&" \
            f"restaurantTypeInform=&" \
            f"restaurantNameCd=&" \
            f"wheelchairCount=0&" \
            f"stretcherCount=0&" \
            f"showWay=&" \
            f"reservationStatus=&" \
            f"beforeUrl=%2Finternalerror%2F&" \
            f"wayBack="
    url = HOST + path + "?" + param
    driver.implicitly_wait(5)
    driver.get(url)
    time.sleep(5)
    got_reservation_list = driver.find_elements_by_class_name("hasGotReservation")
    for got_reservation in got_reservation_list:
        name = got_reservation.find_elements_by_class_name("name")
        print(name)
    driver.quit()


if __name__ == "__main__":
    main()