from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)  # Разрешаем CORS

# Ваши данные Yandex Cloud
YANDEX_FOLDER_ID = "b1gem6hvga1n872g5iug"
YANDEX_API_KEY = "AQVNxxfO7thv4q0zZt_tYo2gBHQfVRCz_oTgPO8B"

@app.route('/test', methods=['GET'])
def test_connection():
    """Проверка работы сервера"""
    return jsonify({
        'status': 'ok',
        'message': 'Прокси-сервер работает',
        'yandex_configured': bool(YANDEX_API_KEY and YANDEX_FOLDER_ID)
    })

@app.route('/proxy', methods=['POST', 'OPTIONS'])
def proxy_to_yandex():
    """Прокси запросов к YandexGPT API"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        
        # Используем данные из запроса или из конфигурации
        folder_id = data.get('folderId', YANDEX_FOLDER_ID)
        api_key = data.get('apiKey', YANDEX_API_KEY)
        query = data.get('query', '')
        model = data.get('model', 'yandexgpt-lite')
        
        if not query:
            return jsonify({'error': 'Пустой запрос'}), 400
        
        # Формируем запрос к YandexGPT
        yandex_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {api_key}',
            'x-folder-id': folder_id
        }
        
        payload = {
            'modelUri': f'gpt://{folder_id}/{model}',
            'completionOptions': {
                'stream': False,
                'temperature': 0.3,
                'maxTokens': 4000
            },
            'messages': [
                {
                    'role': 'system',
                    'text': 'Ты эксперт по разработке Telegram Mini Apps. Отвечай подробно с примерами кода.'
                },
                {
                    'role': 'user',
                    'text': query
                }
            ]
        }
        
        # Отправляем запрос к YandexGPT
        response = requests.post(yandex_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'result' in result and 'alternatives' in result['result']:
            answer = result['result']['alternatives'][0]['message']['text']
            return jsonify({'response': answer})
        else:
            return jsonify({'error': 'Неверный ответ от YandexGPT'}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Ошибка подключения к YandexGPT: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервера"""
    return jsonify({'status': 'healthy', 'service': 'yandex-proxy'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Прокси-сервер для YandexGPT запущен!")
    print(f"📁 Folder ID: {YANDEX_FOLDER_ID}")
    print("🔑 API Key: ************")
    print("🌐 Сервер доступен по адресу: http://localhost:3000")
    print("=" * 50)
    print("\n📋 Инструкция:")
    print("1. Откройте index.html в браузере")
    print("2. Убедитесь что URL прокси: http://localhost:3000/proxy")
    print("3. Нажмите 'Проверить подключение'")
    print("4. Начните отправлять запросы к YandexGPT")
    print("\n⚠️  Для остановки сервера нажмите Ctrl+C")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=3000, debug=True)
