import requests
from flask import Flask, request, render_template, jsonify
from itertools import permutations

app = Flask(__name__)

# Chave da API do Google Maps (substitua com a sua própria chave)
API_KEY = 'AIzaSyAGDNNmzbgBpZFCF5GNm9nMzLv_2lNeygw'

# Coordenadas do ponto de partida (exemplo)
local_partida = (-23.694179107549026, -46.605410054686395)
origin = f"{local_partida[0]},{local_partida[1]}"

# Lista para armazenar os endereços adicionados
enderecos_adicionados = []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        enderecos = request.form.getlist('endereco')

        if enderecos:
            waypoints_str = '|'.join([get_coordinates(endereco)
                                      for endereco in enderecos])

            directions_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={origin}&waypoints={waypoints_str}&key={API_KEY}'

            response = requests.get(directions_url)
            data = response.json()

            if data['status'] == 'OK':
                tempo_rota_total = 0
                quilometragem_total_metros = 0

                for leg in data['routes'][0]['legs']:
                    tempo_rota_total += leg['duration']['value']  # em segundos
                    # em metros
                    quilometragem_total_metros += leg['distance']['value']

                tempo_rota = f"{int(tempo_rota_total / 60)} minutos"
                quilometragem_total = f"{round(quilometragem_total_metros / 1000, 2)} km"

                optimized_waypoints = data['routes'][0]['waypoint_order']
                waypoints = [enderecos[i] for i in optimized_waypoints]

                route_summary = data['routes'][0]['summary']
                encoded_route = data['routes'][0]['overview_polyline']['points']
                map_url = f'https://www.google.com/maps/dir/?api=1&origin={origin}&destination={origin}&waypoints={"|".join(waypoints)}'

                return render_template('index.html', tempo_rota=tempo_rota, quilometragem_total=quilometragem_total, map_url=map_url, enderecos_adicionados=enderecos_adicionados)

    return render_template('index.html', tempo_rota=None, quilometragem_total=None, map_url=None, api_key=API_KEY, enderecos_adicionados=enderecos_adicionados)


@app.route('/adicionar_endereco', methods=['POST'])
def adicionar_endereco():
    endereco = request.form.get('endereco')
    if endereco:
        enderecos_adicionados.append(endereco)
    return jsonify({'success': True})


@app.route('/calcular_rota', methods=['POST'])
def calcular_rota():
    data = request.get_json()
    enderecos = data.get('enderecos', [])

    if enderecos:
        # Limitar o número de permutações a 10
        num_permutacoes_max = 150  # 15 permutações por minuto / 150 permutações = 10 min
        num_permutacoes = min(num_permutacoes_max, len(enderecos))
        enderecos = enderecos[:num_permutacoes]

        melhor_rota = None
        menor_tempo = float('inf')

        total_permutacoes = 0  # Contagem total de permutações
        permutacoes_feitas = 0  # Contagem de permutações feitas

        for permutacao in permutations(enderecos):
            total_permutacoes += 1  # Incrementa a contagem total de permutações
            permutacoes_feitas += 1  # Incrementa a contagem de permutações feitas

            waypoints_str = '|'.join([get_coordinates(endereco)
                                     for endereco in permutacao])
            directions_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={origin}&waypoints={waypoints_str}&key={API_KEY}'

            response = requests.get(directions_url)
            data = response.json()

            if data['status'] == 'OK':
                tempo_rota_total = 0

                for leg in data['routes'][0]['legs']:
                    tempo_rota_total += leg['duration']['value']  # em segundos

                if tempo_rota_total < menor_tempo:
                    menor_tempo = tempo_rota_total
                    melhor_rota = permutacao

            if permutacoes_feitas >= num_permutacoes_max:
                break  # Sai do loop se o limite de permutações for atingido

        print(f"Contagem total de permutações: {total_permutacoes}")
        print(f"Permutações feitas: {permutacoes_feitas}")

        if melhor_rota:
            waypoints_str = '|'.join([get_coordinates(endereco)
                                     for endereco in melhor_rota])
            directions_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={origin}&waypoints={waypoints_str}&key={API_KEY}'
            response = requests.get(directions_url)
            data = response.json()

            if data['status'] == 'OK':
                optimized_waypoints = data['routes'][0]['waypoint_order']
                waypoints = [melhor_rota[i] for i in optimized_waypoints]

                map_url = f'https://www.google.com/maps/dir/?api=1&origin={origin}&destination={origin}&waypoints={"|".join(waypoints)}'
                return jsonify({'map_url': map_url})

    return jsonify({'map_url': None})


def get_coordinates(address):
    geocoding_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}'
    response = requests.get(geocoding_url)
    data = response.json()
    if data['status'] == 'OK' and len(data['results']) > 0:
        location = data['results'][0]['geometry']['location']
        return f"{location['lat']},{location['lng']}"
    return ""


if __name__ == '__main__':
    app.run(debug=True)
