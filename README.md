# Sistema de Cobrança - Kanastra

## 📄 Sumário

- [Sistema de Cobrança - Kanastra](#sistema-de-cobrança---kanastra)
  - [📄 Sumário](#-sumário)
  - [Informações de Acesso e Execução](#informações-de-acesso-e-execução)
    - [1. Executando o Sistema](#1-executando-o-sistema)
    - [2. Acessando a API e Documentação](#2-acessando-a-api-e-documentação)
    - [3. Visualizando o Banco de Dados](#3-visualizando-o-banco-de-dados)
    - [4. Monitoramento de Tarefas](#4-monitoramento-de-tarefas)
    - [5. Executando os Testes](#5-executando-os-testes)
  - [Rotas da API](#rotas-da-api)
    - [**POST** `/api/v1/billing/upload`](#post-apiv1billingupload)
  - [Sobre o Projeto](#sobre-o-projeto)
  - [Tecnologias Utilizadas](#tecnologias-utilizadas)
  - [Arquitetura do Sistema](#arquitetura-do-sistema)
  - [Configuração do Ambiente](#configuração-do-ambiente)
  - [Banco de Dados](#banco-de-dados)

---

## Informações de Acesso e Execução

### 1. Executando o Sistema

Para iniciar o sistema completo, utilize o comando:

```bash
docker-compose -f docker-compose.yml up -d --build
```

### 2. Acessando a API e Documentação

- **Documentação da API (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Rota para Envio do Arquivo CSV**: `POST http://localhost:8000/api/v1/billing/upload`

### 3. Visualizando o Banco de Dados

Você pode visualizar o conteúdo do banco de dados através da interface MongoExpress:

- **URL**: [http://localhost:8081/db/kanastra_billing/](http://localhost:8081/db/kanastra_billing/)
- **Credenciais**:
  - **Username**: `1234`
  - **Password**: `4321`

### 4. Monitoramento de Tarefas

Para visualizar as tarefas sendo processadas pelo Celery, acesse:

- **URL**: [http://localhost:5555/](http://localhost:5555/)

### 5. Executando os Testes

Para executar os testes unitários e de integração, utilize o seguinte comando:

```bash
docker-compose -f docker-compose.test.yml up --build test
```

## Rotas da API

### **POST** `/api/v1/billing/upload`
- **Descrição**: Recebe um arquivo CSV contendo débitos e inicia o processamento.
- **Formato do CSV**:
  ```
  name,governmentId,email,debtAmount,debtDueDate,debtId
  John Doe,11111111111,johndoe@kanastra.com.br,1000000.00,2022-10-12,1adb6ccf-ff16-467f-bea7-5f05d494280f
  ```
- **Requisitos**: A requisição deve ser enviada como um formulário `multipart/form-data` contendo:
  - `file`: O arquivo CSV a ser processado.
  
- **Exemplo de Resposta**:

```json
{
	"status": "CSV file uploaded successfully for processing",
	"filename": "input.csv",
	"task_id": "1cc51a74-5601-4d93-b29f-5c6138e4e41e"
}
```

---

## Sobre o Projeto

Este projeto foi desenvolvido para o desafio técnico da Kanastra para a posição de Software Engineering Full-stack. A proposta era criar um sistema que processasse arquivos CSV de forma performática, gerando boletos e enviando notificações via e-mail. Além disso, o sistema deveria ser capaz de lidar com grandes volumes de dados de forma eficiente e escalável.

## Tecnologias Utilizadas

- **Backend**: FastAPI
- **Task Queue**: Celery
- **Banco de Dados**: MongoDB
- **Mensageria**: Redis
- **Monitoramento de Tasks**: Flower
- **Interface para o Banco de Dados**: MongoExpress
- **Contêinerização**: Docker & Docker Compose

## Arquitetura do Sistema

O sistema foi desenvolvido utilizando uma arquitetura modular que permite escalabilidade e fácil manutenção. Abaixo estão os principais componentes:

1. **API (FastAPI)**: Responsável por receber o arquivo CSV e iniciar o processo de cobrança.
2. **Celery**: Utilizado para processar as tarefas de forma assíncrona, garantindo que grandes volumes de dados sejam tratados de forma eficiente.
3. **MongoDB**: Banco de dados utilizado para armazenar informações dos débitos, logs de processamento e tarefas em andamento.
4. **Redis**: Servidor de cache usado como broker para o Celery.
5. **Flower**: Interface web para monitoramento das tarefas Celery.
6. **MongoExpress**: Interface web para visualizar o banco de dados MongoDB.

## Configuração do Ambiente

Para facilitar a configuração do ambiente, todas as variáveis de configuração estão centralizadas no arquivo `.env`. Este arquivo contém informações sensíveis, como credenciais do MongoDB e MongoExpress, mas foi mantido público para facilitar o teste do sistema.

**Exemplo do conteúdo do `.env`:**

```env
MONGO_HOST="mongo"
MONGO_PORT="27017"
MONGO_INITDB_ROOT_USERNAME="mongo_user"
MONGO_INITDB_ROOT_PASSWORD="mongo_password"
MONGO_INITDB_DATABASE="kanastra_billing"
ME_CONFIG_BASICAUTH_USERNAME="1234"
ME_CONFIG_BASICAUTH_PASSWORD="4321"
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"
LOG_LEVEL=FATAL
```

## Banco de Dados

O banco de dados foi estruturado com três coleções principais:

1. **`debts`**: Responsável por armazenar todos os débitos que estão no arquivo CSV de entrada.
2. **`logs`**: Contém registros detalhados do processamento, como duplicidade de débitos, e-mails enviados, boletos gerados, e erros encontrados.
3. **`tasks`**: Armazena informações gerais sobre as tarefas executadas pelo sistema, incluindo quantidade de boletos gerados, enviados, pendentes e outros dados relacionados à importação.