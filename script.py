from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import os
from datetime import datetime
import pandas as pd
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

    # Extrai o HTML da página renderizada, análise com BeautifulSoup e encerra o driver
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    # Extração da classe 'a-offscreen' que contém título e preço depois e antes do desconto
    all_offscreen_elements = soup.find_all('span', class_='a-offscreen')

    # Array de tuplas para guardar os elementos
    books = []

    # Loop para pegar cada elemento da classe `a-offscreen`
    for i in range(1, 91, 3):
        try:
            # Extraia o título, preço com desconto e preço original em sequência
            title = all_offscreen_elements[i].get_text(strip=True)
            discount_price = all_offscreen_elements[i + 1].get_text(strip=True)
            original_price = all_offscreen_elements[i + 2].get_text(strip=True)
            
            # Armazena o título e os preços no vetor de livros como uma tupla
            books.append((title, discount_price, original_price))
            
            # Exibe o resultado para verificação
            print(f"Título: {title}\nPreço: {original_price} -> {discount_price}\n")

        except IndexError:
            print("Elemento faltando, verifique a estrutura da página.")
    
    # Cria um DataFrame com os dados dos livros
    df = pd.DataFrame(books, columns=['Título', 'Preço com Desconto', 'Preço Original'])

    current_date = datetime.now().strftime("%d-%m-%Y") # Data atual no formato dia-mês-ano
    file_name = f"Livros em Oferta - {current_date}.csv" # Nome do arquivo que vai ser criado

    # Caminho da pasta onde o arquivo será criado
    folder_path = "C:/Users/Usuario/OneDrive/Web Development/Projects/Amazon_WebScrapper/tabelas"
    
    # Cria o caminho do arquivo
    file_path = os.path.join(folder_path, file_name)

    # Salva o DataFrame em um CSV
    df.to_csv(file_name, index=False, encoding='utf-8') 

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
    # Formata cada tupla da lista `books` para uma string e junta todas no corpo do email
    body = "Livros em Oferta:\n" + "\n".join([f"{title}\n {discount_price} -> {original_price}" for title, discount_price, original_price in books])
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
schedule.every().day.at("18:56").do(scrape_and_send_email)

# Loop que mantém o script rodando
while True:
    schedule.run_pending()
    time.sleep(60)  # Espera um minuto antes de verificar novamente