import sys
from ply import lex, yacc

# =========================================================
# TOKENS
# =========================================================

tokens = (
    # Palavras-chave
    "DISPOSITIVOS", "FIMDISPOSITIVOS",
    "DEF", "QUANDO", "SENAO",
    "EXECUTE", "EM", "LIGAR", "DESLIGAR",
    "ALERTA", "PARA", "DIFUNDIR",
    "AND",

    # Operadores, literais especiais
    "OP_LOGIC", "ARROW",

    # Valores
    "NUM", "BOOL", "MSG",

    # Identificadores genéricos (ID_DEVICE e ID_OBS no parser)
    "ID",
)

# Regex dos tokens simples
t_OP_LOGIC = r'==|!=|>=|<=|>|<'
t_ARROW = r'->'
t_ignore = ' \t'

# Literais
literals = [':', '[', ']', ',', '=', ';']

# =========================================================
# PALAVRAS-RESERVADAS
# =========================================================

reserved_map = {
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


# =========================================================
# EXPRESSÕES REGULARES
# =========================================================

def t_MSG(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

def t_BOOL(t):
    r'TRUE|FALSE'
    t.value = True if t.value == "TRUE" else False
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    lower = t.value.lower()
    if lower in reserved_map:
        t.type = reserved_map[lower]
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'\#.*'
    pass

def t_error(t):
    print(f"Erro léxico: caractere inválido '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# =========================================================
# ESTRUTURAS DE CONTROLE
# =========================================================

dispositivos = []
obs_def = {}    # {nome: valor}
obs_uso = set() # variáveis observadas

def indent(code, n=4):
    esp = ' ' * n
    return "\n".join(esp + linha if linha.strip() else linha for linha in code.splitlines())


# =========================================================
# GRAMÁTICA E AÇÕES SEMÂNTICAS
# =========================================================

def p_programa(p):
    '''programa : sec_dev sec_cmd'''
    
    # Cabeçalho Python com as funções obrigatórias
    out = [
        "def ligar(id_device):",
        "    print(f\"{id_device} ligado!\")\n",
        "def desligar(id_device):",
        "    print(f\"{id_device} desligado!\")\n",
        "def alerta(id_device, msg):",
        "    print(f\"{id_device} recebeu o alerta:\\n{msg}\")\n",
        "def alerta_var(id_device, msg, var):",
        "    print(f\"{id_device} recebeu o alerta:\\n{msg} {var}\")\n",
        f"dispositivos = {dispositivos!r}\n"
    ]

    # Variáveis observadas
    for nome, val in obs_def.items():
        out.append(f"{nome} = {val}")
    for nome in obs_uso:
        if nome not in obs_def:
            out.append(f"{nome} = 0")

    out.append("\n# Código traduzido:\n")
    out.append(p[2])
    p[0] = "\n".join(out)


# ======== dispositivos ========

def p_sec_dev(p):
    '''sec_dev : DISPOSITIVOS ':' lista_devices FIMDISPOSITIVOS'''
    pass

def p_lista_devices_rec(p):
    '''lista_devices : linha_device lista_devices'''
    pass

def p_lista_devices_base(p):
    '''lista_devices : linha_device'''
    pass

def p_linha_device1(p):
    '''linha_device : ID'''
    dispositivos.append(p[1])

def p_linha_device2(p):
    '''linha_device : ID '[' ID ']' '''
    dispositivos.append(p[1])
    obs_uso.add(p[3])


# ======== comandos ========

def p_sec_cmd(p):
    '''sec_cmd : lista_cmd'''
    p[0] = p[1]

def p_lista_cmd_rec(p):
    '''lista_cmd : cmd ';' lista_cmd'''
    p[0] = p[1] + "\n" + p[3]

def p_lista_cmd_base(p):
    '''lista_cmd : cmd ';' '''
    p[0] = p[1]

def p_cmd(p):
    '''cmd : atribuicao
           | obsv_acao
           | acao'''
    p[0] = p[1]


# ======== atribuição ========

def p_atribuicao(p):
    '''atribuicao : DEF ID '=' valor'''
    nome = p[2]
    expr = p[4]
    obs_def[nome] = expr
    obs_uso.add(nome)
    p[0] = f"{nome} = {expr}"


# ======== quando ========

def p_obsv_acao_simples(p):
    '''obsv_acao : QUANDO observacao ':' acao'''
    p[0] = f"if {p[2]}:\n{indent(p[4])}"

def p_obsv_acao_senao(p):
    '''obsv_acao : QUANDO observacao ':' acao SENAO acao'''
    p[0] = f"if {p[2]}:\n{indent(p[4])}\nelse:\n{indent(p[6])}"


# ======== observações ========

def p_observacao_simples(p):
    '''observacao : ID OP_LOGIC valor'''
    obs_uso.add(p[1])
    p[0] = f"({p[1]} {p[2]} {p[3]})"

def p_observacao_and(p):
    '''observacao : ID OP_LOGIC valor AND observacao'''
    obs_uso.add(p[1])
    p[0] = f"({p[1]} {p[2]} {p[3]}) and {p[5]}"


# ======== valores ========

def p_valor_num(p):
    '''valor : NUM'''
    p[0] = str(p[1])

def p_valor_bool(p):
    '''valor : BOOL'''
    p[0] = "True" if p[1] else "False"

def p_valor_id(p):
    '''valor : ID'''
    obs_uso.add(p[1])
    p[0] = p[1]


# ======== ações ========

def p_acao_ligar(p):
    '''acao : EXECUTE LIGAR EM ID'''
    p[0] = f'ligar("{p[4]}")'

def p_acao_desligar(p):
    '''acao : EXECUTE DESLIGAR EM ID'''
    p[0] = f'desligar("{p[4]}")'

def p_acao_alerta1(p):
    '''acao : ALERTA PARA ID ':' MSG'''
    p[0] = f'alerta("{p[3]}", {p[5]!r})'

def p_acao_alerta2(p):
    '''acao : ALERTA PARA ID ':' MSG ',' ID'''
    obs_uso.add(p[7])
    p[0] = f'alerta_var("{p[3]}", {p[5]!r}, {p[7]})'

def p_acao_difundir1(p):
    '''acao : DIFUNDIR ':' MSG ARROW '[' lista_ids ']' '''
    lista = p[6]
    p[0] = f"for dev in {lista}:\n    alerta(dev, {p[3]!r})"

def p_acao_difundir2(p):
    '''acao : DIFUNDIR ':' MSG ID ARROW '[' lista_ids ']' '''
    obs_uso.add(p[4])
    lista = p[7]
    p[0] = f"for dev in {lista}:\n    alerta_var(dev, {p[3]!r}, {p[4]})"


def p_lista_ids_unico(p):
    '''lista_ids : ID'''
    p[0] = [p[1]]

def p_lista_ids_multi(p):
    '''lista_ids : ID ',' lista_ids'''
    p[0] = [p[1]] + p[3]


# ======== erro sintático ========

def p_error(p):
    if p is None:
        print("Erro de sintaxe: fim inesperado.")
    else:
        print(f"Erro de sintaxe perto de '{p.value}' na linha {p.lineno}")


# =========================================================
# PARSER
# =========================================================

parser = yacc.yacc()


# =========================================================
# EXECUÇÃO
# =========================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python obsact_compiler.py entrada.obs [saida.py]")
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else "saida.py"

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            code = f.read()

        result = parser.parse(code)
        if result:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Arquivo gerado em: {output_path}")
        else:
            print("Erro: Nenhuma saída foi produzida.")

    except Exception as e:
        print("Erro:", e)


if __name__ == "__main__":
    main()
