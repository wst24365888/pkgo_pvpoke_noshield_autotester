from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import threading
import json
import time
import chromedriver_autoinstaller

lock = threading.Lock()

pokemons = []
scores = []

OPPO_SHIELD = 1
OUR_SHIELD = 1


def autotest(begin, end):
    chromedriver_autoinstaller.install()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://pvpoketw.com/battle/")

    time.sleep(2.5)

    multi_battle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#main > div.section.league-select-container.white > div > a:nth-child(2)")))
    multi_battle.click()

    time.sleep(0.5)

    team_select = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(3) > select.format-select"))))
    team_select.select_by_value("custom")

    fill_team = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(3) > div > div.custom-options > select"))))
    fill_team.select_by_value("great")

    opponent_shield = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(3) > div > div.options > select.shield-select"))))
    opponent_shield.select_by_value(str(OPPO_SHIELD))

    firstTime = True

    for pokeIndex in range(begin, end):
        try:
            global pokemons
            if not pokemons:
                choose_pokemon = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(1) > select")))
                pokemons = choose_pokemon.text.split('\n')

                print("len of pokemons:", len(pokemons))

            fill_pokemon = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(1) > input")))
            fill_pokemon.clear()
            fill_pokemon.send_keys(pokemons[pokeIndex+1].strip())

            if firstTime:
                pokemon_shield = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(1) > div.poke-stats > div.options > div.shield-section > select"))))
                pokemon_shield.select_by_value(str(OUR_SHIELD))

            cp = int(WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(1) > div.poke-stats > h3 > span.stat"))).text)
            print(f"#{pokeIndex} {pokemons[pokeIndex+1]}: {cp}")

            if cp < 1400:
                continue

            battle = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".battle-btn")))
            battle.click()

            score = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#main > div.section.battle > div:nth-child(6) > div > div > div > div > div.label.rating.star > span"))).text

            with lock:
                scores.append(
                    {"name": pokemons[pokeIndex+1].strip(), "score": int(score)})

            firstTime = False
        except:
            continue


if __name__ == "__main__":
    time_start = time.time()

    threads = []

    for i in range(10):
        t = threading.Thread(target=autotest, args=(116*i, 116*(i+1),))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    scores = [dict(tuple_item) for tuple_item in {
        tuple(dictionary.items()) for dictionary in scores}]
    result = sorted(scores, key=lambda k: k["score"], reverse=True)

    print(result)

    f = open("result.json", "w", encoding="utf-8")
    json.dump(result, f, ensure_ascii=False)
    f.close()

    time_end = time.time()

    print(f"time cost: {time_end - time_start} secs")
