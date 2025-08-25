import requests
from bs4 import BeautifulSoup
import random
import re
from db import ad_exists, add_ad

def get_random_cars(min_price=500, max_price=3000, count=1, max_photos=10, max_pages=20):
    headers = {"User-Agent": "Mozilla/5.0"}

    for attempt in range(max_pages):  # максимум столько попыток
        page = random.randint(1, 10)  # можно заменить на последовательный перебор
        url = f"https://cars.av.by/filter?price_usd[min]={min_price}&price_usd[max]={max_price}&page={page}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.find_all("div", class_="listing-item")
        if not items:
            continue

        random.shuffle(items)  # перемешаем
        results = []

        for random_item in items:
            if len(results) >= count:
                break

            title_tag = random_item.find("a", class_="listing-item__link")
            link = "https://cars.av.by" + title_tag["href"] if title_tag else ""

            # проверяем, не отправляли ли это объявление раньше
            if not link or ad_exists(link):
                continue

            title = title_tag.text.strip() if title_tag else "Без названия"

            price = random_item.find("div", class_="listing-item__priceusd")
            price_text = price.text.strip() if price else "Нет цены"

            location = random_item.find("div", class_="listing-item__location")
            location_text = location.text.strip() if location else "Неизвестно"

            params = random_item.find("div", class_="listing-item__params")
            params_text = params.get_text(", ", strip=True) if params else ""
            params_text = re.sub(r"(,\s*){2,}", ", ", params_text)
            params_text = re.sub(r"\s{2,}", " ", params_text)
            params_text = params_text.strip(", ")

            desc_tag = random_item.find("div", class_="listing-item__message")
            description = desc_tag.text.strip() if desc_tag else "Нет описания"

            # фото
            photos = []
            adv_resp = requests.get(link, headers=headers)
            adv_soup = BeautifulSoup(adv_resp.text, "html.parser")
            gallery = adv_soup.select(".gallery__stage .gallery__frame img")
            for img in gallery:
                url_img = img.get("data-src") or img.get("src")
                if url_img and not url_img.startswith("data:image"):
                    photos.append(url_img)
                if len(photos) >= max_photos:
                    break

            # удаляем дубликат последней фотки (если совпадает с предпоследней)
            if len(photos) >= 2 and photos[-1] == photos[-2]:
                photos.pop()

            results.append({
                "title": title,
                "price": price_text,
                "location": location_text,
                "params": params_text,
                "description": description,
                "link": link,
                "photos": photos,
            })

            # сохраняем объявление в БД
            add_ad(link)

        if results:  # нашли новые объявления → выходим
            return results

    # если за max_pages попыток ничего не нашли
    return []
