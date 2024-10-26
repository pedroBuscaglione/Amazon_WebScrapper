from bs4 import BeautifulSoup
import requests

with open('api_key.txt', 'r') as file:
    api_key = file.read().strip()

amazon_url = "https://www.amazon.com.br/Livros/"
scraperapi_url = f"http://api.scraperapi.com?api_key={api_key}&url={amazon_url}&render=true"

response = requests.get(scraperapi_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    books = soup.find_all('span', class_='a-truncate-cut')  # Atualize a classe, se necessário, após verificar o HTML

    if books:
        for book in books:
            print(book.get_text(strip=True))  # Imprime o título do livro
    else:
        print("Nenhum livro encontrado. Verifique a classe ou estrutura do HTML.")
else:
    print(f"Erro ao acessar a página: Status {response.status_code}")
