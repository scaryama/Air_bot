# =========================
# crawling
# =========================
from selenium import webdriver
from selenium.webdriver.common.by import By


def removeElement(xpath):
    driver.execute_script("""
    var element = arguments[0];
    element.parentNode.removeChild(element);
    """, driver.find_element(By.XPATH, xpath))

def removes(ar):
    for id in ar:
        removeElement("//*[@id=\"" + id +"\"]")

def getValue():
    while True:
        element = driver.find_element(By.XPATH, "//*[@id=\"location-value\"]")
        value = element.text
        if len(value) > 0:
            driver.execute_script("arguments[0].innerHTML=''", element)
            break
    return value

options = webdriver.ChromeOptions()
#options.add_argument('headless')

url1 = "https://earth.nullschool.net/#current/particulates/surface/level/overlay=pm1/orthographic=126.92,37.38,3000/loc=126.922,37.383"
url2 = "https://earth.nullschool.net/#current/particulates/surface/level/overlay=pm2.5/orthographic=126.92,37.38,3000/loc=126.922,37.383"
url3 = "https://earth.nullschool.net/#current/particulates/surface/level/overlay=pm10/orthographic=126.92,37.38,3000/loc=126.922,37.383"

driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)

driver.get(url1)

removeElement("/html/head")
removeElement("/html/body/script")
removes(["display", "tara-stats", "sponsor", "notice", "settings-wrap", "calendar-wrapper", "earth", "status"])

#driver.get(url1)
p1 = getValue()
print(p1)

driver.get(url2)
p2 = getValue()
print(p2)

driver.get(url3)
p3 = getValue()
print(p3)

#driver.quit()


