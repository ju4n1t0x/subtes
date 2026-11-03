import pandas as pd

OUTPUT = "Datasets/total_viajes_por_linea.csv"
PAX = ["pax_pagos", "pax_pases_pagos", "pax_franq", "pax_TOTAL"]

# Original column name (header in each CSV) -> unified column name
SOURCES = [
    {
        "path": "Datasets/historico_2014.csv",
        "sep": ",",
        "columns": {
            "FECHA": "FECHA",
            "LINEA": "LINEA",
            "PAX_PAGO": "pax_pagos",
            "PAX_PASES_PAGOS": "pax_pases_pagos",
            "PAX_FRANQ": "pax_franq",
            "PAX_TOTAL": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2015.csv",
        "sep": ",",
        "columns": {
            "fecha": "FECHA",
            "linea": "LINEA",
            "pax_pagos": "pax_pagos",
            "pax_pases_pagos": "pax_pases_pagos",
            "pax_franq": "pax_franq",
            "total": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2016.csv",
        "sep": ",",
        "columns": {
            "FECHA": "FECHA",
            "LINEA": "LINEA",
            "PAX_PAGOS": "pax_pagos",
            "PAX_PASES_PAGOS": "pax_pases_pagos",
            "PAX_FREQ": "pax_franq",
            "TOTAL": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2017.csv",
        "sep": ",",
        "columns": {
            "FECHA": "FECHA",
            "LINEA": "LINEA",
            "PAX_PAGOS": "pax_pagos",
            "PAX_PASES_PAGOS": "pax_pases_pagos",
            "PAX_FREQ": "pax_franq",
            "TOTAL": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2018.csv",
        "sep": ",",
        "columns": {
            "fecha": "FECHA",
            "linea": "LINEA",
            "pax_pagos": "pax_pagos",
            "pax_pases_pagos": "pax_pases_pagos",
            "pax_franq": "pax_franq",
            "total": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2019.csv",
        "sep": ",",
        "columns": {
            "fecha": "FECHA",
            "linea": "LINEA",
            "pax_pagos": "pax_pagos",
            "pax_pases_pagos": "pax_pases_pagos",
            "pax_franq": "pax_franq",
            "total": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2020.csv",
        "sep": ",",
        "columns": {
            "FECHA": "FECHA",
            "LINEA": "LINEA",
            "pax_pagos": "pax_pagos",
            "pax_pases_pagos": "pax_pases_pagos",
            "pax_franq": "pax_franq",
            "pax_TOTAL": "pax_TOTAL",
        },
    },
    {
        "path": "Datasets/historico_2021.csv",
        "sep": ";",
        "columns": {
            "FECHA": "FECHA",
            "LINEA": "LINEA",
            "pax_pagos": "pax_pagos",
            "pax_pases_pagos": "pax_pases_pagos",
            "pax_franq": "pax_franq",
            "pax_TOTAL": "pax_TOTAL",
        },
    },
]

rows_before = 0
total_before = 0
pieces = []

for source in SOURCES:
    columns = source["columns"]      # original -> unified
    usecols = list(columns)          # dict keys = original header names
    dtype = {
        original: ("string" if unified in ("FECHA", "LINEA") else "float64")
        for original, unified in columns.items()
    }

    df = pd.read_csv(
        source["path"],
        sep=source["sep"],
        usecols=usecols,
        dtype=dtype,
        encoding=source.get("encoding", "utf-8")
    )
    df = df.rename(columns=columns)

    df["FECHA"] = pd.to_datetime(df["FECHA"], format="mixed", dayfirst=True)

    # Normalize line names: A, LINEA_A, LineaA -> A
    df["LINEA"] = (
        df["LINEA"].str.upper().str.replace("LINEA", "", regex=False).str.strip("_ ")
    )

    unusable = df["FECHA"].isna() | df["LINEA"].isna()
    if unusable.any():
        print(f"{source['path']}: descartando {int(unusable.sum()):,} filas sin fecha o línea")
        df = df[~unusable]

    for col in PAX:
        df[col] = df[col].fillna(0).astype("int64")

    df["periodo"] = df["FECHA"].dt.year.astype("int16")
    df["mes"] = df["FECHA"].dt.month.astype("int8")

    rows_before += len(df)
    total_before += int(df["pax_TOTAL"].sum())

    pieces.append(df.groupby(["periodo", "mes", "LINEA"], as_index=False)[PAX].sum())
    del df

result = pd.concat(pieces, ignore_index=True)
result = result.groupby(["periodo", "mes", "LINEA"], as_index=False)[PAX].sum()
result = result.sort_values(["periodo", "mes", "LINEA"]).reset_index(drop=True)

assert int(result["pax_TOTAL"].sum()) == total_before, "Totales de pax_TOTAL no coinciden"

result.to_csv(OUTPUT, sep=";", index=False)

print(f"Registros originales: {rows_before:,}")
print(f"Registros finales:    {len(result):,}")
print(f"pax_TOTAL: {total_before:,} (originales) vs {int(result['pax_TOTAL'].sum()):,} (agregado)")
print(f"Archivo generado: {OUTPUT}")
