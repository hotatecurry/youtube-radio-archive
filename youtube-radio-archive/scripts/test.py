from google import genai

client = genai.Client(api_key="AIzaSyD_dQFtMf-_6nhccnSBLtOtkcIyLzQ1Ltg")
for m in client.models.list():
    print(m.name)