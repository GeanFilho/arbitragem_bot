# utils.py

def calcular_lucro(stakes):
    """
    Recebe a lista de stakes já calculadas,
    retorna o lucro líquido garantido em qualquer cenário.
    """
    total_investido = sum(s["stake"] for s in stakes)

    # como arbitragem é garantida, o retorno líquido é:
    # retorno de qualquer aposta - total investido
    retorno_qualquer = stakes[0]["return_if_win"]

    lucro = retorno_qualquer - total_investido

    return round(total_investido, 2), round(retorno_qualquer, 2), round(lucro, 2)
