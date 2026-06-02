import os
import tempfile
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicia o cliente da API do Groq para o novo projeto
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ROTA PRINCIPAL: Auditoria de Fotos de Anúncios com o CDC
@app.post("/analyze-image")
async def analyze_image_endpoint(image: UploadFile = File(...)):
    image_bytes = await image.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    ext = image.filename.split(".")[-1].lower()
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

    # Prompt ultra-calibrado para a ementa de Técnico em Vendas e CDC
    system_prompt = """
    Você é um Auditor Jurídico e Professor Coordenador do curso Técnico em Vendas, especialista em Código de Defesa do Consumidor (CDC) aplicado ao Marketing Comercial.
    Sua função é analisar a imagem de um anúncio, panfleto, cartaz ou propaganda enviada pelos estudantes e emitir um relatório de conformidade legal rígido.
    
    Sua resposta DEVE ser dividida estritamente usando as marcações [TEXTO_CHAT] e [AUDIO_PROFESSOR].

    [TEXTO_CHAT]
    Crie um relatório estruturado em formato de Folha de Auditoria Comercial Oficial:
    
    1. PERCENTUAL DE ADERÊNCIA À LEI: Diga claramente a porcentagem estimada de quanto o anúncio cumpre as regras do CDC (Ex: "Porcentagem de Conformidade: 45%").
    2. O QUE FALTA / IRREGULARIDADES: Liste em tópicos curtos o que está errado ou ausente no anúncio (Ex: falta do preço total à vista, letras de rodapé ilegíveis, indução a erro sobre características, omissão de juros mensais/anuais, falta de clareza em propostas B2C ou B2B).
    3. ARTIGOS DO CDC VIOLADOS: Cite explicitamente os artigos correspondentes às infrações (Dê ênfase especial aos Artigos 30, 31, 35, 36 e 37 que tratam de oferta e publicidade enganosa ou abusiva).
    4. RECOMENDAÇÃO TÉCNICA (SUGESTÃO DO VENDEDOR): Explique como os alunos de vendas devem reestruturar essa peça ou abordagem para que ela seja altamente persuasiva, mas 100% ética e legalizada.

    [AUDIO_PROFESSOR]
    Escreva EXCLUSIVAMENTE o texto que será narrado no ouvido do estudante. O tom deve ser de um professor avaliador analisando o trabalho do aluno em sala.
    - Comece de forma direta: "Analisando essa imagem que você mandou, a peça publicitária atingiu tantos por cento de conformidade com o nosso Código de Defesa do Consumidor."
    - Explique de forma conversacional e simplificada qual foi o pior erro e o que eles devem corrigir como técnicos em vendas.
    - Proibido usar asteriscos, siglas de artigos isoladas, barras ou emojis nesta seção de áudio.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            model="llama-3.2-11b-vision-instruct", # Modelo focado em ler imagens
        )
        full_response = chat_completion.choices[0].message.content

        chat_text = "Não foi possível estruturar o relatório visual."
        audio_text = "Não foi possível estruturar o áudio."

        if "[TEXTO_CHAT]" in full_response and "[AUDIO_PROFESSOR]" in full_response:
            parts = full_response.split("[AUDIO_PROFESSOR]")
            audio_text = parts[1].strip()
            chat_text = parts[0].replace("[TEXTO_CHAT]", "").strip()
        else:
            chat_text = full_response

        return {
            "teacher_response_chat": chat_text,
            "teacher_response_audio": audio_text
        }
    except Exception as e:
        return {"teacher_response_chat": f"Erro no processamento visual: {str(e)}", "teacher_response_audio": "Erro interno."}
