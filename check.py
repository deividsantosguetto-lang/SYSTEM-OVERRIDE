import google.generativeai as genai

# Chave que deu sinal de vida (Key 3)
genai.configure(api_key="AIzaSyCK_sCDcEPy0Kg8ldI1JcSbuCxF3_wmCxw")

print("🔍 PERGUNTANDO AO GOOGLE QUAIS MODELOS VOCÊ TEM...")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ DISPONÍVEL: {m.name}")
except Exception as e:
    print(f"❌ ERRO NA CHAVE: {e}")