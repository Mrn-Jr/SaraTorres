from datetime import datetime, timedelta

def buscar_horarios_livres(data_str, duracao_minutos, agendamentos_dia, regras_disponibilidade):
    """
    Calcula os horários disponíveis para um serviço num dia específico.
    
    :param data_str: String da data (ex: '2026-06-20')
    :param duracao_minutos: Duração do serviço escolhido em minutos (ex: 60)
    :param agendamentos_dia: Lista de dicionários com agendamentos já marcados no dia
    :param regras_disponibilidade: Dicionário com horário de 'trabalho' e 'bloqueios' (ex: almoço)
    :return: Lista de strings com os horários de início disponíveis
    """
    
    # 1. Definir horário de funcionamento (Exemplo: 09:00 às 18:00)
    hora_abertura = datetime.strptime(f"{data_str} {regras_disponibilidade['trabalho']['inicio']}", "%Y-%m-%d %H:%M")
    hora_fecho = datetime.strptime(f"{data_str} {regras_disponibilidade['trabalho']['fim']}", "%Y-%m-%d %H:%M")
    
    # 2. Definir o bloqueio de almoço
    almoco_inicio = datetime.strptime(f"{data_str} {regras_disponibilidade['bloqueio']['inicio']}", "%Y-%m-%d %H:%M")
    almoco_fim = datetime.strptime(f"{data_str} {regras_disponibilidade['bloqueio']['fim']}", "%Y-%m-%d %H:%M")

    horarios_disponiveis = []
    
    # Vamos testar a agenda em blocos de 30 em 30 minutos
    hora_atual = hora_abertura
    passo = timedelta(minutes=30)
    duracao_servico = timedelta(minutes=duracao_minutos)

    while hora_atual + duracao_servico <= hora_fecho:
        fim_estimado = hora_atual + duracao_servico
        conflito = False

        # Regra A: Verificar se o serviço bate na hora de almoço
        if (hora_atual < almoco_fim) and (fim_estimado > almoco_inicio):
            conflito = True

        # Regra B: Prevenção de conflitos contínua com outros agendamentos
        if not conflito:
            for agendamento in agendamentos_dia:
                agend_inicio = datetime.strptime(agendamento['inicio'], "%Y-%m-%d %H:%M")
                agend_fim = datetime.strptime(agendamento['fim'], "%Y-%m-%d %H:%M")
                
                # Se o horário atual ou o fim estimado se sobrepuserem a uma marcação existente
                if (hora_atual < agend_fim) and (fim_estimado > agend_inicio):
                    conflito = True
                    break # Para de verificar os outros, pois já achou um conflito

        # Se não houve nenhum conflito e couber na agenda, este é um horário livre!
        if not conflito:
            horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
            
        hora_atual += passo

    return horarios_disponiveis

# ---------------------------------------------------------
# Teste Rápido (Apenas para simular como a API vai usar)
# ---------------------------------------------------------
if __name__ == '__main__':
    # Simulando um "Design com Henna" que demora 60 minutos
    duracao = 60 
    
    regras = {
        'trabalho': {'inicio': '09:00', 'fim': '18:00'},
        'bloqueio': {'inicio': '12:00', 'fim': '13:00'} # Hora de almoço
    }
    
    # Simulando que já existe uma cliente marcada às 14:00 (Demorou 60 min, vai até às 15:00)
    agendamentos = [
        {'inicio': '2026-06-20 14:00', 'fim': '2026-06-20 15:00'}
    ]
    
    livres = buscar_horarios_livres('2026-06-20', duracao, agendamentos, regras)
    print(f"Horários livres para o serviço de {duracao} minutos:")
    print(livres)