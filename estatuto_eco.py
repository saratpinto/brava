import pandas as pd
import plotly.graph_objects as go

# -----------------------------------
# 1. Ler dados
# -----------------------------------
file_path = r"C:\Users\sarat\Dropbox\Sara_Pinto\Conteudos_produzidos\Lista de Espécies\especies_Brava_ilheus_VFF.xlsx"
df = pd.read_excel(file_path)

df = df.rename(columns={
    "Estatuto (catálogo)": "Catalogo",
    "Estatuto LPES": "LPES"
})
df["Grupo"] = df["Grupo"].replace({"Líquen": "Líquenes"})

# -----------------------------------
# 2. Converter para formato longo
# -----------------------------------
df_long = df.melt(
    id_vars=["Grupo"],
    value_vars=["Catalogo", "LPES"],
    var_name="Fonte",
    value_name="Estatuto"
).dropna(subset=["Estatuto"])

df_count = df_long.groupby(["Grupo", "Fonte", "Estatuto"]).size().reset_index(name="N")

# -----------------------------------
# 3. Cores simplificadas
# -----------------------------------
color_map_detailed = {
    # Catálogo
    ("Catalogo", "Aut"): "#1f78b4",
    ("Catalogo", "End"): "#91cf60",
    ("Catalogo", "M"): "#abd9e9",
    ("Catalogo", "SI"): "#f5f5dc",
    
    # LPES
    ("LPES", "Aut"): "#1f78b4",
    ("LPES", "Aut. Poss"): "#74add1",
    ("LPES", "Aut. Prov"): "#abd9e9",
    ("LPES", "Intr"): "#d73027",
    ("LPES", "Intr. Prov"): "#f46d43",
    ("LPES", "Inv"): "#a50026",
    ("LPES", "SI"): "#f5f5dc",
}

parent_colors = {
    "Catalogo": "#d0e1f9",
    "LPES": "#fddbc7"
}

unique_groups = df["Grupo"].unique()
group_palette = ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3"]
group_color_map = {g: group_palette[i % len(group_palette)] for i, g in enumerate(unique_groups)}

# -----------------------------------
# 4. Criar listas para sunburst
# -----------------------------------
ids = []
labels = []
parents = []
values = []
marker_colors = []

# Nível 0
group_agg = df_count.groupby("Grupo")["N"].sum().reset_index()
for _, row in group_agg.iterrows():
    group = row["Grupo"]
    ids.append(group)
    labels.append(group)
    parents.append("")
    values.append(row["N"])
    marker_colors.append(group_color_map.get(group, "lightgrey"))

# Nível 1
fonte_agg = df_count.groupby(["Grupo", "Fonte"])["N"].sum().reset_index()
for _, row in fonte_agg.iterrows():
    group, fonte, val = row["Grupo"], row["Fonte"], row["N"]
    node_id = f"{group}_{fonte}"
    ids.append(node_id)
    labels.append(fonte)
    parents.append(group)
    values.append(val)
    marker_colors.append(parent_colors.get(fonte, "grey"))

# Nível 2
for _, row in df_count.iterrows():
    group, fonte, estatuto = row["Grupo"], row["Fonte"], row["Estatuto"]
    val = row["N"]
    node_id = f"{group}_{fonte}_{estatuto}"
    ids.append(node_id)
    labels.append(estatuto)
    parents.append(f"{group}_{fonte}")
    values.append(val)
    marker_colors.append(color_map_detailed.get((fonte, estatuto), "lightgrey"))

# -----------------------------------
# 5. Criar gráfico
# -----------------------------------
fig = go.Figure(go.Sunburst(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    marker=dict(colors=marker_colors, line=dict(color="#696969", width=1)),
    insidetextorientation='radial',
    domain=dict(x=[0.1, 0.75])
))

fig.update_layout(
    margin=dict(t=0, l=0, r=320, b=0),
    paper_bgcolor="#f0f0f0",
    title=None
)

# -----------------------------------
# 6. Legenda
# -----------------------------------
legend_text = (
    "<b>Estatuto no Catálogo:</b><br>"
    "<span style='color:#1f78b4'>■</span> Aut: Autóctone<br>"
    "<span style='color:#91cf60'>■</span> End: Endémica<br>"
    "<span style='color:#abd9e9'>■</span> M: Migratória<br>"
    "<span style='color:#f5f5dc'>■</span> SI: Sem Informação<br><br>"
    "<b>Estatuto na LPES:</b><br>"
    "<span style='color:#1f78b4'>■</span> Aut: Autóctone<br>"
    "<span style='color:#74add1'>■</span> Aut. Poss: Autóctone Possível<br>"
    "<span style='color:#abd9e9'>■</span> Aut. Prov: Autóctone Provável<br>"
    "<span style='color:#d73027'>■</span> Intr: Introduzida<br>"
    "<span style='color:#f46d43'>■</span> Intr. Prov: Introduzida Provável<br>"
    "<span style='color:#a50026'>■</span> Inv: Invasora<br>"
    "<span style='color:#f5f5dc'>■</span> SI: Sem Informação<br>"
)

fig.update_layout(
    annotations=[dict(
        x=1.15,
        y=0.5,
        xref="paper",
        yref="paper",
        text="<b>Espécies da Ilha Brava</b><br>" + legend_text,
        showarrow=False,
        align="left",
        bordercolor="black",
        borderwidth=1,
        borderpad=10,
        bgcolor="white",
        opacity=0.9
    )]
)

# -----------------------------------
# 7. Guardar como página web
# -----------------------------------
fig.write_html("estatuto_eco.html")
