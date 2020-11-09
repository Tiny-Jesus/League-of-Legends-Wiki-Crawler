from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import string
import re
import sqlite3

connection = sqlite3.connect("leaguestats.db")
db = connection.cursor()

def fix(data):
    search = re.search(r"\-*\d+\.*\d*", data)
    data = search.group(0)
    data = round(1 + (float(data) / 100), 2)
    return(data)

start = time.time()
# path to chromedriver.exe
path = 'C:\Program Files (x86)\chromedriver.exe'
# create instance of webdriver
driver = webdriver.Chrome(path)
# leaguewiki url
url = 'https://leagueoflegends.fandom.com/wiki/List_of_champions'
# Code to open a specific url
driver.get(url)
# Set main window
main_window = driver.current_window_handle
# Find champion table
table = driver.find_element_by_class_name('wikitable.sortable.jquery-tablesorter')
num = 0
tbody = table.find_element_by_tag_name('tbody')
# Iterate over each champion in table
for row in tbody.find_elements_by_css_selector('tr'):
    num += 1
    # Get address of champ in row
    firstcell = row.find_elements_by_tag_name('td')[0]
    champlink = firstcell.find_element_by_tag_name("a").get_attribute("href")
    if champlink != "https://leagueoflegends.fandom.com/wiki/Nunu_%26_Willump":
        champlink = (f'{champlink}/LoL')
    # Pull champ img, role, and release date
    img = firstcell.find_element_by_tag_name("img").get_attribute("data-src")
    role = row.find_elements_by_tag_name("td")[1].text
    release_date = row.find_elements_by_tag_name("td")[3].text
    # Open new tab and change handler
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    # Open Champion page
    driver.get(champlink)

    # Get champion name
    name = driver.find_element_by_class_name("page-header__title").text
    #Remove "(League of Legends)" from name
    name = name.replace("(League of Legends)","").strip()
    # Edit champion name to wiki specifications for id searches
    champion = name
    if "'" in champion:
        champion = champion.lower().capitalize()
    champion = re.sub(r"([^a-zA-Z])","", champion)
    # Wrangle Outliers
    if champion == "Kled":
        champion = "Kled1"
    if champion == "Kogmaw":
        champion = "KogMaw"
    if champion == "LeBlanc":
        champion = "Leblanc"
    if champion == "NunuWillump":
        champion = "Nunu"
    if champion == "Reksai":
        champion = "RekSai"
    if champion == "Wukong":
        champion = "MonkeyKing"
    # Get INFO
    hp = driver.find_element_by_id(f'Health_{champion}').text
    hp_lvl = driver.find_element_by_id(f'Health_{champion}_lvl').text
    hp_regen = driver.find_element_by_id(f'HealthRegen_{champion}').text
    hp_regen_lvl = driver.find_element_by_id(f'HealthRegen_{champion}_lvl').text
    armor = driver.find_element_by_id(f'Armor_{champion}').text
    armor_lvl = driver.find_element_by_id(f'Armor_{champion}_lvl').text
    mr = driver.find_element_by_id(f'MagicResist_{champion}').text
    mr_lvl = driver.find_element_by_id(f'MagicResist_{champion}_lvl').text.strip("+ ")
    movespeed = driver.find_element_by_id(f'MovementSpeed_{champion}').text
    resourcebox = driver.find_element_by_css_selector('div[data-source="resource"]')
    resource = resourcebox.find_elements_by_tag_name('a')[1].text
    # Find resource numbers champion isn't resourceless
    if resource == "Mana":
        resource_amt = driver.find_element_by_id(f'ResourceBar_{champion}').text
        resource_amt_lvl = driver.find_element_by_id(f'ResourceBar_{champion}_lvl').text.strip("+ ")
        resource_regen = driver.find_element_by_id(f'ResourceRegen_{champion}').text
        resource_regen_lvl = driver.find_element_by_id(f'ResourceRegen_{champion}_lvl').text.strip("+ ")
    elif resource =="Energy":
        resource_amt = driver.find_element_by_id(f'ResourceBar_{champion}').text
        resource_amt_lvl = driver.find_element_by_id(f'ResourceBar_{champion}_lvl').text.strip("+ ")
        resource_regen = driver.find_element_by_css_selector('div[data-source="resource regen"]').text
    else:
        resource = "Resourceless"
        resource_amt = None
        resource_amt_lvl = None
        resource_regen = None
        resource_regen_lvl = None

    atk_dmg = driver.find_element_by_id(f'AttackDamage_{champion}').text
    atk_dmg_lvl = driver.find_element_by_id(f'AttackDamage_{champion}_lvl').text.strip("+ ")
    atk_range = driver.find_element_by_id(f'AttackRange_{champion}').text
    base_atk_spd = driver.find_element_by_css_selector(f'div[data-source="attack speed"]').text
    base_atk_spd = re.sub(r"([^0-9|-|.])", "", base_atk_spd, 0)
    
    # Get ARAM info
    aram_dmg_dealt = fix(driver.find_element_by_css_selector('div[data-source="aram-dmg-dealt"]').text)
    aram_dmg_taken = fix(driver.find_element_by_css_selector('div[data-source="aram-dmg-taken"]').text)
    aram_healing = fix(driver.find_element_by_css_selector('div[data-source="aram-healing"]').text)
    aram_shielding = fix(driver.find_element_by_css_selector('div[data-source="aram-shielding"]').text)
    
    # Click URF info
    click = "document.getElementsByClassName('pi-section-tab')[3].click()"
    driver.execute_script(click)
    # Get URF info
    urf_dmg_dealt = fix(driver.find_element_by_css_selector('div[data-source="urf-dmg-dealt"]').text)
    urf_dmg_taken = fix(driver.find_element_by_css_selector('div[data-source="urf-dmg-taken"]').text)
    urf_healing = fix(driver.find_element_by_css_selector('div[data-source="urf-healing"]').text)
    urf_shielding = fix(driver.find_element_by_css_selector('div[data-source="urf-shielding"]').text)

    # Close new window
    driver.close()
    driver.switch_to.window(main_window)

    #  !!SQL QUERIES!!
    db.execute("INSERT INTO champions VALUES (:name, :release_date, :img, :role, :resource, :resource_amt, :resource_amt_lvl, :resource_regen, :resource_regen_lvl, :hp, :hp_lvl, :hp_regen, :hp_regen_lvl, :movespeed, :armor, :armor_lvl, :mr, :mr_lvl, :atk_dmg, :atk_dmg_lvl, :atk_range, :base_atk_spd);", (name, release_date, img, role, resource, resource_amt, resource_amt_lvl, resource_regen, resource_regen_lvl, hp, hp_lvl, hp_regen, hp_regen_lvl, movespeed, armor, armor_lvl, mr, mr_lvl, atk_dmg, atk_dmg_lvl, atk_range, base_atk_spd))
    db.execute("INSERT INTO aram VALUES (:name, :aram_dmg_dealt, :aram_dmg_taken, :aram_healing, :aram_shielding);", (name, aram_dmg_dealt, aram_dmg_taken, aram_healing, aram_shielding))
    db.execute("INSERT INTO urf VALUES (:name, :urf_dmg_dealt, :urf_dmg_taken, :urf_healing, :urf_shielding);", (name, urf_dmg_dealt, urf_dmg_taken, urf_healing, urf_shielding))
    print(f'Champion: {name} #:{num}')
connection.commit()
print(f'Time To Execute: {time.time() - start}')
driver.quit()