from langchain.tools import Tool
        
def calcular_impuesto(ingreso_anual_anio)-> str:
    renta_anual, anio = eval(ingreso_anual_anio)
    if anio==2023:
        tramos = [
            (9907434, 0.00, 0),
            (22016520, 0.04, 396297.36),
            (36694200, 0.08, 1276958.16),
            (51371880, 0.135, 3295139.16),
            (66049560, 0.230, 8175467.76),
            (88066080, 0.304, 13063135.20),
            (227504040, 0.35, 17114174.88),
            (float("inf"), 0.40, 28489376.88),
        ]
    elif anio==2022:
        tramos = [
            (8775702, 0.00, 0),
            (19501560, 0.04, 351028.08),
            (32502600, 0.08, 1131090.48),
            (45503640, 0.135, 2918733.48),
            (58504680, 0.23, 7241579.28),
            (78006240, 0.304, 11570925.60),
            (201516120, 0.35, 15159212.64),
            (float("inf"), 0.40, 25235018.64),
        ]
    elif anio==2021:
        tramos = [
            (8266698, 0, 0),
            (18370440, 0.04, 330667.92),
            (30617400, 0.08, 1065485.52),
            (42864360, 0.135, 2749442.52),
            (55111320, 0.23, 6821556.72),
            (73481760, 0.304, 10899794.4),
            (189827880, 0.35, 14279955.36),
            (float("inf"), 0.4, 23771349.36),
        ]
    else:
        return 'Año no válido. Debes consultar el año al usuario'

    final_factor = None
    final_rebaja = None
    for i, (limite, factor, rebaja) in enumerate(tramos):
        if renta_anual <= limite:
            final_factor = factor
            final_rebaja = rebaja
            break

    print(final_factor)
    print(final_rebaja)
    return renta_anual*final_factor - final_rebaja

# tools = [
#     StructuredTool.from_function(func=calcular_impuesto),
# ]

tools = [
    Tool(
        name ='Calculo Impuesto',
        description='útil para calcular el impuesto dado el INGRESO ANUAL IMPONIBLE y el AÑO FISCAL. Formato input función (ingreso_anual,año). Solo años 2021, 2022, y 2023.',
        func=calcular_impuesto,
    ),
]