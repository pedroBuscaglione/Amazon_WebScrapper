from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import sys
sys.stdout.reconfigure(encoding='utf-8')

# Defina o caminho do ChromeDriver
service = Service("C:/chromedriver.exe") 
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa o Chrome em modo headless (sem abrir janela)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Inicie o driver do Chrome
driver = webdriver.Chrome(service=service, options=options)

# Carrega a página da Amazon
url = "https://www.amazon.com.br/Livros/"
driver.get(url)

# Aguarda até que os elementos carreguem
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'a-truncate-full'))
    )
except Exception as e:
    print("Erro ao carregar a página:", e)

# Extrai o HTML da página renderizada
html = driver.page_source

# Uso do BeautifulSoup para analisar o HTML
soup = BeautifulSoup(html, 'html.parser')

in_offer_books = False # Boolean para separar os livros em discouto dos livros mais vendidos

# Extração dos títulos dos livros
books = soup.find_all('span', class_='a-truncate-full a-offscreen')
for book in books:
    if book.text == "Livros em Oferta":
        in_offer_section = True
        continue  # Ignora essa linha
    
    # Se entrou na seção de ofertas seleciona esse livro
    if in_offer_section: 
        print(book.get_text(strip=True).replace('\u200f', '').replace('\u200e', ''))

# Encerra o driver do Chrome
driver.quit()
