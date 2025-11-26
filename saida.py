def ligar(id_device):
    print(f"{id_device} ligado!")

def desligar(id_device):
    print(f"{id_device} desligado!")

def alerta(id_device, msg):
    print(f"{id_device} recebeu o alerta:\n{msg}")

def alerta_var(id_device, msg, var):
    print(f"{id_device} recebeu o alerta:\n{msg} {var}")

dispositivos = ['Lampada']

potencia = 10

# Código traduzido:

potencia = 10
if (potencia > 5):
    ligar("Lampada")