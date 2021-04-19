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

lock = threading.Lock()

pokemons = []
scores = []


def autotest(begin, end):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://pvpoketw.com/battle/")

    time.sleep(2.5)

    multi_battle = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div/div/div[2]/div/a[2]")))
    multi_battle.click()

    team_select = Select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div/div/div[3]/div[3]/select[1]"))))
    team_select.select_by_index(5)

    fill_team = Select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div/div/div[3]/div[3]/div/div[1]/select"))))
    fill_team.select_by_index(1)

    opponent_shield = Select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div/div/div[3]/div[3]/div/div[2]/select[1]"))))
    opponent_shield.select_by_index(2)

    firstTime = True

    for pokeIndex in range(begin, end):
        print(f"now processing pokemon #{pokeIndex}")

        global pokemons
        if not pokemons:
            choose_pokemon = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[3]/div[1]/select")))
            pokemons = choose_pokemon.text.split('\n')

            print("len of pokemons:", len(pokemons))

        fill_pokemon = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[3]/div[1]/input")))
        fill_pokemon.clear()
        fill_pokemon.send_keys(pokemons[pokeIndex+1].strip())

        if firstTime:
            pokemon_shield = Select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div/div/div[3]/div[1]/div[2]/div[11]/div[1]/select"))))
            pokemon_shield.select_by_index(0)


        if int(WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/div[1]/div[2]/div[6]/div/span[2]"))).text) < 1400:
            continue

        battle = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".battle-btn")))
        battle.click()

        score = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[4]/div[4]/div/div/div/div/div[4]/span"))).text

        with lock:
            scores.append({"name": pokemons[pokeIndex+1].strip(), "score": int(score)})

        firstTime = False


if __name__ == "__main__":
    time_start = time.time()

    threads = []

    for i in range(10):
        t = threading.Thread(target=autotest, args=(113*i, 113*(i+1),))
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
