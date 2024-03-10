"""

Idea to print a table with the steps and the description of each step

"""
from rich import print as rp
from rich.table import Table
from rich.columns import Columns

sample = {'variable': 1234, 'variable_2': 'value_2'}
num_stages = 6
columns_layout = []
table = []
for i in range(num_stages):
    table.append(Table())
    table[i].add_column(f"Esta sería la etapa #{i}",
                        justify="center", style="cyan", no_wrap=True)
    table[i].add_row(f"Descripción de la etapa_{i}")
    s = ""
    for k, v in sample.items():
        s += f"{k}: {v}\n"
    table[i].add_row(s)
    columns_layout.append(table[i])
    if i < 6-1:
        columns_layout.append("\n->")
columns = Columns(columns_layout)
rp(columns)
