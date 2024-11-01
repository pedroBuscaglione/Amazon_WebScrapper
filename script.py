from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import re
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
sys.stdout.reconfigure(encoding='utf-8')

def scrape_and_send_email():

    # Defina o caminho do ChromeDriver
    service = Service("C:/chromedriver.exe") 
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executa o Chrome em modo headless (sem abrir janela)

    # Inicie o driver do Chrome
    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("Erro ao iniciar o WebDriver:", e)
        return

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

    # Extrai o HTML da página renderizada, analisa com BeautifulSoup e encerra o driver
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    # Boolean para separar os livros em discouto dos livros mais vendidos e Lista dos livros
    in_offer_section = False
    offer_books = [] 

    # Extração dos títulos dos livros
    books = soup.find_all('span', class_='a-truncate-full a-offscreen')
    for book in books:
        title = book.get_text(strip=True).replace('\u200f', '').replace('\u200e', '')
        if title == "Livros em Oferta":
            in_offer_section = True
            continue
        if in_offer_section:
            offer_books.append(title)

    with open('info.txt', 'r') as info:
        sender_email = info.readline().strip()
        receiver_email = info.readline().strip()
        password = info.readline().strip()

    # Lê o arquivo com dados sensíveis
    try:
        with open('info.txt', 'r') as info:
            sender_email = info.readline().strip()
            receiver_email = info.readline().strip()
            password = info.readline().strip()
    except FileNotFoundError:
        print("Arquivo info.txt não encontrado.")
        return

    # Componha o e-mail

    subject = "Relatório Diário de Livros da Amazon"
    body = "Livros em Oferta:\n" + "\n".join(offer_books)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Envio do e-mail
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Inicia uma conexão segura no port 587, que o protocolo SMTP usa
            server.login(sender_email, password)  # Faz login na conta de e-mail
            server.send_message(msg)  # Envia o e-mail
        print("E-mail enviado com sucesso!")
    except smtplib.SMTPException as e:
        print("Erro ao enviar o e-mail:", e)

# Horário para a execução do scraping e envio do e-mail uma vez por dia
schedule.every().day.at("12:00").do(scrape_and_send_email)

# Loop que mantém o script rodando
while True:
    schedule.run_pending()
    time.sleep(60)  # Espera um minuto antes de verificar novamente