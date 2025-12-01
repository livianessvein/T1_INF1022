#include <stdio.h>
#include <string.h>

void ligar(char* id) {
    printf("%s ligado!\n", id);
}

void desligar(char* id) {
    printf("%s desligado!\n", id);
}

void alerta(char* id, char* msg) {
    printf("%s recebeu o alerta: %s\n", id, msg);
}

void alerta_var(char* id, char* msg, char* var) {
    printf("%s recebeu o alerta: %s %s\n", id, msg, var);
}
int main() {
    alerta_var("Termometro", "Temperatura esta em", temperatura);
    return 0;
}
