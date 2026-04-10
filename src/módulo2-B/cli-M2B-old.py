import typer
import cv2
import requests
import numpy as np

app = typer.Typer(no_args_is_help=True)

@app.command(name="abrir-camera")
def abrir_camera():
    url = "http://10.30.244.181/stream"
    print(f"Conectando ao sistema da Itu Bombas em {url}...")
    
    try:
        res = requests.get(url, stream=True, timeout=5)
        
        if res.status_code != 200:
            print(f"Erro: A placa respondeu, mas recusou o vídeo (Status {res.status_code})")
            return
            
        print("Sinal de vídeo recebido")
        
        bytes_data = bytes()
        for chunk in res.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8') 
            b = bytes_data.find(b'\xff\xd9') 
            
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                
                if frame is not None:
                    cv2.imshow('ITU BOMBAS', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        cv2.destroyAllWindows()
        
    except requests.exceptions.RequestException as e:
        print("\n Erro de conexão com a placa.")
        print("A ESP32 desligou, o IP mudou, ou o computador não está na mesma rede.")
        print(f"Detalhe técnico: {e}")

@app.command(name="status")
def status():
    print("Sistema pronto.")

if __name__ == "__main__":
    app()