import googlemaps

# Substitua 'SUA_CHAVE_DE_API' pela chave de API que você obteve
chave_api = 'AIzaSyAGDNNmzbgBpZFCF5GNm9nMzLv_2lNeygw'

# Inicialize a API do Google Maps
cliente = googlemaps.Client(key=chave_api)

# Defina os locais de entrega como coordenadas (latitude, longitude)
locais_entrega = [
    (-23.717328052327055, -46.568369082682636),
    (-23.698637281458257, -46.55062976452177),
    # Adicione mais locais de entrega conforme necessário
]

# O local de partida (geralmente o depósito)
local_partida = (-23.694191776643493, -46.605377959371594)

# O local de chegada (destino final)
# Substitua pelas coordenadas reais
local_chegada = (-23.694191776643493, -46.605377959371594)

# Crie uma lista de destinos a partir dos locais de entrega
destinos = [str(local[0]) + ',' + str(local[1]) for local in locais_entrega]

# Adicione o local de partida como o primeiro destino
destinos.insert(0, str(local_partida[0]) + ',' + str(local_partida[1]))

# Adicione o local de chegada como o último destino
destinos.append(str(local_chegada[0]) + ',' + str(local_chegada[1]))

# Faça a solicitação de direções otimizadas
rota_otimizada = cliente.directions(
    origin=str(local_partida[0]) + ',' + str(local_partida[1]),
    destination=str(local_chegada[0]) + ',' + str(local_chegada[1]),
    mode='driving',
    # Exclua o primeiro (partida) e o último (chegada) destinos
    waypoints=destinos[1:-1],
    optimize_waypoints=True  # Isso otimizará a ordem das entregas
)

# Verifique se há uma rota otimizada
if rota_otimizada:
    # Crie o link para o Google Maps com a rota
    link_google_maps = 'https://www.google.com/maps/dir/?api=1&origin=' + str(local_partida[0]) + ',' + str(
        local_partida[1]) + '&destination=' + str(local_chegada[0]) + ',' + str(local_chegada[1]) + '&waypoints=' + '|'.join(destinos[1:-1])

    print(f"Link para a rota otimizada: {link_google_maps}")

    distancia_total = rota_otimizada[0]['legs'][0]['distance']['text']
    tempo_total = rota_otimizada[0]['legs'][0]['duration']['text']
    ordem_entrega_otimizada = rota_otimizada[0]['waypoint_order']

    # Exiba a ordem otimizada de entregas
    print("Ordem otimizada de entregas:")
    for i, indice in enumerate(ordem_entrega_otimizada):
        print(f"{i + 1}. Entrega {locais_entrega[indice]}")

    print(f"Tempo Total: {tempo_total}")
else:
    print("Não foi possível encontrar uma rota otimizada.")
