# League-of-Legends-Wiki-Crawler
A bot to crawl through the LoL wiki to extract base stats for all champions.

Lines 38-39, 60-71 are due to inconsistent naming of web elements on the wiki.

This bot uses Selenium (https://www.selenium.dev/) and ChromeDriver (https://chromedriver.chromium.org/downloads) to open the wiki page of each champion, target the HTML elements, and record the following:
-Champion Name
-Champion Release Date
-Link to champion thumbnail
-All base and growth stats for
  -Movespeed
  -HP
  -Mana/Energy/Etc.
  -Armor
  -Magic Resist
  -Attack Damage
  -Attack Speed
  -Attack Range
 -As well as modifiers for both
  -URF
  -ARAM
These stats are saved to a SQLite3 Database.
