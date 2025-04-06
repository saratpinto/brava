import pandas as pd
import plotly.graph_objects as go


file_path = r"C:\Users\sarat\Dropbox\Sara_Pinto\Conteudos_produzidos\Lista de Espécies\especies_Brava_ilheus_VFF.xlsx"
df = pd.read_excel(file_path)


df = df.rename(columns={
    "Avaliação UICN": "IUCN",
    "Lista Vermelha Cabo Verde": "LVCV"
})
df["Grupo"] = df["Grupo"].replace({"Líquen": "Líquenes"})

df_long = df.melt(
    id_vars=["Grupo"],
    value_vars=["IUCN", "LVCV"],
    var_name="Fonte",
    value_name="Estatuto"
).dropna(subset=["Estatuto"])


df_count = df_long.groupby(["Grupo", "Fonte", "Estatuto"]).size().reset_index(name="N")


group_agg = df_count.groupby("Grupo")["N"].sum().reset_index()
fonte_agg = df_count.groupby(["Grupo", "Fonte"])["N"].sum().reset_index()


group_palette = [
    "#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3",
    "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd",
    "#ccebc5", "#ffed6f", "#ffff99", "#bae1ff", "#ffc9de",
    "#ffccf9", "#c6e2ff", "#f2ffe6", "#fdfd96", "#ffd1dc",
]
unique_groups = group_agg["Grupo"].unique()
group_color_map = {g: group_palette[i % len(group_palette)] for i, g in enumerate(unique_groups)}
group_color_map.update({
    "Algas": "#66c2a5",
    "Répteis": "#fc8d62",
    "Líquenes": "#8da0cb",
    "Insetos": "#e78ac3"
})

parent_colors = {
    "IUCN": "#aec7e8",
    "LVCV": "#fff2b8"
}

color_map_detailed = {
    ("IUCN", "DD"): "#FFFF99",  
    ("IUCN", "CR"): "#8B0000",  
    ("IUCN", "EN"): "#FF6347",  
    ("IUCN", "VU"): "#C71585",  
    ("IUCN", "NT"): "#FFC0CB",  
    ("IUCN", "LC"): "#008000",  
    ("IUCN", "NE"): "#f5f5dc",  
    ("LVCV", "EX"): "#000000",  
    ("LVCV", "Ind"): "#D3D3D3", 
    ("LVCV", "Des"): "#D2B48C", 
    ("LVCV", "Rara"): "#FFA500",
    ("LVCV", "NE"): "#f5f5dc",  
    ("LVCV", "DD"): "#FFFF99",  
    ("LVCV", "CR"): "#8B0000",  
    ("LVCV", "EN"): "#FF6347",  
    ("LVCV", "VU"): "#C71585",  
}


ids = []
labels = []
parents = []
values = []
marker_colors = []

# Nível 0
for _, row in group_agg.iterrows():
    group = row["Grupo"]
    ids.append(group)
    labels.append(group)
    parents.append("")
    values.append(row["N"])
    marker_colors.append(group_color_map.get(group, "lightgrey"))

# Nível 1
for _, row in fonte_agg.iterrows():
    group = row["Grupo"]
    fonte = row["Fonte"]
    node_id = f"{group}_{fonte}"
    ids.append(node_id)
    labels.append(fonte)
    parents.append(group)
    values.append(row["N"])
    marker_colors.append(parent_colors.get(fonte, "grey"))

# Nível 2
for _, row in df_count.iterrows():
    group = row["Grupo"]
    fonte = row["Fonte"]
    estatuto = row["Estatuto"]
    node_id = f"{group}_{fonte}_{estatuto}"
    ids.append(node_id)
    labels.append(estatuto)
    parents.append(f"{group}_{fonte}")
    values.append(row["N"])
    marker_colors.append(color_map_detailed.get((fonte, estatuto), "lightgrey"))


fig = go.Figure(go.Sunburst(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    marker=dict(
        colors=marker_colors,
        line=dict(color="#696969", width=1)
    ),
    insidetextorientation='radial',
    domain=dict(x=[0.08, 0.93])  # puxado ligeiramente à direita
))


fig.update_layout(
    margin=dict(t=0, l=0, r=340, b=0),  # margem direita maior
    paper_bgcolor="#f0f0f0",
    title=None
)


legend_text = (
    "<b>Avaliação IUCN (IUCN):</b><br>"
    f"<span style='color:{color_map_detailed[('IUCN','DD')]}'>■</span> DD: Dados Insuficientes<br>"
    f"<span style='color:{color_map_detailed[('IUCN','CR')]}'>■</span> CR: Criticamente em Perigo<br>"
    f"<span style='color:{color_map_detailed[('IUCN','EN')]}'>■</span> EN: Em Perigo<br>"
    f"<span style='color:{color_map_detailed[('IUCN','VU')]}'>■</span> VU: Vulnerável<br>"
    f"<span style='color:{color_map_detailed[('IUCN','NT')]}'>■</span> NT: Quase Ameaçado<br>"
    f"<span style='color:{color_map_detailed[('IUCN','LC')]}'>■</span> LC: Pouco Preocupante<br>"
    f"<span style='color:{color_map_detailed[('IUCN','NE')]}'>■</span> NE: Não Avaliado<br><br>"
    "<b>Lista Vermelha Cabo Verde (LVCV):</b><br>"
    f"<span style='color:{color_map_detailed[('LVCV','EX')]}'>■</span> EX: Extinto<br>"
    f"<span style='color:{color_map_detailed[('LVCV','Ind')]}'>■</span> Ind: Indeterminado<br>"
    f"<span style='color:{color_map_detailed[('LVCV','Des')]}'>■</span> Des: Desaparecido<br>"
    f"<span style='color:{color_map_detailed[('LVCV','Rara')]}'>■</span> Rara<br>"
    f"<span style='color:{color_map_detailed[('LVCV','NE')]}'>■</span> NE: Não Avaliado<br>"
    f"<span style='color:{color_map_detailed[('LVCV','DD')]}'>■</span> DD: Dados Insuficientes<br>"
    f"<span style='color:{color_map_detailed[('LVCV','CR')]}'>■</span> CR: Criticamente em Perigo<br>"
    f"<span style='color:{color_map_detailed[('LVCV','EN')]}'>■</span> EN: Em Perigo<br>"
    f"<span style='color:{color_map_detailed[('LVCV','VU')]}'>■</span> VU: Vulnerável<br><br>"
    "<b>Grupo Taxonómico:</b><br>"
)
for g in sorted(unique_groups):
    color_g = group_color_map[g]
    legend_text += f"<span style='color:{color_g}'>■</span> {g}<br>"

fig.update_layout(
    annotations=[dict(
        x=1.2,  # ainda mais à direita
        y=0.5,
        xref="paper",
        yref="paper",
        text="<b>Estatuto de Conservação das espécies da Ilha Brava</b><br>" + legend_text,
        showarrow=False,
        align="left",
        bordercolor="black",
        borderwidth=1,
        borderpad=10,
        bgcolor="white",
        opacity=0.9
    )]
)


fig.show()

import os
print("Ficheiro será guardado em:", os.getcwd())

fig.write_html("conservacao_ilha_brava.html")
