# Assistente LLM Especializado com FastAPI e Gemini

## 🎯 Objetivo do Projeto

Este projeto implementa um **microserviço em Python utilizando o framework FastAPI** que atua como um assistente inteligente especializado. O assistente é focado em **boas práticas de programação Python e no framework FastAPI**.

A API se integra com o modelo de linguagem **Gemini 2.5 Flash** da Google, utilizando o SDK oficial `google-genai`. O principal diferencial é a implementação de um **contexto conversacional simples** (histórico de chat) mantido em memória, atendendo aos requisitos da **Trilha A – Assistente LLM**.

## 🛠️ Tecnologias Utilizadas

*   **Backend:** Python 3.11+
*   **Framework Web:** FastAPI
*   **Geração de IA:** Google Gemini API (modelo `gemini-2.5-flash`)
*   **Gerenciamento de Dependências:** `requirements.txt`
*   **Variáveis de Ambiente:** `python-dotenv`

## ⚙️ Instruções de Instalação

1.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
     venv\Scripts\activate  # No Windows
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Obtenha sua Chave de API do Gemini:**
    *   Crie uma conta no Google AI Studio e gere sua chave de API.
    *   Acesse: [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)

4.  **Configure a Variável de Ambiente:**
    - Vá no arquivo `.env` na raiz do projeto e adicione sua chave de API:
    ```
    GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
    ```
    - Como usar

- Defina a variável de ambiente GEMINI_API_KEY antes de iniciar o servidor:
- No proprio Powershell antes de inicializar o servidor coloque a chave nas "" 
```
$env:GEMINI_API_KEY="SUA_CHAVE-API"
```
- O projeto utiliza a biblioteca `python-dotenv` para carregar essa variável automaticamente.

## ▶️ Como Rodar o Servidor

Com o ambiente virtual ativado e as dependências instaladas, execute o servidor Uvicorn:

```bash
uvicorn main:app --reload
```

O servidor estará acessível em `http://127.0.0.1:8000`.

## 🧪 Como Testar as Rotas

A documentação interativa (Swagger UI) está disponível em: `http://127.0.0.1:8000/docs`.

### 1. Rota Principal: `/chat` (POST)

Esta rota é responsável pela interação com o assistente LLM, mantendo o contexto conversacional.

**Endpoint:** `POST /chat`

**Corpo da Requisição (JSON):**

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `user_id` | `string` | Identificador único para a sessão de chat (necessário para manter o histórico). | `"usuario_teste_123"` |
| `message` | `string` | A mensagem a ser enviada ao assistente. | `"Qual a diferença entre Pydantic BaseModel e dataclasses?"` |

**Exemplo de Teste com `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": "dev_001",
  "message": "Qual a diferença entre Pydantic BaseModel e dataclasses?"
}'
```

**Resposta Esperada (JSON):**

```json
{
  "user_id": "dev_001",
  "response": "O Pydantic BaseModel é focado em validação de dados e serialização/desserialização, sendo ideal para APIs (como no FastAPI). Já o dataclass é uma ferramenta nativa do Python para criar classes com foco em armazenamento de dados, sem a validação automática do Pydantic.",
  "history_length": 2
}
```

**Teste de Contexto (Segunda Mensagem):**

Envie uma segunda mensagem usando o **mesmo `user_id`** para testar se o assistente lembra do tópico anterior:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": "dev_001",
  "message": "E qual deles o FastAPI usa por padrão para definir o corpo da requisição?"
}'
```

A resposta deve fazer referência ao Pydantic, confirmando que o contexto foi mantido.

### 2. Rota de Limpeza de Histórico: `/chat/{user_id}` (DELETE)

**Endpoint:** `DELETE /chat/{user_id}`

**Descrição:** Limpa o histórico de chat de um usuário específico, forçando o início de uma nova conversa.

**Exemplo de Teste com `curl`:**

```bash
curl -X 'DELETE' \
  'http://127.0.0.1:8000/chat/dev_001' \
  -H 'accept: application/json'
```

### 3. Rota de Status: `/status` (GET)

**Endpoint:** `GET /status`

**Descrição:** Verifica o status da API e se o cliente Gemini foi inicializado corretamente.

## 📂 Estrutura Mínima do Projeto

```
fastapi_llm_assistant/
├── .env                  # Variável de ambiente com a chave GEMINI_API_KEY
├── main.py               # Código principal da aplicação FastAPI
├── requirements.txt      # Lista de dependências do projeto
└── README.md             # Este arquivo
```

## ⚠️ Tratamento de Erros

A API inclui tratamento básico de erros:

*   **503 Service Unavailable:** Retornado se a `GEMINI_API_KEY` não estiver configurada ou se o cliente Gemini falhar ao inicializar.
*   **500 Internal Server Error:** Retornado em caso de falha na comunicação com a API do Gemini (ex: chave inválida, limite de taxa excedido).
*   **404 Not Found:** Retornado ao tentar limpar o histórico de um `user_id` inexistente.
*   **422 Unprocessable Entity:** Erro padrão do FastAPI para validação de dados (se o JSON de entrada estiver incorreto).
