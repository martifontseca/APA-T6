import re

def normalizaHoras(ficText, ficNorm):
    """
    Lee el fichero de texto 'ficText', busca expresiones horarias y escribe
    el fichero 'ficNorm' con las horas en formato estándar HH:MM.
    Las expresiones incorrectas se dejan tal cual.
    """
    
    def reemplaza(match):
        grupo = match.group().strip()

        # 1. Formato: 8h30m, 8h, 17h5m
        h_m = re.match(r'^(\d{1,2})h(?:(\d{1,2})m?)?$', grupo)
        if h_m:
            h = int(h_m.group(1))
            m_str = h_m.group(2)
            m = int(m_str) if m_str else 0
            if h < 24 and m < 60:
                return f'{h:02d}:{m:02d}'
            return grupo

        # 2. Formato estándar o similar: 8:30, 18:05, 17:5 (este último es incorrecto)
        h_p_m = re.match(r'^(\d{1,2}):(\d{1,2})$', grupo)
        if h_p_m:
            h = int(h_p_m.group(1))
            m_str = h_p_m.group(2)
            m = int(m_str)
            # El enunciado dice que '17:5' es incorrecto (los minutos deben tener 2 dígitos)
            if h < 24 and m < 60 and len(m_str) == 2:
                return f'{h:02d}:{m:02d}'
            return grupo

        # 3. Formato hablado con momento del día: "4 y media de la tarde", "12 de la noche"
        hablado_momento = re.match(
            r'^(\d{1,2})(?:\s+(en punto|y cuarto|y media|menos cuarto))?\s+de la\s+(mañana|tarde|noche|madrugada|mediodía)$', 
            grupo
        )
        if hablado_momento:
            h = int(hablado_momento.group(1))
            f = hablado_momento.group(2)
            p = hablado_momento.group(3)

            # Validar restricciones estrictas del enunciado por momento del día
            if p == 'mañana' and not (4 <= h <= 12):
                return grupo
            if p == 'mediodía' and not (12 <= h <= 3):
                return grupo
            if p == 'tarde' and not (3 <= h <= 8):
                return grupo
            if p == 'noche' and not (8 <= h <= 12) and not (1 <= h <= 4):
                return grupo
            if p == 'madrugada' and not (1 <= h <= 6):
                return grupo

            # Convertir formato de 12h a 24h basándose en el contexto hablado
            if p in ['tarde', 'noche'] and h != 12:
                h += 12
            if p == 'noche' and h == 12:
                h = 0
            if p == 'madrugada' and h == 12:  # por si acaso dijeran 12 de la madrugada
                h = 0

            # Calcular los minutos
            m = 0
            if f == 'y cuarto':
                m = 15
            elif f == 'y media':
                m = 30
            elif f == 'menos cuarto':
                h -= 1
                if h < 0:
                    h = 23
                m = 45

            return f'{h:02d}:{m:02d}'

        # 4. Formato hablado simple (rango de 00:00 a 11:59): "8 en punto", "5 menos cuarto"
        hablado = re.match(r'^(\d{1,2})\s+(en punto|y cuarto|y media|menos cuarto)$', grupo)
        if hablado:
            h = int(hablado.group(1))
            f = hablado.group(2)

            if not (1 <= h <= 12):
                return grupo

            m = 0
            if f == 'y cuarto':
                m = 15
            elif f == 'y media':
                m = 30
            elif f == 'menos cuarto':
                h -= 1
                if h == 0:
                    h = 12
                m = 45

            # El enunciado dice: "El resultado se devolverá siempre en el rango de 00:00 a 11:59"
            if h == 12 and f != 'menos cuarto':
                h = 0

            return f'{h:02d}:{m:02d}'

        return grupo

    # Expresión regular global para capturar todas las estructuras horarias posibles del texto
    compila = re.compile(
        r'\b\d{1,2}h(?:\d{1,2}m?)?\b|'
        r'\b\d{1,2}:\d{1,2}\b|'
        r'\b\d{1,2}\s+(?:en punto|y cuarto|y media|menos cuarto)(?:\s+de la\s+(?:mañana|tarde|noche|madrugada|mediodía))?\b|'
        r'\b\d{1,2}\s+de la\s+(?:mañana|tarde|noche|madrugada|mediodía)\b'
    )

    with open(ficText, 'r', encoding='utf-8') as entrada, open(ficNorm, 'w', encoding='utf-8') as salida:
        for linea in entrada:
            # Reemplaza las horas detectadas usando la función interna
            linea_normalizada = compila.sub(reemplaza, linea)
            salida.write(linea_normalizada)


if __name__ == "__main__":
    # Ejemplo de ejecución local
    normalizaHoras('horas.txt', 'horas_normalizadas.txt')