import os
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from db_handler import DBHandler
from tweet_handler import TweetHandler
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

HOST = os.environ["SCRAPING_TARGET_URL"]
WEEKDAY_LIST = ["月","火","水","木","金","土","日"]
ROUND_PER_EXEC = 1  # Job1回あたりに何回転するか
MAX_RETRY = 4


def get_target_date_obj_list():
    """
    クローリング対象のdatetimeオブジェクトのリストを取得する。
    本日から2か月間を対象とする。
    """
    current_date = datetime.now(timezone(timedelta(hours=9)))
    end_date = current_date + relativedelta(months=2) - timedelta(days=2)
    target_date_list = [current_date]
    should_continue = True
    while should_continue:
        next_date = current_date + timedelta(days=1)
        current_date = next_date
        target_date_list.append(next_date)
        if next_date > end_date:
            should_continue = False
    return target_date_list


def fetch_all_restaurant_name(driver, target_datetime_obj):
    """
    すべてのレストランの名称を返却する。
    """
    path = "/sp/restaurant/list/"
    target_date_str = target_datetime_obj.strftime('%Y%m%d')
    param = f"useDate={target_date_str}&" \
            f"mealDivInform=&" \
            f"adultNum=2&" \
            f"childNum=0&" \
            f"childAgeInform=&" \
            f"restaurantTypeInform=&" \
            f"restaurantNameCd=&" \
            f"wheelchairCount=0&" \
            f"stretcherCount=0&" \
            f"showWay=&" \
            f"reservationStatus=0&" \
            f"beforeUrl=%2Finternalerror%2F&" \
            f"wayBack="
    url = HOST + path + "?" + param
    driver.get(url)
    time.sleep(5)
    icon_show_restaurant_list = []
    for i in range(MAX_RETRY):
        icon_show_restaurant_list = driver.find_elements_by_class_name("iconShowRestaurant")
        if len(icon_show_restaurant_list) != 0:
            break
        time.sleep(5)
    if len(icon_show_restaurant_list) == 0:
        raise Exception(f"{MAX_RETRY}回リトライしましたがアクセスできませんでした。")
    name_list = driver.find_elements_by_class_name("name")
    return[name.text for name in name_list][:-2]  # 後ろ2つの要素は不要


def fetch_single_date_restaurant_info(driver, target_datetime_obj):
    """
    予約可能なレストラン名称をリストにして返す。
    """
    path = "/sp/restaurant/list/"
    target_date_str = target_datetime_obj.strftime('%Y%m%d')
    param = f"useDate={target_date_str}&" \
            f"mealDivInform=&" \
            f"adultNum=2&" \
            f"childNum=0&" \
            f"childAgeInform=&" \
            f"restaurantTypeInform=&" \
            f"restaurantNameCd=&" \
            f"wheelchairCount=0&" \
            f"stretcherCount=0&" \
            f"showWay=&" \
            f"reservationStatus=1&" \
            f"beforeUrl=%2Finternalerror%2F&" \
            f"wayBack="
    url = HOST + path + "?" + param
    driver.get(url)
    time.sleep(5)
    icon_show_restaurant_list = []
    for i in range(MAX_RETRY):
        icon_show_restaurant_list = driver.find_elements_by_class_name("iconShowRestaurant")
        if len(icon_show_restaurant_list) != 0:
            break
        time.sleep(5)
    if len(icon_show_restaurant_list) == 0:
        raise Exception(f"{MAX_RETRY}回リトライしましたがアクセスできませんでした。")
    got_reservation_list = driver.find_elements_by_class_name("hasGotReservation")
    can_reserve_restaurant_name_list = []
    for got_reservation in got_reservation_list:
        name = got_reservation.find_elements_by_class_name("name")
        can_reserve_restaurant_name_list.append(name[0].text)
    return can_reserve_restaurant_name_list


def get_status_updated_restaurant_info(db_handler, target_datetime_obj, all_restaurant_name_list, can_reserve_restaurant_name_list):
    """
    予約可能情報の差分を返却する。
    """
    cannot_reserve_to_reserve = []  # 予約不可 -> 予約可
    reserve_to_cannot_reserve = []  # 予約可 -> 予約不可
    restaurant_status_dict = db_handler.select_from_drestaurant_status_dict(target_datetime_obj)
    for restaurant_name in all_restaurant_name_list:
        previous_status = restaurant_status_dict.get(restaurant_name)
        current_status = (restaurant_name in can_reserve_restaurant_name_list)
        # 予約不可 -> 予約可
        if not previous_status and current_status:
            cannot_reserve_to_reserve.append(restaurant_name)
        # 予約可 -> 予約不可
        if previous_status and not current_status:
            reserve_to_cannot_reserve.append(restaurant_name)
    return cannot_reserve_to_reserve, reserve_to_cannot_reserve


def update_db(db_handler, target_datetime_obj, cannot_reserve_to_reserve, reserve_to_cannot_reserve):
    """
    クローリンクした結果をDBに格納する。
    """
    for restaurant_name in cannot_reserve_to_reserve:
        db_handler.update_drestaurant_status(target_datetime_obj, restaurant_name, True)
    for restaurant_name  in reserve_to_cannot_reserve:
        db_handler.delete_drestaurant_status(target_datetime_obj, restaurant_name)


def post_tweet(tweet_handler, target_date_obj, cannot_reserve_to_reserve):
    """
    ツイートする。
    """
    # URLを生成
    path = "/sp/restaurant/list/"
    target_date_str = target_date_obj.strftime('%Y%m%d')
    param = f"useDate={target_date_str}&" \
            f"mealDivInform=&" \
            f"adultNum=2&" \
            f"childNum=0&" \
            f"childAgeInform=&" \
            f"restaurantTypeInform=&" \
            f"restaurantNameCd=&" \
            f"wheelchairCount=0&" \
            f"stretcherCount=0&" \
            f"showWay=&" \
            f"reservationStatus=1&" \
            f"beforeUrl=%2Finternalerror%2F&" \
            f"wayBack="
    url = HOST + path + "?" + param

    dt_now_utc_aware = datetime.now(timezone(timedelta(hours=9)))
    weekday_str = WEEKDAY_LIST[target_date_obj.weekday()]
    tweet_text = f"{format(target_date_obj, '%Y/%m/%d')}({weekday_str}) 予約がとれそう！\n"
    for i, restaurant_name in enumerate(cannot_reserve_to_reserve):
        tweet_text += f"{restaurant_name}\n"
        if i > 5:
            # ツイートの文字制限対策
            tweet_text += "...\n"
            break
    tweet_text += url + "\n"
    tweet_text += f"※{dt_now_utc_aware.strftime('%Y/%m/%d %H:%M:%S')}時点の情報\n"
    tweet_text += f"#ディズニー #ディズニーレストラン"
    tweet_handler.post_tweet(tweet_text)


def main():
    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    driver.implicitly_wait(5)
    db_handler = DBHandler()
    tweet_handler = TweetHandler()
    target_date_obj_list = get_target_date_obj_list()
    all_restaurant_name = fetch_all_restaurant_name(driver, target_date_obj_list[0])
    for counter in range(ROUND_PER_EXEC):
        for target_datetime_obj in target_date_obj_list:
            time.sleep(5)
            target_datetime_str = format(target_datetime_obj, '%Y/%m/%d')
            try:
                can_reserve_restaurant_name_list = fetch_single_date_restaurant_info(driver, target_datetime_obj)
            except Exception as e:
                print(f"クローリングに失敗しました：{target_datetime_str}")
                print(e)
                continue
            cannot_reserve_to_reserve, reserve_to_cannot_reserve \
                = get_status_updated_restaurant_info(db_handler,
                                                     target_datetime_obj,
                                                     all_restaurant_name,
                                                     can_reserve_restaurant_name_list)
            update_db(db_handler, target_datetime_obj, cannot_reserve_to_reserve, reserve_to_cannot_reserve)
            try:
                if len(cannot_reserve_to_reserve) != 0:
                    post_tweet(tweet_handler, target_datetime_obj, cannot_reserve_to_reserve)
                print(target_datetime_str, cannot_reserve_to_reserve, reserve_to_cannot_reserve)
            except Exception as e:
                print(f"Twitterへの投稿に失敗しました：{target_datetime_str}")
                print(e)
    driver.quit()


if __name__ == "__main__":
    main()
