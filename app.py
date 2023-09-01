from flask import Flask, render_template, request, redirect, url_for

import googlemaps

app = Flask(__name__)

# Substitua 'SUA_CHAVE_DE_API' pela sua chave de API do Google Maps
chave_api = 'AIzaSyAGDNNmzbgBpZFCF5GNm9nMzLv_2lNeygw'

locais_entrega_temp = []  # Lista temporária para armazenar as coordenadas de entrega

# Coordenadas do local de partida (geralmente o depósito)
local_partida = (-23.694191776643493, -46.605377959371594)

# Coordenadas do local de chegada (destino final)
# Substitua pelas coordenadas reais
local_chegada = (-23.694191776643493, -46.605377959371594)


def adicionar_local_entrega(coordenadas):
    locais_entrega_temp.append(coordenadas)


def otimizar_rota():
    if not locais_entrega_temp:
        return "Por favor, insira as coordenadas de entrega.", None

    cliente = googlemaps.Client(key=chave_api)

    try:
        destinos = locais_entrega_temp.copy()
        destinos.insert(0, local_partida)
        destinos.append(local_chegada)

        rota_otimizada = cliente.directions(
            origin=str(local_partida[0]) + ',' + str(local_partida[1]),
            destination=str(local_chegada[0]) + ',' + str(local_chegada[1]),
            mode='driving',
            waypoints=destinos[1:-1],
            optimize_waypoints=True
        )

        if rota_otimizada:
            distancia_total = 0

            # Calcule a distância total percorrendo as etapas da rota
            for step in rota_otimizada[0]['legs']:
                distancia_total += step['distance']['value']  # Em metros

            # Converta a distância total para quilômetros
            distancia_total_km = distancia_total / 1000

            # Gere o link do Google Maps
            link_google_maps = 'https://www.google.com/maps/dir/?api=1&origin=' + str(local_partida[0]) + ',' + str(local_partida[1]) + \
                '&destination=' + str(local_chegada[0]) + ',' + str(local_chegada[1]) + \
                '&waypoints=' + '|'.join(destinos[1:-1])

            return distancia_total_km, link_google_maps
        else:
            return "Não foi possível encontrar uma rota otimizada.", None
    except Exception as e:
        return f"Erro ao otimizar a rota: {str(e)}", None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        coordenadas = request.form.get('coordenadas')
        if coordenadas:
            adicionar_local_entrega(coordenadas)
    return render_template('index.html', locais_entrega_temp=locais_entrega_temp)


@app.route('/otimizar_rota', methods=['GET'])
def rota():
    resultado, link_google_maps = otimizar_rota()
    return render_template('index.html', locais_entrega_temp=locais_entrega_temp, resultado=resultado, link_google_maps=link_google_maps)


if __name__ == '__main__':
    app.run(debug=True)
