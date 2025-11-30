import sys
from ply import lex, yacc


tokens = (
    "DISPOSITIVOS", "FIMDISPOSITIVOS",
    "DEF", "QUANDO", "SENAO",
    "EXECUTE", "EM",
    "LIGAR", "DESLIGAR",
    "ALERTA", "PARA",
    "DIFUNDIR",
    "AND",
    "OP_LOGIC",
    "ARROW",
    "NUM",
    "BOOL",
    "MSG",
    "ID",
)

# Ignorar espaços e tabs
t_ignore = " \t"

# Operadores lógicos
t_OP_LOGIC = r'==|!=|>=|<=|>|<'

# ARROW
t_ARROW = r'->'

# Literais diretos
literals = [':', '[', ']', ',', ';', '=']


reserved = {
    "dispositivos": "DISPOSITIVOS",
    "fimdispositivos": "FIMDISPOSITIVOS",
    "def": "DEF",
    "quando": "QUANDO",
    "senao": "SENAO",
    "execute": "EXECUTE",
    "em": "EM",
    "ligar": "LIGAR",
    "desligar": "DESLIGAR",
    "alerta": "ALERTA",
    "para": "PARA",
    "difundir": "DIFUNDIR",
    "and": "AND",
    "true": "BOOL",
    "false": "BOOL",
}

def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value.lower(), "ID")
    return t

def t_NUM(t):
    r"\d+"
    t.value = int(t.value)
    return t

def t_BOOL(t):
    r"TRUE|FALSE|true|false"
    t.value = t.value.lower() == "true"
    return t

def t_MSG(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'\#.*'
    pass

def t_error(t):
    print(f"Erro lexico: {t.value[0]}")
    t.lexer.skip(1)


lexer = lex.lex()


def p_programa(p):
    """programa : sec_dev sec_cmd"""
    p[0] = (p[1], p[2])

def p_sec_dev(p):
    """sec_dev : DISPOSITIVOS ':' lista_devices FIMDISPOSITIVOS"""
    p[0] = p[3]

def p_lista_devices_rec(p):
    """lista_devices : linha_device lista_devices"""
    p[0] = [p[1]] + p[2]

def p_lista_devices_base(p):
    """lista_devices : linha_device"""
    p[0] = [p[1]]

def p_linha_device_1(p):
    """linha_device : ID"""
    p[0] = (p[1], None)

def p_linha_device_2(p):
    """linha_device : ID '[' ID ']'"""
    p[0] = (p[1], p[3])

def p_sec_cmd(p):
    """sec_cmd : lista_cmd"""
    p[0] = p[1]

def p_lista_cmd_rec(p):
    """lista_cmd : cmd ';' lista_cmd"""
    p[0] = [p[1]] + p[3]

def p_lista_cmd_base(p):
    """lista_cmd : cmd ';'"""
    p[0] = [p[1]]

def p_cmd(p):
    """cmd : atribuicao
           | obsv_acao
           | acao"""
    p[0] = p[1]

def p_atribuicao(p):
    """atribuicao : DEF ID '=' valor"""
    p[0] = ("atribuicao", p[2], p[4])

def p_obsv_acao_if(p):
    """obsv_acao : QUANDO observacao ':' acao"""
    p[0] = ("if", p[2], p[4])

def p_obsv_acao_if_else(p):
    """obsv_acao : QUANDO observacao ':' acao SENAO acao"""
    p[0] = ("ifelse", p[2], p[4], p[6])

def p_observacao_simples(p):
    """observacao : ID OP_LOGIC valor"""
    p[0] = ("cond", p[1], p[2], p[3])

def p_observacao_and(p):
    """observacao : ID OP_LOGIC valor AND observacao"""
    p[0] = ("and", ("cond", p[1], p[2], p[3]), p[5])

def p_valor_num(p):
    """valor : NUM"""
    p[0] = p[1]

def p_valor_bool(p):
    """valor : BOOL"""
    p[0] = p[1]

def p_valor_id(p):
    """valor : ID"""
    p[0] = p[1]

def p_acao_ligar(p):
    """acao : EXECUTE LIGAR EM ID"""
    p[0] = ("ligar", p[4])

def p_acao_desligar(p):
    """acao : EXECUTE DESLIGAR EM ID"""
    p[0] = ("desligar", p[4])

def p_acao_alerta_1(p):
    """acao : ALERTA PARA ID ':' MSG"""
    p[0] = ("alerta1", p[3], p[5])

def p_acao_alerta_2(p):
    """acao : ALERTA PARA ID ':' MSG ',' ID"""
    p[0] = ("alerta2", p[3], p[5], p[7])

def p_acao_difundir_1(p):
    """acao : DIFUNDIR ':' MSG ARROW '[' lista_ids ']'"""
    p[0] = ("diff1", p[3], p[6])

def p_acao_difundir_2(p):
    """acao : DIFUNDIR ':' MSG ID ARROW '[' lista_ids ']'"""
    p[0] = ("diff2", p[3], p[4], p[7])

def p_lista_ids_unico(p):
    """lista_ids : ID"""
    p[0] = [p[1]]

def p_lista_ids_multi(p):
    """lista_ids : ID ',' lista_ids"""
    p[0] = [p[1]] + p[3]

def p_error(p):
    print("Erro sintatico!")


# GERAÇÃO DE C 

def gerar_cabecalho():
    cab = []
    cab.append("#include <stdio.h>")
    cab.append("#include <string.h>")
    cab.append("")
    cab.append("void ligar(char* id) {")
    cab.append('    printf("%s ligado!\\n", id);')
    cab.append("}")
    cab.append("")
    cab.append("void desligar(char* id) {")
    cab.append('    printf("%s desligado!\\n", id);')
    cab.append("}")
    cab.append("")
    cab.append("void alerta(char* id, char* msg) {")
    cab.append('    printf("%s recebeu o alerta: %s\\n", id, msg);')
    cab.append("}")
    cab.append("")
    cab.append("void alerta_var(char* id, char* msg, char* var) {")
    cab.append('    printf("%s recebeu o alerta: %s %s\\n", id, msg, var);')
    cab.append("}")
    cab.append("")
    return "\n".join(cab)


# gerar variaveis:

def gerar_variavel(node):
    # node = ("atribuicao", nome, valor)
    _, nome, valor = node

    # valor pode ser NUM (int), BOOL (True/False), ID (variável)
    if isinstance(valor, bool):
        valor_c = "1" if valor else "0"
    else:
        valor_c = str(valor)

    return f"int {nome} = {valor_c};"


def gerar_acao_ligar(node):
    # node = ("ligar", id_do_dispositivo)
    _, nome = node
    return f'ligar("{nome}");'

def gerar_acao_desligar(node):
    # node = ("desligar", id_do_dispositivo)
    _, nome = node
    return f'desligar("{nome}");'


def gerar_alerta1(node):
    # node = ("alerta1", id, msg)
    _, dispositivo, msg = node
    return f'alerta("{dispositivo}", "{msg}");'

def gerar_alerta2(node):
    # node = ("alerta2", id, msg, var)
    _, dispositivo, msg, var = node
    return f'alerta_var("{dispositivo}", "{msg}", {var});'

def gerar_condicao(node):
    tipo = node[0]

    # ("cond", id, op, valor)
    if tipo == "cond":
        _, ident, op, valor = node
        if isinstance(valor, bool):
            valor_c = "1" if valor else "0"
        else:
            valor_c = str(valor)
        return f"{ident} {op} {valor_c}"

    # ("and", cond1, cond2)
    if tipo == "and":
        _, c1, c2 = node
        return f"({gerar_condicao(c1)}) && ({gerar_condicao(c2)})"

    return "/* condicao_invalida */"

def gerar_if(node):
    _, cond, acao = node

    cond_c = gerar_condicao(cond)

    # gerar o código da ação interna
    if acao[0] == "ligar":
        acao_c = gerar_acao_ligar(acao)
    elif acao[0] == "desligar":
        acao_c = gerar_acao_desligar(acao)
    elif acao[0] == "alerta1":
        acao_c = gerar_alerta1(acao)
    elif acao[0] == "alerta2":
        acao_c = gerar_alerta2(acao)
    else:
        acao_c = f"// acao ainda nao implementada: {acao}"

    bloco = []
    bloco.append(f"if ({cond_c}) {{")
    bloco.append(f" {acao_c}")
    bloco.append("}")
    return "\n".join(bloco)


def gerar_ifelse(node):
    _, cond, acao1, acao2 = node

    cond_c = gerar_condicao(cond)

    # ação do IF
    if acao1[0] == "ligar":
        a1 = gerar_acao_ligar(acao1)
    elif acao1[0] == "desligar":
        a1 = gerar_acao_desligar(acao1)
    elif acao1[0] == "alerta1":
        a1 = gerar_alerta1(acao1)
    elif acao1[0] == "alerta2":
        a1 = gerar_alerta2(acao1)
    else:
        a1 = f"// acao nao implementada: {acao1}"

    # ação do ELSE
    if acao2[0] == "ligar":
        a2 = gerar_acao_ligar(acao2)
    elif acao2[0] == "desligar":
        a2 = gerar_acao_desligar(acao2)
    elif acao2[0] == "alerta1":
        a2 = gerar_alerta1(acao2)
    elif acao2[0] == "alerta2":
        a2 = gerar_alerta2(acao2)
    else:
        a2 = f"// acao nao implementada: {acao2}"

    bloco = []
    bloco.append(f"if ({cond_c}) {{")
    bloco.append(f"    {a1}")
    bloco.append("} else {")
    bloco.append(f"    {a2}")
    bloco.append("}")
    return "\n".join(bloco)


def gerar_diff1(node):
    # node = ("diff1", msg, lista_ids)
    _, msg, ids = node
    linhas = []
    for dispositivo in ids:
        linhas.append(f'alerta("{dispositivo}", "{msg}");')
    return "\n".join(linhas)


def gerar_diff2(node):
    # node = ("diff2", msg, var, lista_ids)
    _, msg, var, ids = node
    linhas = []
    for dispositivo in ids:
        linhas.append(f'alerta_var("{dispositivo}", "{msg}", {var});')
    return "\n".join(linhas)


def validar_dispositivos(lista_dispositivos, lista_cmd):
    # cria um conjunto com nomes de dispositivos declarados
    nomes = {nome for (nome, attr) in lista_dispositivos}

    erros = []

    for cmd in lista_cmd:
        tipo = cmd[0]

        # AÇÕES SIMPLES
        if tipo in ("ligar", "desligar"):
            _, dispositivo = cmd
            if dispositivo not in nomes:
                erros.append(f"Dispositivo '{dispositivo}' nao existe.")

        # ALERTA1
        elif tipo == "alerta1":
            _, dispositivo, msg = cmd
            if dispositivo not in nomes:
                erros.append(f"Dispositivo '{dispositivo}' nao existe.")

        # ALERTA2
        elif tipo == "alerta2":
            _, dispositivo, msg, var = cmd
            if dispositivo not in nomes:
                erros.append(f"Dispositivo '{dispositivo}' nao existe.")

        # DIFUNDIR (lista)
        elif tipo == "diff1":
            _, msg, lista_ids = cmd
            for dispositivo in lista_ids:
                if dispositivo not in nomes:
                    erros.append(f"Dispositivo '{dispositivo}' nao existe.")

        elif tipo == "diff2":
            _, msg, var, lista_ids = cmd
            for dispositivo in lista_ids:
                if dispositivo not in nomes:
                    erros.append(f"Dispositivo '{dispositivo}' nao existe.")

        # IF e IFELSE — precisam validar ações internas
        elif tipo == "if":
            _, cond, acao = cmd
            erros.extend( validar_dispositivos([], [acao]) )

        elif tipo == "ifelse":
            _, cond, acao1, acao2 = cmd
            erros.extend( validar_dispositivos([], [acao1]) )
            erros.extend( validar_dispositivos([], [acao2]) )

    return erros


def gerar_codigo(lista_cmd):
    linhas = []

    for cmd in lista_cmd:

        # ATRIBUIÇÃO
        if cmd[0] == "atribuicao":
            linhas.append(gerar_variavel(cmd))

        # LIGAR
        elif cmd[0] == "ligar":
            linhas.append(gerar_acao_ligar(cmd))

        # DESLIGAR
        elif cmd[0] == "desligar":
            linhas.append(gerar_acao_desligar(cmd))

        # ALERTA SIMPLES
        elif cmd[0] == "alerta1":
            linhas.append(gerar_alerta1(cmd))

        # ALERTA COM VARIÁVEL
        elif cmd[0] == "alerta2":
            linhas.append(gerar_alerta2(cmd))

        # IF
        elif cmd[0] == "if":
            linhas.append(gerar_if(cmd))

        # IF/ELSE
        elif cmd[0] == "ifelse":
            linhas.append(gerar_ifelse(cmd))

        # DIFUNDIR SIMPLES
        elif cmd[0] == "diff1":
            linhas.append(gerar_diff1(cmd))

        # DIFUNDIR COM VARIÁVEL
        elif cmd[0] == "diff2":
            linhas.append(gerar_diff2(cmd))

        else:
            linhas.append(f"// comando ainda nao implementado: {cmd}")

    return "\n".join(linhas)




#compilador:

parser = yacc.yacc()

def main():
    if len(sys.argv) < 2:
        print("Uso: python compilador.py arquivo.obs")
        return

    entrada = sys.argv[1]
    with open(entrada) as f:
        codigo = f.read()

    resultado = parser.parse(codigo)

    lista_dispositivos = resultado[0]
    lista_cmd = resultado[1]

    # extrazinho: validar dispositivos
    erros = validar_dispositivos(lista_dispositivos, lista_cmd)

    if erros:
        print("ERROS DE COMPILACAO:")
        for e in erros:
            print(" -", e)
        print("Nenhum arquivo C foi gerado.")
        return

    
    with open("saida.c", "w") as out:
        out.write(gerar_cabecalho())
        out.write("int main() {\n")

        codigo = gerar_codigo(lista_cmd)
        out.write("    " + codigo.replace("\n", "\n    ") + "\n")

        out.write("    return 0;\n")
        out.write("}\n")


    print("Arquivo saida.c criado com sucesso!")

if __name__ == "__main__":
    main()
