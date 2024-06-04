import requests
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
from webdriver_manager.chrome import ChromeDriverManager

# Inicialização do WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL do XML
xml_url = "https://www.ladygriffeoficial.com.br/xml/google"

# Função para obter e analisar o XML
def obter_dados_xml(url):
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        produtos = []
        marcas = {}
        for item in root.findall('.//item'):
            marca = item.find('{http://base.google.com/ns/1.0}brand').text
            if marca not in marcas:
                marcas[marca] = 0
            marcas[marca] += 1
            produto = {
                'nome': item.find('title').text,
                'pre_descricao': item.find('description').text,
                'preco': item.find('{http://base.google.com/ns/1.0}price').text,
                'marca': marca,
                'imagem_links': [item.find('{http://base.google.com/ns/1.0}image_link').text]  # Pega a primeira imagem
            }
            # Adiciona imagens adicionais se houver
            additional_image_links = item.findall('{http://base.google.com/ns/1.0}additional_image_link')
            for link in additional_image_links:
                produto['imagem_links'].append(link.text)
            produtos.append(produto)
        return produtos, marcas
    else:
        print(f"Erro ao obter o XML: {response.status_code}")
        return [], {}

# Função para baixar a imagem a partir de um link
def baixar_imagem(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Erro ao baixar a imagem: {response.status_code}")

# Função para gerar dados aleatórios de peso, altura, largura, comprimento e estoque
def gerar_dados_aleatorios():
    peso = round(random.uniform(0.1, 1.0), 3)
    altura = random.randint(10, 100)
    largura = random.randint(10, 100)
    comprimento = random.randint(10, 100)
    estoque = random.randint(1, 100)
    return peso, altura, largura, comprimento, estoque

# Função para cadastrar produtos no WooCommerce
def cadastrar_produto(produto):
    nome, preco, marca, pre_descricao, imagem_links = produto['nome'], produto['preco'], produto['marca'], produto['pre_descricao'], produto['imagem_links']
    peso, altura, largura, comprimento, estoque = gerar_dados_aleatorios()
    
    nome_input = driver.find_element(By.XPATH, '//*[@id="nome_produto"]')
    preco_input = driver.find_element(By.XPATH, '//*[@id="vr_preco"]')
    marca_input = driver.find_element(By.XPATH, '//*[@id="desc_marca"]')
    pre_descricao_input = driver.find_element(By.XPATH, '//*[@id="desc_pequena"]')
    
    nome_input.send_keys(nome)
    time.sleep(1)
    preco_input.send_keys(preco)
    time.sleep(1)
    marca_input.send_keys(marca)
    time.sleep(1)
    pre_descricao_input.send_keys(pre_descricao)
    time.sleep(1)

    # Selecionar a área de categorias
    categoria_dropdown = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="desc_categorias_chosen"]/ul/li')))
    driver.execute_script("arguments[0].scrollIntoView(true);", categoria_dropdown)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", categoria_dropdown)
    time.sleep(1)

    # Selecionar a categoria específica
    categoria_especifica = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="desc_categorias_chosen"]/div/ul/li')))
    driver.execute_script("arguments[0].scrollIntoView(true);", categoria_especifica)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", categoria_especifica)
    time.sleep(1)

    # Clique no botão para mais informações
    mais_info_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div[2]/div[3]/div[2]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", mais_info_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", mais_info_button)
    time.sleep(1)

    # Preencher peso
    peso_input = driver.find_element(By.XPATH, '//*[@id="vr_peso"]')
    peso_input.send_keys(str(peso))
    time.sleep(1)

    # Preencher altura
    altura_input = driver.find_element(By.XPATH, '//*[@id="form_produto"]/section[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div/div[2]/input')
    altura_input.send_keys(str(altura))
    time.sleep(1)

    # Preencher largura
    largura_input = driver.find_element(By.XPATH, '//*[@id="form_produto"]/section[3]/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[2]/input')
    largura_input.send_keys(str(largura))
    time.sleep(1)

    # Preencher comprimento
    comprimento_input = driver.find_element(By.XPATH, '//*[@id="form_produto"]/section[3]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[2]/input')
    comprimento_input.send_keys(str(comprimento))
    time.sleep(1)

    # Preencher estoque
    estoque_input = driver.find_element(By.XPATH, '//*[@id="num_estoque_atual"]')
    estoque_input.send_keys(str(estoque))
    time.sleep(1)

    # Clique para adicionar uma imagem
    adicionar_imagem_button = driver.find_element(By.XPATH, '//*[@id="form_produto"]/section[2]/div[2]/div[2]/div[1]/div')
    driver.execute_script("arguments[0].scrollIntoView(true);", adicionar_imagem_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", adicionar_imagem_button)
    time.sleep(1)

    # Baixar as imagens e fazer o upload da primeira imagem
    local_image_paths = []
    for index, imagem_link in enumerate(imagem_links):
        local_image_path = f"C:/Users/ikaro/OneDrive/Área de Trabalho/fotostp/imagem_temp_{index}.jpg"
        baixar_imagem(imagem_link, local_image_path)
        local_image_paths.append(local_image_path)

        # Selecionar o input de upload de imagem e enviar o caminho da imagem local
        upload_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@type="file"]')))
        upload_input.send_keys(local_image_path)
        time.sleep(1)

    # Clicar no botão salvar
    salvar_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/nav/div/div/div[3]/div/div[1]/p')))
    driver.execute_script("arguments[0].scrollIntoView(true);", salvar_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", salvar_button)
    time.sleep(3)

    # Clicar no botão para voltar à lista de produtos
    voltar_lista_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div/a[2]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", voltar_lista_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", voltar_lista_button)
    
    # Esperar até que a página carregue completamente
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div/div[1]')))

    # Clicar no botão para cadastrar novo produto
    cadastrar_novo_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div/div[1]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", cadastrar_novo_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", cadastrar_novo_button)
    time.sleep(2)

    # Remover as imagens baixadas após o uso
    for local_image_path in local_image_paths:
        if os.path.exists(local_image_path):
            os.remove(local_image_path)

# Função para exibir a interface de seleção
def exibir_interface_selecao(marcas):
    marcas_options = ''.join([f'<option value="{marca}">{marca} ({quantidade})</option>' for marca, quantidade in marcas.items()])
    html_content = f'''
    <html>
    <body>
        <h1>Selecione a Marca e Quantidade de Produtos</h1>
        <form id="form">
            <label for="marcas">Marcas:</label>
            <select id="marcas" name="marcas">
                {marcas_options}
            </select>
            <br>
            <label for="quantidade">Quantidade:</label>
            <input type="number" id="quantidade" name="quantidade" min="1">
            <br>
            <button type="submit">Submeter</button>
        </form>
        <script>
            document.getElementById('form').addEventListener('submit', function(event) {{
                event.preventDefault();
                const marca = document.getElementById('marcas').value.split(' ')[0];
                const quantidade = document.getElementById('quantidade').value;
                const status = document.createElement('div');
                status.id = 'status';
                status.innerText = `Marca: ${{marca}}, Quantidade: ${{quantidade}}`;
                document.body.appendChild(status);
            }});
        </script>
    </body>
    </html>
    '''
    driver.get("data:text/html;charset=utf-8," + html_content)
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'status')))
    marca = driver.find_element(By.ID, 'status').text.split(',')[0].split(': ')[1]
    quantidade = driver.find_element(By.ID, 'status').text.split(',')[1].split(': ')[1]
    return marca, quantidade

# Função principal
def main():
    # Obter dados do XML
    produtos, marcas = obter_dados_xml(xml_url)

    # Exibir interface de seleção
    marca_selecionada, quantidade_input = exibir_interface_selecao(marcas)
    quantidade = int(quantidade_input)

    # Filtrar produtos pela marca selecionada
    produtos_filtrados = [produto for produto in produtos if produto['marca'] == marca_selecionada]

    # Embaralhar e selecionar a quantidade desejada de produtos sem repetir
    random.shuffle(produtos_filtrados)
    produtos_selecionados = produtos_filtrados[:quantidade]

    # Abrir a página de login da loja
    driver.get('https://www.gg4.com.br/admin_loja/produto/carrega')

    # Esperar o usuário fazer o login manualmente
    while True:
        try:
            WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, '//*[@id="nome_produto"]')))
            break
        except:
            print("Por favor, faça o login na página.")

    # Cadastrar a quantidade de produtos especificada
    for produto in produtos_selecionados:
        cadastrar_produto(produto)

    # Fechar o navegador
    driver.quit()

# Executar a função principal
main()