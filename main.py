import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError

# --- Configuração do FastAPI ---
app = FastAPI(
    title="Assistente LLM com FastAPI e Gemini",
    description="API para um assistente inteligente utilizando o modelo Gemini e mantendo um contexto conversacional simples."
)

# --- Variáveis globais ---
gemini_client = None
chat_session = {}  # {user_id: ChatSession}

# --- Modelos Pydantic ---
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    user_id: str
    response: str
    history_length: int

# --- Inicialização do cliente Gemini ---
@app.on_event("startup")
async def startup_event():
    global gemini_client

    if "GEMINI_API_KEY" not in os.environ:
        print("AVISO: A variável de ambiente GEMINI_API_KEY não está definida. A API não funcionará.")
        return

    try:
        gemini_client = genai.Client()
        print("Cliente Gemini inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar o cliente Gemini: {e}")
        gemini_client = None

# --- Rota de informação sobre chat ---
@app.get("/chat")
def chat_info():
    return {"message": "Use POST para enviar mensagens."}

# --- Rota principal de chat ---
@app.post("/chat", response_model=ChatResponse, summary="Envia uma mensagem para o assistente LLM")
async def chat_with_assistant(request: ChatRequest):
    global gemini_client

    if gemini_client is None:
        raise HTTPException(status_code=503, detail="Serviço de IA indisponível. Verifique a GEMINI_API_KEY.")

    user_id = request.user_id
    user_message = request.message

    # --- Gerenciar sessão de chat ---
    if user_id not in chat_session:
        system_instruction = (
            "Você é um assistente inteligente especializado em boas práticas de programação Python e FastAPI. "
            "Responda de forma clara, concisa e com exemplos de código quando necessário."
        )
        try:
            chat = gemini_client.chats.create(model="gemini-2.5-flash")
            chat.send_message(system_instruction)
            chat_session[user_id] = chat
            print(f"Nova sessão de chat criada para o usuário: {user_id}")
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"Erro ao iniciar a sessão de chat com a IA: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado ao iniciar a sessão de chat: {e}")

    chat = chat_session[user_id]

    # --- Enviar mensagem do usuário e obter resposta ---
    try:
        response = chat.send_message(user_message)
        return ChatResponse(
            user_id=user_id,
            response=response.text,
            history_length=len(chat.get_history())
        )
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Erro da API Gemini: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado durante o processamento: {e}")

# --- Rota de status ---
@app.get("/status", summary="Verifica o status da API")
async def get_status():
    return {
        "status": "online",
        "llm_client_initialized": gemini_client is not None,
        "active_chat_sessions": len(chat_session)
    }

# --- Rota para limpar histórico ---
@app.delete("/chat/{user_id}", summary="Limpa o histórico de chat de um usuário")
async def clear_chat_history(user_id: str):
    if user_id in chat_session:
        del chat_session[user_id]
        return {"message": f"Histórico de chat para o usuário {user_id} limpo com sucesso."}
    else:
        raise HTTPException(status_code=404, detail=f"Nenhuma sessão de chat encontrada para o usuário {user_id}.")
