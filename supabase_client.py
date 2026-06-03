import os
from dotenv import load_dotenv
from supabase import create_client

#OBSERVAÇÃO IMPORTANTE:
#- Use Python 3.12 (versões diferentes podem causar erro no supabase)
#- Recrie o venv quando trocar de versão do Python:

# INSTALAR O PYTHON 3.12 -> winget install Python.Python.3.12

#  1. deletar venv atual
#  2. py -3.12 -m venv venv
#  3. venv\\Scripts\\activate
#  4. pip install -r requirements.txt

# - Criar arquivo .env na raiz:
#  DATABASE_URL=... (se você já tem o .env provavelmetne já tem esse, então é só adicionar os dois de baixo)
#  SUPABASE_URL=...
#  SUPABASE_KEY=...

# - Reiniciar o VS Code/terminal após mudar o ambiente

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)