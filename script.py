from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Defina o caminho do ChromeDriver
service = Service("C:\chromedriver.exe") 
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa o Chrome em modo headless (sem abrir janela)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Inicie o driver do Chrome
driver = webdriver.Chrome(service=service, options=options)

# Carrega a página da Amazon
url = "https://www.amazon.com.br/Livros/"
driver.get(url)

# Aguarde alguns segundos para garantir que o JavaScript carregue todo o conteúdo
time.sleep(5)  # Ajuste o tempo de espera, se necessário

# Extrai o HTML da página renderizada
html = driver.page_source

# Salve o HTML em um arquivo para análise
with open("selenium_response.html", "w", encoding="utf-8") as file:
    file.write(html)

# Use BeautifulSoup para analisar o HTML
soup = BeautifulSoup(html, 'html.parser')

# Exemplo de extração: ajuste o seletor conforme a estrutura da página
books = soup.find_all('span', class_='a-truncate-cut')  # Verifique se a classe está correta
for book in books:
    print(book.get_text(strip=True))  # Exibe o título do livro

# Encerra o driver do Chrome
driver.quit()
