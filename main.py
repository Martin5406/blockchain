import hashlib
import json
from time import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- Třída pro Blockchain zůstává úplně stejná ---
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pridat_blok(data="Tohle je prvni (Genesis) blok", predchozi_hash="0")

    def pridat_blok(self, data, predchozi_hash):
        blok = {
            "index": len(self.chain) + 1,
            "cas": time(),
            "data": data,
            "predchozi_hash": predchozi_hash
        }
        text_bloku = json.dumps(blok, sort_keys=True).encode()
        blok["hash"] = hashlib.sha256(text_bloku).hexdigest()
        self.chain.append(blok)
        return blok

muj_blockchain = Blockchain()

# --- Vytvoření API serveru čistě pomocí základu Pythonu ---
class APIHandler(BaseHTTPRequestHandler):
    # Pomocná funkce pro nastavení hlaviček odpovědi
    def _nastav_hlavicky(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # Zpracování GET requestu (zobrazení blockchainu)
    def do_GET(self):
        if self.path == '/ukazat':
            self._nastav_hlavicky(200)
            odpoved = {
                "pocet_bloku": len(muj_blockchain.chain),
                "blockchain": muj_blockchain.chain
            }
            # Odeslání odpovědi
            self.wfile.write(json.dumps(odpoved).encode('utf-8'))
        else:
            self._nastav_hlavicky(404)
            self.wfile.write(b'{"chyba": "Nenalezeno, zkus /ukazat"}')

    # Zpracování POST requestu (přidání bloku)
    def do_POST(self):
        if self.path == '/pridat':
            # Zjištění délky příchozích dat a jejich přečtení
            delka_dat = int(self.headers.get('Content-Length', 0))
            data_z_requestu = self.rfile.read(delka_dat).decode('utf-8')
            
            try:
                obsah = json.loads(data_z_requestu)
                data_do_bloku = obsah.get('data', 'Zadna data')
            except:
                data_do_bloku = 'Chyba v datech'

            posledni_blok = muj_blockchain.chain[-1]
            predchozi_hash = posledni_blok["hash"]
            
            novy_blok = muj_blockchain.pridat_blok(data=data_do_bloku, predchozi_hash=predchozi_hash)
            
            self._nastav_hlavicky(201)
            self.wfile.write(json.dumps({"zprava": "Uspesne pridano!", "blok": novy_blok}).encode('utf-8'))

if __name__ == '__main__':
    # Spuštění serveru na portu 5000
    adresa = ('localhost', 5000)
    server = HTTPServer(adresa, APIHandler)
    print("Server bezi na http://localhost:5000")
    print("Pro zobrazeni bez do prohlizece na: http://localhost:5000/ukazat")
    server.serve_forever()