import spacy
from spacy_layout import spaCyLayout
import pandas as pd
import re
from unidecode import unidecode

def norm(s):
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', unidecode(str(s)).strip().lower())

field_map = {
    'POTENCIA': ['(cv)', 'potencia (cv)', 'potência (cv)', 'potencia cv', 'potência cv', 'potencia'],
    'NORMA DE REFERENCIA': ['referência', 'norma de referência', 'norma referencia', 'norma'],
    'CILINDROS': ['cilindros (unidades)', 'cilindros', '(unidades)', 'nº cilindros', 'numero de cilindros'],
    'ASPIRACAO': ['aspiração', 'aspiracao', 'aspiracao do motor'],
    'INJECAO': ['injecao', 'injeção', 'sistema de injecao'],
    'TIPO': ['tipo', 'tipo do motor', 'tipo de transmissão', 'tipo de transmissao'],
    'FRENTE X RE': ['frente x re', 'frente x ré', 'frente x re (mm)'],
    'TIPO EMBREAGEM': ['embreagem tipo', 'tipo embreagem', 'embreagem'],
    'TRACAO': ['tracao', 'tração', 'traçao'],
    'TDP': ['(rpm)', 'tdp', 'tdp (rpm)', 'rotacao (rpm)', 'rotação (rpm)'],
    'VAZAO HIDRAULICO': ['(l/min)', 'vazao hidraulico', 'vazão hidráulico', 'vazao do hidraulico', 'vazão do hidráulico'],
    'VALVULAS CONTROLE': ['(nº)', 'valvulas controle remoto', 'válvulas controle remoto', 'valvulas', 'vávulas controle'],
    'VAZAO CONTROLE ': ['vazao controle remoto', 'vazão controle remoto', 'vazao controle'],
    'CAPACIDADE LEVANTE': ['capacidade levante', 'capacidade de levante', 'capacidade de levantamento', 'capacidade levante (kgf)'],
    'ALTURA(MM)': ['altura (mm)', 'altura mm', 'altura'],
    'ENTRE EIXOS(MM)': ['Entre eixos (mm)', 'entre eixos mm', 'entre eixos', 'eixos (mm)'],
    'VAO LIVRE': ['vao livre', 'vão livre', 'vao livre (mm)'],
    'PESO': ['peso (kg)', 'peso', 'peso (kg), Peso, Peso (kg)'],
    'TANQUE': ['tanque (l)', 'tanque', 'tanque (l)'],
    'POSTO DE OPERACAO': ['posto de operacao', 'Posto de Operação', 'posto de trabalho', 'Operação', 'Operacao', 'Operaçao'],
    'NOME': ['nome', 'nome do trator', 'modelo', 'marca modelo', 'marca / modelo']
}

# cria lista única de rótulos normalizados para detecção rápida
_all_labels = set()
for labels in field_map.values():
    for lbl in labels:
        _all_labels.add(norm(lbl))

def is_label_like(s):
    """Retorna True se a célula parece ser um rótulo/cabeçalho (contém/prefixa rótulos conhecidos)."""
    if s is None:
        return False
    s_n = norm(s)
    if not s_n:
        return False
    # se a célula contém muitos tokens de rótulo ou começa com um rótulo
    for lbl in _all_labels:
        if lbl and (s_n.startswith(lbl) or lbl in s_n):
            return True
    # também considera provável rótulo se a célula é curta e contém apenas palavras comuns de rótulos
    if len(s_n) < 20 and any(tok in s_n for tok in ('potencia','cilindros','aspir','injec','tipo','frente','tdp','vazao','press','valvul','capacidade')):
        return True
    return False

def is_value_like(s):
    """Verificar se uma célula parece conter um valor útil (não cabeçalho)."""
    if s is None:
        return False
    s_n = norm(s)
    if not s_n:
        return False
    if is_label_like(s):
        return False
    # considera valor se tiver dígitos ou se for uma string não-trivial (>2 chars)
    if re.search(r'\d', s_n):
        return True
    if len(s_n) > 2:
        return True
    return False

def find_field(df, candidates):
    """
    Procura por qualquer candidato (lista de strings) na tabela df e retorna
    valor à direita do rótulo quando encontrado. Retorna 'ND' caso não ache.
    Evita devolver células que sejam rótulos/headers.
    """
    rows, cols = df.shape
    # passa por cada candidato (normalizado)
    for cand in candidates:
        ncand = norm(cand)
        if not ncand:
            continue
        for r in range(rows):
            for c in range(cols):
                try:
                    cell_raw = df.iat[r, c]
                except Exception:
                    cell_raw = None
                if pd.isna(cell_raw) or cell_raw is None:
                    continue
                cell = norm(cell_raw)
                if not cell:
                    continue
                # verifica ocorrência do candidato na célula
                if ncand in cell or re.search(r'\b' + re.escape(ncand) + r'\b', cell):
                    # 1) tenta células à direita na mesma linha (offsets)
                    for offset in (1, 2, 3):
                        cc = c + offset
                        if cc < cols:
                            try:
                                val_raw = df.iat[r, cc]
                            except Exception:
                                val_raw = None
                            if not pd.isna(val_raw) and val_raw is not None and is_value_like(val_raw):
                                return val_raw
                    # 2) tenta linhas abaixo na mesma coluna e colunas próximas
                    for rr in range(r + 1, min(rows, r + 5)):
                        for cc in range(max(0, c - 1), min(cols, c + 3)):
                            try:
                                val_raw = df.iat[rr, cc]
                            except Exception:
                                val_raw = None
                            if not pd.isna(val_raw) and val_raw is not None and is_value_like(val_raw):
                                return val_raw
                    # 3) extrai após ":" na própria célula (ex: "Potência: 80 cv")
                    m = re.search(r'[:\-\s]+(.+)$', str(cell_raw).strip())
                    if m:
                        candidate_val = m.group(1).strip()
                        if candidate_val and not is_label_like(candidate_val):
                            return candidate_val
                    # 4) se chegou aqui e encontrou apenas rótulo (header), tentar procurar na linha seguinte na mesma coluna
                    if r + 1 < rows:
                        try:
                            val_raw = df.iat[r + 1, c]
                        except Exception:
                            val_raw = None
                        if not pd.isna(val_raw) and val_raw is not None and is_value_like(val_raw):
                            return val_raw
    # tentativa alternativa: se cabeçalho na linha 0 possui candidato, procurar primeira célula não-rótulo na coluna abaixo
    if rows > 1:
        for c in range(cols):
            try:
                header_cell = df.iat[0, c]
            except Exception:
                header_cell = None
            if header_cell is None or pd.isna(header_cell):
                continue
            header = norm(header_cell)
            for cand in candidates:
                if norm(cand) in header:
                    # procurar primeira linha abaixo com valor nessa coluna ou colunas adjacentes
                    for rr in range(1, min(rows, 6)):
                        for cc in range(max(0, c - 1), min(cols, c + 3)):
                            try:
                                val_raw = df.iat[rr, cc]
                            except Exception:
                                val_raw = None
                            if not pd.isna(val_raw) and val_raw is not None and is_value_like(val_raw):
                                return val_raw
    return 'ND'

def extract_name(df):
    """Heurística para extrair o nome do trator procurando nas primeiras linhas/células."""
    rows, cols = df.shape
    # 1) primeira linha: escolher a célula mais longa e não-label
    if rows >= 1:
        first_row = []
        for c in range(cols):
            try:
                first_row.append(df.iat[0, c])
            except Exception:
                first_row.append(None)
        candidates = [str(x).strip() for x in first_row if x and len(str(x).strip()) > 2 and not is_label_like(x)]
        if candidates:
            cand = max(candidates, key=len)
            m = re.match(r'^\s*([^:]{1,40})[:\-]\s*(.+)$', cand)
            if m and len(m.group(2).strip()) > 1:
                return m.group(2).strip()
            return cand
    # 2) posições comuns (0,1),(0,0),(1,0),(1,1)
    for r, c in ((0, 1), (0, 0), (1, 0), (1, 1)):
        if r < rows and c < cols:
            try:
                val = df.iat[r, c]
            except Exception:
                val = None
            if val and len(str(val).strip()) > 2 and not is_label_like(val):
                return str(val).strip()
    # 3) procurar nas 3 primeiras linhas a primeira célula significativa que não seja rótulo
    for r in range(min(3, rows)):
        for c in range(cols):
            try:
                val = df.iat[r, c]
            except Exception:
                val = None
            if val and len(str(val).strip()) > 2 and not is_label_like(val):
                return str(val).strip()
    # 4) fallback: procurar por mapping 'NOME'
    return find_field(df, field_map['NOME'])

def parse_int_or_nd(val):
    """
    Retorna uma string contendo apenas o inteiro encontrado em val ou 'ND'.
    Regras:
    - Se val for None ou 'ND' (qualquer case) -> 'ND'
    - Se contiver um decimal (ex.: '12.5' ou '12,5') -> 'ND'
    - Caso contenha um inteiro junto de unidades ('80 cv', '  120 mm') -> retorna '80' ou '120'
    - Caso não consiga extrair inteiro -> 'ND'
    """
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s:
        return 'ND'
    if s.strip().upper() == 'ND':
        return 'ND'
    # Se existe padrão decimal (dígito . ou , dígito) -> rejeitar
    if re.search(r'\d[.,]\d', s):
        return 'ND'
    # extrai o primeiro inteiro encontrado
    m = re.search(r'(-?\d+)', s)
    if m:
        return m.group(1)
    return 'ND'

def normalize_tipoEmbreagem(val):
    """
    Normaliza o campo 'tipo de embreagem' para um dos valores permitidos:
    Disco simples, Monodisco seco, Seca, Multidisco úmida, PermaClutchTM,
    Multidisco, Cerametálico, Disco duplo a seco, Simples a seco, Brake to Clutch
    """
    if val is None:
        return 'ND'
    s = norm(val)
    if not s:
        return 'ND'
    if s.upper() == 'ND':
        return 'ND'
    
    # mapeamento com prioridade (mais específicos primeiro)
    mappings = [
        (['brake to clutch', 'brake clutch'], 'Brake to Clutch'),
        (['permaclachtm', 'permaclutch'], 'PermaClutchTM'),
        (['disco duplo a seco', 'duplo seco', 'disco duplo'], 'Disco duplo a seco'),
        (['simples a seco', 'simples seco'], 'Simples a seco'),
        (['disco simples'], 'Disco simples'),
        (['monodisco seco', 'mono disco seco', 'Monodisco a seco', 'Monodisco a seco', 'monodisco a seco'], 'Monodisco a seco'),
        (['multidisco umida', 'multidisco úmida', 'multi disco umida'], 'Multidisco úmida'),
        (['multidisco', 'multi disco'], 'Multidisco'),
        (['cerametalico', 'cerametálico', 'cera metalico'], 'Cerametálico'),
        (['seca', 'Seca'], 'Seca'),
        (['disco duplo'], 'Disco duplo'),
        (['disco duplo independente'], 'Disco duplo independente'),
        (['Disco cerametálico-seco', 'disco cerametálico-seco', 'disco cerametalico-seco'], 'Disco cerametálico-seco'),
        (['Disco cerametálico-duplo estágio', 'disco cerametalico-duplo estagio'], 'Disco cerametálico-duplo estágio'),
        (['Hidrostática', 'hidrostatica', 'hidrostatica'], 'Hidrostática'),
        (['Multidisco a óleo', 'multidisco a oleo', 'multidisco a óleo'], 'Multidisco a óleo'),
        (['disco duplo independente', 'Disco duplo independente'], 'Disco duplo independente'),
        (['discoseco simples', 'disco seco simples', 'disco seco si'], 'Disco seco simples'),
        (['Dupla a Seco', 'dupla a seco'], 'Dupla a Seco'),
        (['Disco seco', 'disco seco'], 'Disco seco')
    ]
    
    # verifica cada mapeamento na ordem (mais específico primeiro)
    for keywords, canonical in mappings:
        for kw in keywords:
            if kw in s:
                return canonical
    
    return 'ND'

def normalize_posto(val):
    """
    Normaliza o campo 'posto de operação' para um dos valores permitidos:
    ND, Acavalado, Plataformado, Semiplataformado, Cabinado, Semiacavalado
    """
    allowed = {
        'acavalado': 'Acavalado',
        'plataformado': 'Plataformado',
        'plataforma': 'Plataformado',
        'semiplataformado': 'Semiplataformado',
        'semi-plataformado': 'Semiplataformado',
        'cabinado': 'Cabinado',
        'semiacavalado': 'Semiacavalado',
        'semi-acavalado': 'Semiacavalado'
    }
    if val is None:
        return 'ND'
    s = norm(val)
    if not s:
        return 'ND'
    if s.upper() == 'ND':
        return 'ND'
    # busca palavra-chave no valor normalizado
    for key, canon in allowed.items():
        if key in s:
            return canon
    # algumas variações diretas
    if 'acaval' in s:
        return 'Acavalado'
    if 'plataform' in s or 'plataformado' in s:
        return 'Plataformado'
    if 'cabina' in s or 'cabin' in s:
        return 'Cabinado'
    # fallback ND
    return 'ND'

# --- novos helpers para potencia, tdp, tipo, peso e aspiração/injeção ---
def parse_potencia(val):
    """Retorna float (string) se potência estiver no intervalo [14.7, 830], senão 'ND'."""
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s:
        return 'ND'
    if s.strip().upper() == 'ND':
        return 'ND'
    # extrai número (aceita decimais)
    m = re.search(r'(-?\d+[.,]?\d*)', s)
    if not m:
        return 'ND'
    num = float(m.group(1).replace(',', '.'))
    if 14.7 <= num <= 830:
        # potência final como float (string com ponto decimal)
        return str(num)
    return 'ND'

def parse_cilindros(val):
    """Retorna inteiro em string se encontrar inteiro, senão 'ND'."""
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s:
        return 'ND'
    m = re.search(r'(-?\d+)', s)
    if m:
        return m.group(1)
    return 'ND'

def parse_norma(val):
    """
    Mantém a string se aparentar ser uma norma (ISO, SAE, NBR, ECE, ou padrões como 97/68/EC),
    senão retorna 'ND'.
    """
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s:
        return 'ND'
    s_n = s.upper()
    # padrões esperados
    if re.search(r'\bISO\b', s_n) or re.search(r'\bSAE\b', s_n) or re.search(r'\bNBR\b', s_n) or re.search(r'\bECE\b', s_n):
        return s
    if re.search(r'\d{2,3}/\d{2,3}/[A-Z]{2,3}', s_n) or re.search(r'97/68/EC', s_n):
        return s
    # combinações como 'SAE J1995' ou 'ISO TR14396'
    if re.search(r'\bSAE\s*J?\d+', s_n) or re.search(r'\bISO\s*TR?\s*\d+', s_n):
        return s
    return 'ND'

_injecao_map = {
    'mec': 'Mecânica',
    'mecânica': 'Mecânica',
    'mecanica': 'Mecânica',
    'eletr': 'Eletrônica',
    'eletrônica': 'Eletrônica',
    'eletronica': 'Eletrônica'
}

def parse_injecao(val):
    """Mapeia injeção para 'Mecânica', 'Eletrônica' ou 'ND'."""
    if val is None:
        return 'ND'
    s = norm(val)
    if not s:
        return 'ND'
    for k, v in _injecao_map.items():
        if k in s:
            return v
    return 'ND'

def find_weight_by_units(df):
    """
    Busca em toda a tabela a primeira célula que contenha 'kg' ou 'kgf' com um número e retorna o inteiro.
    Retorna 'ND' se não achar.
    """
    rows, cols = df.shape
    for r in range(rows):
        for c in range(cols):
            try:
                cell = df.iat[r, c]
            except Exception:
                cell = None
            if cell is None or pd.isna(cell):
                continue
            s = str(cell)
            if re.search(r'\b(kg|kgf)\b', s, flags=re.I):
                m = re.search(r'(-?\d+)', s)
                if m:
                    return m.group(1)
    return 'ND'

# ajusta resolve_peso_tanque para não eliminar possibilidades legitimas
def resolve_peso_tanque(peso_raw, tanque_raw, df=None):
    """
    Tenta distinguir peso de tanque com heurísticas e fallback para varredura na tabela (df).
    """
    def has_liter(s):
        if s is None:
            return False
        return bool(re.search(r'\b(l|lt|litro|ltrs|l\/)\b', str(s), flags=re.I))
    def has_kg(s):
        if s is None:
            return False
        return bool(re.search(r'\b(kg|kgf)\b', str(s), flags=re.I))

    # se peso_raw nulo -> tentar buscar por kg na tabela
    if peso_raw is None or str(peso_raw).strip() == '':
        if df is not None:
            return find_weight_by_units(df)
        return 'ND'
    p = str(peso_raw).strip()
    t = '' if tanque_raw is None else str(tanque_raw).strip()

    # se peso contém unidade de litro -> provavelmente é tanque
    if has_liter(p):
        # mas ainda pode haver outro campo com kg na tabela
        if df is not None:
            return find_weight_by_units(df)
        return 'ND'
    # se peso tem kg explícito -> extrai inteiro
    if has_kg(p):
        m = re.search(r'(-?\d+)', p)
        if m:
            return m.group(1)
    # se peso igual tanque e tanque não tem kg -> tentar procurar kg na tabela
    if t and p == t and not has_kg(p):
        if df is not None:
            return find_weight_by_units(df)
        return 'ND'
    # extrai primeiro inteiro plausível e verifica heurística mínima
    m = re.search(r'(-?\d+)', p)
    if m:
        num = int(m.group(1))
        if abs(num) >= 30:  # reduzido pra aceitar tratores leves também
            return str(num)
    # fallback: procurar na tabela se fornecida
    if df is not None:
        return find_weight_by_units(df)
    return 'ND'


def parse_tdp(val):
    """
    Valida formatos de TDP aceitáveis:
    - números simples (540)
    - grupos com '/', ex: 540/750/1.000
    - sufixos tipo E, SE: 540E/540SE
    - permite pontos/vírgulas em milhares: 1.000
    Retorna string original (limpa) se válido, senão 'ND'.
    """
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s:
        return 'ND'
    if s.strip().upper() == 'ND':
        return 'ND'
    s_clean = s.replace(' ', '')
    # aceita grupos separados por '/', cada grupo: número possivelmente com '.' ou ',' e optional sufixo letters (E/SE)
    pattern = r'^[0-9]+(?:[.,][0-9]+)?(?:[A-Za-z]{0,3})(?:\/[0-9]+(?:[.,][0-9]+)?(?:[A-Za-z]{0,3}))*$'
    if re.match(pattern, s_clean):
        return s
    return 'ND'

_tipo_map = {
    'sincroniz': 'Sincronizada',
    'sincronizada': 'Sincronizada',
    'mecanic': 'Mecânica',
    'mecânica': 'Mecânica',
    'mecanica': 'Mecânica',
    'powershift': 'PowerShift',
    'full-powershift': 'Full-PowerShift',
    'full powershift': 'Full-PowerShift',
    'cv t': 'CVT',
    'cvt': 'CVT',
    'hidrost': 'Hidrostática',
    'hidrostática': 'Hidrostática',
    'hidrostatic': 'Hidrostática',
    'deslizant': 'Deslizante',
    'deslizante': 'Deslizante'
}

def normalize_tipo(val):
    """
    Mapeia valores livres para um dos tipos permitidos:
    Sincronizada, Mecânica, PowerShift, CVT, Full-PowerShift, Hidrostática, Deslizante
    Retorna 'ND' se não conseguir mapear.
    """
    if val is None:
        return 'ND'
    s = norm(val)
    if not s:
        return 'ND'
    # verifica por substring do mapa
    for k, v in _tipo_map.items():
        if k in s:
            return v
    # tokens isolados
    for token in s.split():
        for k, v in _tipo_map.items():
            if k in token:
                return v
    return 'ND'

def refine_aspiracao_injecao(asp_raw, inj_raw):
    """
    Evita que ASPIRACAO receba valores de INJECAO:
    - se aspiracao contém termos relacionados à injecção -> ND
    - se aspiracao == injecao -> aspiracao = ND
    - otherwise retorna aspiracao ou 'ND'
    """
    def contains_injec(s):
        if s is None:
            return False
        return bool(re.search(r'injec|injeç|injeção|injection', str(s), flags=re.I))
    a = asp_raw
    i = inj_raw
    # se aspiracao aparenta ser índice de injecção, rejeitar
    if contains_injec(a):
        return 'ND'
    # se aspiracao vazio -> ND
    if a is None or str(a).strip() == '':
        return 'ND'
    # se igual à injecao -> rejeitar para evitar duplicação
    if i is not None and str(a).strip() == str(i).strip():
        return 'ND'
    return a

def parse_numeric_field(val):
    """
    Extrai apenas o primeiro inteiro encontrado em val e retorna como string.
    Usado para campos que devem ser sempre inteiros: VAZAO CONTROLE, CAPACIDADE LEVANTE, TANQUE.
    Retorna 'ND' se não encontrar inteiro ou se val for None/vazio.
    """
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s or s.upper() == 'ND':
        return 'ND'
    m = re.search(r'(-?\d+)', s)
    if m:
        return m.group(1)
    return 'ND'

def validate_peso_threshold(val, min_threshold=1000):
    """
    Retorna o inteiro do peso (string) se for >= min_threshold.
    Caso contrário ou se inválido -> 'ND'.
    """
    if val is None:
        return 'ND'
    iv = parse_int_or_nd(val)
    if iv == 'ND':
        iv = parse_numeric_field(val)
    if iv == 'ND':
        return 'ND'
    try:
        num = abs(int(iv))
    except Exception:
        return 'ND'
    if num < min_threshold:
        return 'ND'
    return str(num)

def partition(arr, low, high, key_col):
    """
    Partição para quicksort. Separa elementos onde key_col != 'ND' dos que são 'ND'.
    Elementos com 'ND' ficam no final.
    """
    pivot_index = high
    i = low
    
    for j in range(low, high):
        if arr[j][key_col] != 'ND':
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    
    arr[i], arr[pivot_index] = arr[pivot_index], arr[i]
    return i

def quicksort(arr, low, high, key_col):
    """
    Quicksort para ordenar array baseado em uma coluna.
    Coloca elementos com 'ND' no final.
    """
    if low < high:
        pi = partition(arr, low, high, key_col)
        quicksort(arr, low, pi - 1, key_col)
        quicksort(arr, pi + 1, high, key_col)

def remove_nd_potencia_rows(dataframe):
    """
    Remove linhas onde a coluna 'POTENCIA' é 'ND' utilizando quicksort.
    Primeiro organiza o dataframe movendo linhas com potência 'ND' para o final,
    depois remove essas linhas.
    
    Args:
        dataframe: DataFrame pandas com coluna 'POTENCIA'
    
    Returns:
        DataFrame limpo sem linhas com potência 'ND'
    """
    if 'POTENCIA' not in dataframe.columns:
        return dataframe
    
    # Converter dataframe para lista de dicionários para usar quicksort
    rows = dataframe.to_dict('records')
    
    if len(rows) == 0:
        return dataframe
    
    # Aplicar quicksort para mover linhas com 'ND' para o final
    quicksort(rows, 0, len(rows) - 1, 'POTENCIA')
    
    # Contar quantas linhas têm 'ND' em POTENCIA
    nd_count = sum(1 for row in rows if row['POTENCIA'] == 'ND')
    
    # Remover linhas com 'ND' (as últimas nd_count linhas após quicksort)
    if nd_count > 0:
        rows = rows[:-nd_count]
    
    # Converter de volta para dataframe
    cleaned_dataframe = pd.DataFrame(rows)
    return cleaned_dataframe.reset_index(drop=True)

def ocrAnuario(file_path_pdf, output_xlsx):
    try:
        nlp = spacy.load("pt_core_news_sm")
    except IOError:
        print("Erro: Modelo 'pt_core_news_sm' não encontrado.")
        print("Execute: python3 -m spacy download pt_core_news_sm")
        return 

    layout = spaCyLayout(nlp)

    print(f"Processando arquivo: {file_path_pdf}...")
    doc = layout(file_path_pdf)

    try:
        dataframe = pd.read_excel(output_xlsx, dtype=str)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{output_xlsx}' não encontrado.")
        print("Por favor, verifique o caminho e o nome do arquivo.")
        return 
    
    contador = 0

    # itera tabelas detectadas
    for table in doc._.tables:
        df_tabela = table._.data
        
        try:
            nome_trator = extract_name(df_tabela)
        except Exception:
            nome_trator = find_field(df_tabela, field_map['NOME'])
        print(f"\n-- Processando Tabela: {nome_trator} ---")

        # usa mapping para buscar cada campo (mais robusto que iloc fixo)
        potencia_raw = find_field(df_tabela, field_map['POTENCIA'])
        normaReferencia_raw = find_field(df_tabela, field_map['NORMA DE REFERENCIA'])
        cilindros_raw = find_field(df_tabela, field_map['CILINDROS'])
        aspiracao_raw = find_field(df_tabela, field_map['ASPIRACAO'])
        injecao_raw = find_field(df_tabela, field_map['INJECAO'])
        tipo_raw = find_field(df_tabela, field_map['TIPO'])
        frenteRe = find_field(df_tabela, field_map['FRENTE X RE'])
        embreagemTipo_raw = find_field(df_tabela, field_map['TIPO EMBREAGEM'])
        tracao = find_field(df_tabela, field_map['TRACAO'])
        tdp_between_raw = find_tdp_between(df_tabela)
        tdp_raw = find_field(df_tabela, field_map['TDP'])
        vazaoHidraulico_raw = find_field(df_tabela, field_map['VAZAO HIDRAULICO'])
        valvulasControle = find_field(df_tabela, field_map['VALVULAS CONTROLE'])
        # tentar extrair Vazão Controle Remoto (L/min) entre o rótulo "Vazão controle remoto" e "Capacidade Levante"
        try:
            vazao_controle_between = find_vazao_controle_between(df_tabela)
        except Exception:
            vazao_controle_between = 'ND'
        if vazao_controle_between != 'ND':
            vazaoControleRemoto_raw = vazao_controle_between
        else:
            vazaoControleRemoto_raw = find_field(df_tabela, field_map['VAZAO CONTROLE '])
        capacidadeLevante_raw = find_field(df_tabela, field_map['CAPACIDADE LEVANTE'])
        # tentar extrair Capacidade Levante (kgf) entre o rótulo "Capacidade levante" e próximas
        try:
            capacidade_between = find_capacidade_levante_between(df_tabela)
        except Exception:
            capacidade_between = 'ND'
        if capacidade_between != 'ND':
            capacidadeLevante_raw = capacidade_between
        altura = find_field(df_tabela, field_map['ALTURA(MM)'])
        entreEixos_raw = find_field(df_tabela, field_map['ENTRE EIXOS(MM)'])
        # entreEixos = parse_int_or_nd(entreEixos_raw)
         # tenta extrair Entre eixos(mm) entre o rótulo "Entre eixos" e "Vão livre"
        try:
            entreEixos_between = find_entre_eixos_value_between(df_tabela)
        except Exception:
            entreEixos_between = 'ND'
        if entreEixos_between != 'ND':
            entreEixos = entreEixos_between
        else:
            entreEixos = parse_int_or_nd(entreEixos_raw)
        vaoLivre_raw = find_field(df_tabela, field_map['VAO LIVRE'])
        vaoLivre = parse_int_or_nd(vaoLivre_raw)
        peso_raw = find_field(df_tabela, field_map['PESO'])
        tanque_raw = find_field(df_tabela, field_map['TANQUE'])
        postoOperacao_raw = find_field(df_tabela, field_map['POSTO DE OPERACAO'])

        # aplica validações/finalizações
        potencia = parse_potencia(potencia_raw)
        normaReferencia = parse_norma(normaReferencia_raw)
        cilindros = parse_cilindros(cilindros_raw)
        # usa o valor entre rótulos se disponível, senão usa o valor encontrado por find_field
        if tdp_between_raw != 'ND':
            tdp = parse_tdp(tdp_between_raw)
        else:
            tdp = parse_tdp(tdp_raw)
        tipo = normalize_tipo(tipo_raw)
        embreagemTipo = normalize_tipoEmbreagem(embreagemTipo_raw)
        postoOperacao = normalize_posto(postoOperacao_raw)
        peso = peso_raw
        vazaoHidraulico = parse_numeric_field(vazaoHidraulico_raw)
        vazaoControleRemoto = parse_numeric_field(vazaoControleRemoto_raw)
        capacidadeLevante = parse_numeric_field(capacidadeLevante_raw)
        tanque = parse_numeric_field(tanque_raw)
        aspiracao = refine_aspiracao_injecao(aspiracao_raw, injecao_raw)
        injecao = parse_injecao(injecao_raw)

        # escreve no dataframe de saída
        dataframe.at[contador, 'NOME'] = nome_trator
        dataframe.at[contador, 'POTENCIA'] = potencia
        dataframe.at[contador, 'NORMA DE REFERENCIA'] = normaReferencia
        dataframe.at[contador, 'CILINDROS'] = cilindros
        dataframe.at[contador, 'ASPIRACAO'] = aspiracao
        dataframe.at[contador, 'INJECAO'] = injecao
        dataframe.at[contador, 'TIPO'] = tipo
        dataframe.at[contador, 'FRENTE X RE'] = frenteRe
        dataframe.at[contador, 'TIPO EMBREAGEM'] = embreagemTipo
        dataframe.at[contador, 'TRACAO'] = tracao
        dataframe.at[contador, 'TDP'] = tdp
        dataframe.at[contador, 'VAZAO HIDRAULICO'] = vazaoHidraulico
        dataframe.at[contador, 'VAZAO CONTROLE '] = vazaoControleRemoto
        dataframe.at[contador, 'CAPACIDADE LEVANTE'] = capacidadeLevante
        dataframe.at[contador, 'ALTURA(MM)'] = altura
        dataframe.at[contador, 'ENTRE EIXOS(MM)'] = entreEixos
        dataframe.at[contador, 'VAO LIVRE'] = vaoLivre
        dataframe.at[contador, 'PESO'] = peso
        dataframe.at[contador, 'TANQUE'] = tanque
        dataframe.at[contador, 'POSTO DE OPERACAO'] = postoOperacao

        contador += 1
        
    try:
        dataframe.to_excel(output_xlsx, index=False)
        print(f"\n[SUCESSO] Processamento concluído. {contador} tabelas salvas em {output_xlsx}")
    except PermissionError:
        print(f"\n[ERRO] Não foi possível salvar em '{output_xlsx}'.")
        print("Por favor, feche o arquivo Excel se ele estiver aberto.")
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro inesperado ao salvar: {e}")
    
    # Limpar linhas com potência 'ND' usando quicksort
    dataframe = remove_nd_potencia_rows(dataframe)
    
    try:
        dataframe.to_excel(output_xlsx, index=False)
        print(f"[SUCESSO] Linhas com potência 'ND' removidas. Arquivo atualizado em {output_xlsx}")
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar arquivo após limpeza: {e}")
    
def find_tdp_between(df):
    """
    Procura e retorna o valor que está entre o rótulo contendo 'tdp'+'rpm' e o rótulo 'tdp'+'acion' (acionamento).
    Estratégia:
    - localiza posições contendo indicadores de TDP(rpm) e de TDP(acionamento)
    - para cada início (tdp+rpm) tenta achar o fim (tdp+acionamento) que venha depois na ordem de leitura
    - coleta células entre os dois rótulos, prefere células que is_value_like, senão primeiro texto não-vazio
    Retorna 'ND' se não encontrar.
    """
    rows, cols = df.shape
    start_positions = []
    end_positions = []

    for r in range(rows):
        for c in range(cols):
            try:
                cell_raw = df.iat[r, c]
            except Exception:
                cell_raw = None
            if cell_raw is None or pd.isna(cell_raw):
                continue
            s = norm(cell_raw)
            if not s:
                continue
            # detectores flexíveis para variações de rótulo
            if 'tdp' in s and 'rpm' in s:
                start_positions.append((r, c))
            if 'tdp' in s and ('acion' in s or 'acionamento' in s):
                end_positions.append((r, c))

    if not start_positions:
        return 'ND'

    # para cada start, procurar o primeiro end que venha depois na leitura
    for sr, sc in start_positions:
        candidates = [(er, ec) for (er, ec) in end_positions if (er > sr) or (er == sr and ec > sc)]
        if not candidates:
            continue
        er, ec = min(candidates)  # primeiro na ordem de leitura
        # mesma linha: ler entre colunas
        if sr == er:
            values = []
            for cc in range(sc + 1, ec):
                try:
                    v = df.iat[sr, cc]
                except Exception:
                    v = None
                if v is None or pd.isna(v):
                    continue
                if is_value_like(v):
                    values.append(str(v).strip())
            if values:
                return ' '.join(values)
            # fallback: primeira célula não-vazia entre
            for cc in range(sc + 1, ec):
                try:
                    v = df.iat[sr, cc]
                except Exception:
                    v = None
                if v is not None and not pd.isna(v) and str(v).strip():
                    return str(v).strip()
        else:
            # linhas diferentes: varrer em ordem de leitura entre (sr,sc) e (er,ec)
            values = []
            r, c = sr, sc + 1
            while r < rows and not (r == er and c == ec):
                if c >= cols:
                    r += 1
                    c = 0
                    continue
                try:
                    v = df.iat[r, c]
                except Exception:
                    v = None
                if v is not None and not pd.isna(v) and is_value_like(v):
                    values.append(str(v).strip())
                c += 1
            if values:
                return ' '.join(values)
            # fallback: primeira não-vazia entre
            r, c = sr, sc + 1
            while r < rows and not (r == er and c == ec):
                if c >= cols:
                    r += 1
                    c = 0
                    continue
                try:
                    v = df.iat[r, c]
                except Exception:
                    v = None
                if v is not None and not pd.isna(v) and str(v).strip():
                    return str(v).strip()
                c += 1

    # se não achou intervalos com um end após start, tentar heurísticas próximas ao primeiro start
    sr, sc = start_positions[0]
    # verificar células à direita imediatas
    for offset in (1, 2, 3):
        cc = sc + offset
        if cc < cols:
            try:
                v = df.iat[sr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v) and is_value_like(v):
                return str(v).strip()
    # verificar linhas abaixo próximas
    for rr in range(sr + 1, min(rows, sr + 6)):
        for cc in range(max(0, sc - 1), min(cols, sc + 3)):
            try:
                v = df.iat[rr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v) and is_value_like(v):
                return str(v).strip()
    return 'ND'

def find_entre_eixos_between(df):
    """
    Procura e retorna o número de 'Entre eixos (mm)' que esteja após o rótulo 'entre eixos'
    e antes de 'vao livre'. Aceita números com . como separador de milhares (ex: 2.350 -> 2350).
    Retorna inteiro sem separadores como string, ou 'ND'.
    """
    rows, cols = df.shape
    start_positions = []
    end_positions = []

    for r in range(rows):
        for c in range(cols):
            try:
                cell_raw = df.iat[r, c]
            except Exception:
                cell_raw = None
            if cell_raw is None or pd.isna(cell_raw):
                continue
            s = norm(cell_raw)
            if not s:
                continue
            if 'entre' in s and 'eixos' in s:
                start_positions.append((r, c))
            if ('vao' in s or 'vão' in s) and 'livre' in s:
                end_positions.append((r, c))

    if not start_positions:
        return 'ND'

    for sr, sc in start_positions:
        candidates = [(er, ec) for (er, ec) in end_positions if (er > sr) or (er == sr and ec > sc)]
        if not candidates:
            continue
        er, ec = min(candidates)
        # mesma linha: procurar célula com número entre os rótulos
        if sr == er:
            for cc in range(sc + 1, ec):
                try:
                    v = df.iat[sr, cc]
                except Exception:
                    v = None
                if v is None or pd.isna(v):
                    continue
                iv = parse_numeric_with_thousand_separator(v)
                if iv != 'ND':
                    return iv
        else:
            # varrer ordem de leitura entre start e end
            r, c = sr, sc + 1
            while r < rows and not (r == er and c == ec):
                if c >= cols:
                    r += 1
                    c = 0
                    continue
                try:
                    v = df.iat[r, c]
                except Exception:
                    v = None
                if v is not None and not pd.isna(v):
                    iv = parse_numeric_with_thousand_separator(v)
                    if iv != 'ND':
                        return iv
                c += 1

    # heurísticas próximas ao primeiro start
    sr, sc = start_positions[0]
    for offset in (1, 2, 3):
        cc = sc + offset
        if cc < cols:
            try:
                v = df.iat[sr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v):
                iv = parse_numeric_with_thousand_separator(v)
                if iv != 'ND':
                    return iv
    for rr in range(sr + 1, min(rows, sr + 6)):
        for cc in range(max(0, sc - 1), min(cols, sc + 3)):
            try:
                v = df.iat[rr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v):
                iv = parse_numeric_with_thousand_separator(v)
                if iv != 'ND':
                    return iv

    return 'ND'

def find_capacidade_levante_between(df):
    """
    Procura e retorna o número da Capacidade Levante (kgf) após o rótulo 'capacidade levante'.
    Estratégia: localizar posição do rótulo, varrer células à direita e abaixo,
    extrair número que pode conter . ou , como separador de milhares (ex: 5.080, 5,080).
    Retorna inteiro sem separadores como string, ou 'ND'.
    """
    rows, cols = df.shape
    start_positions = []

    for r in range(rows):
        for c in range(cols):
            try:
                cell_raw = df.iat[r, c]
            except Exception:
                cell_raw = None
            if cell_raw is None or pd.isna(cell_raw):
                continue
            s = norm(cell_raw)
            if not s:
                continue
            if 'capacidade' in s and 'levante' in s:
                start_positions.append((r, c))

    if not start_positions:
        return 'ND'

    for sr, sc in start_positions:
        # checar células à direita na mesma linha
        for offset in (1, 2, 3):
            cc = sc + offset
            if cc < cols:
                try:
                    v = df.iat[sr, cc]
                except Exception:
                    v = None
                if v is None or pd.isna(v):
                    continue
                iv = parse_capacidade_levante_value(v)
                if iv != 'ND':
                    return iv
        # checar linhas abaixo próximas na mesma coluna e colunas adjacentes
        for rr in range(sr + 1, min(rows, sr + 6)):
            for cc in range(max(0, sc - 1), min(cols, sc + 3)):
                try:
                    v = df.iat[rr, cc]
                except Exception:
                    v = None
                if v is None or pd.isna(v):
                    continue
                iv = parse_capacidade_levante_value(v)
                if iv != 'ND':
                    return iv

    return 'ND'

def parse_capacidade_levante_value(val):
    """
    Extrai número de capacidade levante que pode conter . ou , como separadores de milhares.
    Ex: "5.080" ou "5,080" -> retorna "5080"
        "5080 kgf" -> retorna "5080"
    Retorna 'ND' se não encontrar número válido.
    """
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s or s.upper() == 'ND':
        return 'ND'
    
    # extrai sequência de dígitos com possíveis . ou , no meio
    # padrão: dígitos opcionalmente seguidos de (ponto/vírgula + dígitos)*
    m = re.search(r'(\d+(?:[.,]\d+)*)', s)
    if not m:
        return 'ND'
    
    num_str = m.group(1)
    # remove todos os . e , para obter número limpo
    num_clean = num_str.replace('.', '').replace(',', '')
    
    # valida se é número válido
    try:
        int(num_clean)
        return num_clean
    except ValueError:
        return 'ND'

def find_entre_eixos_value_between(df):
    """
    Procura e retorna o número de 'Entre eixos (mm)' que esteja após o rótulo 'entre eixos'
    e antes de 'vao livre'. Aceita números com . como separador de milhares (ex: 2.350 -> 2350).
    Retorna inteiro sem separadores como string, ou 'ND'.
    """
    rows, cols = df.shape
    start_positions = []
    end_positions = []

    for r in range(rows):
        for c in range(cols):
            try:
                cell_raw = df.iat[r, c]
            except Exception:
                cell_raw = None
            if cell_raw is None or pd.isna(cell_raw):
                continue
            s = norm(cell_raw)
            if not s:
                continue
            if 'entre' in s and 'eixos' in s:
                start_positions.append((r, c))
            if ('vao' in s or 'vão' in s) and 'livre' in s:
                end_positions.append((r, c))

    if not start_positions:
        return 'ND'

    for sr, sc in start_positions:
        candidates = [(er, ec) for (er, ec) in end_positions if (er > sr) or (er == sr and ec > sc)]
        if not candidates:
            continue
        er, ec = min(candidates)
        # mesma linha: procurar célula com número entre os rótulos
        if sr == er:
            for cc in range(sc + 1, ec):
                try:
                    v = df.iat[sr, cc]
                except Exception:
                    v = None
                if v is None or pd.isna(v):
                    continue
                iv = parse_numeric_with_thousand_separator(v)
                if iv != 'ND':
                    return iv
        else:
            # varrer ordem de leitura entre start e end
            r, c = sr, sc + 1
            while r < rows and not (r == er and c == ec):
                if c >= cols:
                    r += 1
                    c = 0
                    continue
                try:
                    v = df.iat[r, c]
                except Exception:
                    v = None
                if v is not None and not pd.isna(v):
                    iv = parse_numeric_with_thousand_separator(v)
                    if iv != 'ND':
                        return iv
                c += 1

    # heurísticas próximas ao primeiro start
    sr, sc = start_positions[0]
    for offset in (1, 2, 3):
        cc = sc + offset
        if cc < cols:
            try:
                v = df.iat[sr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v):
                iv = parse_numeric_with_thousand_separator(v)
                if iv != 'ND':
                    return iv
    for rr in range(sr + 1, min(rows, sr + 6)):
        for cc in range(max(0, sc - 1), min(cols, sc + 3)):
            try:
                v = df.iat[rr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v):
                iv = parse_numeric_with_thousand_separator(v)
                if iv != 'ND':
                    return iv

    return 'ND'

def parse_numeric_with_thousand_separator(val):
    """
    Extrai número que pode conter . como separador de milhares.
    Ex: "2.350" ou "2350" -> retorna "2350"
    Retorna 'ND' se não encontrar número válido.
    """
    if val is None:
        return 'ND'
    s = str(val).strip()
    if not s or s.upper() == 'ND':
        return 'ND'
    
    # extrai sequência de dígitos com possíveis . no meio (separador de milhares)
    m = re.search(r'(\d+(?:\.\d+)*)', s)
    if not m:
        return 'ND'
    
    num_str = m.group(1)
    # remove todos os . para obter número limpo
    num_clean = num_str.replace('.', '')
    
    # valida se é número válido
    try:
        int(num_clean)
        return num_clean
    except ValueError:
        return 'ND'

def find_vazao_controle_between(df):
    """
    Procura e retorna o número da Vazão Controle Remoto (L/min) que esteja entre
    o rótulo 'vazao controle remoto' e o rótulo 'capacidade levante'.
    Extrai inteiro que pode conter . ou , como separadores de milhares.
    Retorna 'ND' se não encontrar.
    """
    rows, cols = df.shape
    start_positions = []
    end_positions = []

    for r in range(rows):
        for c in range(cols):
            try:
                cell_raw = df.iat[r, c]
            except Exception:
                cell_raw = None
            if cell_raw is None or pd.isna(cell_raw):
                continue
            s = norm(cell_raw)
            if not s:
                continue
            if 'vazao' in s and 'control' in s:
                start_positions.append((r, c))
            if 'capacidade' in s and 'levante' in s:
                end_positions.append((r, c))

    if not start_positions:
        return 'ND'

    for sr, sc in start_positions:
        candidates = [(er, ec) for (er, ec) in end_positions if (er > sr) or (er == sr and ec > sc)]
        if not candidates:
            continue
        er, ec = min(candidates)
        # mesma linha
        if sr == er:
            for cc in range(sc + 1, ec):
                try:
                    v = df.iat[sr, cc]
                except Exception:
                    v = None
                if v is None or pd.isna(v):
                    continue
                iv = parse_capacidade_levante_value(v)
                if iv != 'ND':
                    return iv
        else:
            # varrer ordem de leitura entre start e end
            r, c = sr, sc + 1
            while r < rows and not (r == er and c == ec):
                if c >= cols:
                    r += 1
                    c = 0
                    continue
                try:
                    v = df.iat[r, c]
                except Exception:
                    v = None
                if v is not None and not pd.isna(v):
                    iv = parse_capacidade_levante_value(v)
                    if iv != 'ND':
                        return iv
                c += 1

    # heurísticas próximas ao primeiro start
    sr, sc = start_positions[0]
    for offset in (1, 2, 3):
        cc = sc + offset
        if cc < cols:
            try:
                v = df.iat[sr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v):
                iv = parse_capacidade_levante_value(v)
                if iv != 'ND':
                    return iv
    for rr in range(sr + 1, min(rows, sr + 6)):
        for cc in range(max(0, sc - 1), min(cols, sc + 3)):
            try:
                v = df.iat[rr, cc]
            except Exception:
                v = None
            if v is not None and not pd.isna(v):
                iv = parse_capacidade_levante_value(v)
                if iv != 'ND':
                    return iv