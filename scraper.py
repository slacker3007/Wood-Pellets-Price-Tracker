import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import datetime
import os

def get_balticwood_price():
    url = "https://www.balticwoodtrade.lv/lv/produkcija/kokskaidu-granulas"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if "@graph" in data:
                items = data["@graph"]
            else:
                items = [data]
            
            prices = {}
            for item in items:
                if item.get("@type") == "Product" and "offers" in item:
                    name = item.get("name", "").strip().upper()
                    offers = item["offers"]
                    
                    # Store price even if OutOfStock, but you can filter if preferred.
                    # Currently we prioritize grabbing the price for the specific names.
                    if name in ["GABBY PLUS", "GABBY"]:
                        prices[name] = float(offers["price"])
            
            if prices:
                return prices
        except Exception as e:
            continue
            
    return {}

def get_stali_price():
    url = "https://www.stali.lv/lv/granulas"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") == "Product" and "offers" in data:
                for offer in data["offers"]:
                    if offer.get("sku") == "p - pallets" or "paletes" in offer.get("name", "").lower():
                        return float(offer["price"])
        except Exception:
            continue
            
    return None

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS prices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  website TEXT,
                  price REAL)''')
    conn.commit()
    return conn

def main():
    print("Scraping prices...")
    bwt_prices = get_balticwood_price()
    print(f"BalticWoodTrade: {bwt_prices}")
    
    stali_price = get_stali_price()
    print(f"Stali: {stali_price}")
    
    db_path = "prices.db"
    conn = init_db(db_path)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    
    for name, price in bwt_prices.items():
        c.execute("INSERT INTO prices (date, website, price) VALUES (?, ?, ?)", (today, f"BalticWoodTrade - {name}", price))
        
    if stali_price is not None:
        c.execute("INSERT INTO prices (date, website, price) VALUES (?, ?, ?)", (today, "Stali", stali_price))
        
    conn.commit()
    conn.close()
    print("Prices saved to database.")

    # Call dashboard generator
    import dashboard
    dashboard.generate()

if __name__ == "__main__":
    main()
