from flask import Flask, request, jsonify, send_file
import os
import base64
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)

SAVED_GAME_DATA_DIR = "./saves"
os.makedirs(SAVED_GAME_DATA_DIR, exist_ok=True)

def aes_decrypt(source, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(source), AES.block_size)
    return decrypted

def rotaeno_decrypt(data, key):
    iv = data[:AES.block_size]
    source = data[AES.block_size:]
    return aes_decrypt(source, key, iv)

@app.route('/decryptAndSaveGameData', methods=['POST', 'OPTIONS'])
def decrypt_and_save_game_data():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    object_id = data.get("object-id")
    save_data_encoded = data.get("save-data")
        
    if not object_id or not save_data_encoded:
        return "Missing object-id or save-data", 400
        
    save_data_encrypted = base64.b64decode(save_data_encoded)
    key_string = object_id + "areyoureadyiamlady"
    key = hashlib.sha256(key_string.encode()).digest()
    save_data = rotaeno_decrypt(save_data_encrypted, key)
        
    game_data_path = os.path.join(SAVED_GAME_DATA_DIR, f"{object_id}.json")
    with open(game_data_path, "w") as f:
        f.write(json.dumps(json.loads(save_data.decode()), indent=4, ensure_ascii=False))
        
    return "Game data saved successfully.", 200

@app.route('/decryptGameData', methods=['POST', 'OPTIONS'])
def decrypt_game_data():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        object_id = data.get("object-id")
        save_data_encoded = data.get("save-data")
        
        if not object_id or not save_data_encoded:
            return "Missing object-id or save-data", 400
        
        save_data_encrypted = base64.b64decode(save_data_encoded)
        key_string = object_id + "areyoureadyiamlady"
        key = hashlib.sha256(key_string.encode()).digest()
        save_data = rotaeno_decrypt(save_data_encrypted, key)
        
        return save_data.decode(), 200
    except Exception as e:
        return str(e), 500

@app.route('/getGameData', methods=['GET', 'OPTIONS'])
def get_game_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    object_id = request.args.get("object-id")
    if not object_id:
        return "Missing object-id", 400
    
    game_data_path = os.path.join(SAVED_GAME_DATA_DIR, f"{object_id}.txt")
    if not os.path.exists(game_data_path):
        return "No data saved for this objectID.", 404
    
    return send_file(game_data_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
