import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime

class GerenciadorInvestimentos:
    def __init__(self):
        self.investimentos = pd.DataFrame(columns=['Tipo', 'Nome', 'Valor Investido', 'Rendimento Mensal', 'Data'])

    def adicionar_investimento(self, tipo, nome, valor_investido, rendimento_mensal, data):
        try:
            data = datetime.datetime.strptime(data, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Data deve estar no formato YYYY-MM-DD")

        novo_investimento = {
            'Tipo': tipo,
            'Nome': nome,
            'Valor Investido': valor_investido,
            'Rendimento Mensal': rendimento_mensal,
            'Data': data
        }
        self.investimentos = self.investimentos.append(novo_investimento, ignore_index=True)

    def calcular_rendimentos(self):
        self.investimentos['Rendimento Anual'] = self.investimentos['Rendimento Mensal'] * 12
        self.investimentos['Rendimento Total'] = self.investimentos['Rendimento Mensal'] * (
            datetime.datetime.now().year - self.investimentos['Data'].dt.year + 1
        )
        return self.investimentos

    def mostrar_resumo(self):
        resumo = self.investimentos.groupby('Tipo').agg({
            'Valor Investido': 'sum',
            'Rendimento Mensal': 'sum'
        })
        resumo['Rendimento Anual'] = resumo['Rendimento Mensal'] * 12
        return resumo

    def gerar_grafico(self):
        resumo = self.mostrar_resumo()
        resumo['Valor Investido'].plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title('Distribuição de Investimentos')
        plt.ylabel('')
        plt.show()

    def editar_investimento(self, nome, valor_investido=None, rendimento_mensal=None, data=None):
        if nome not in self.investimentos['Nome'].values:
            raise ValueError("Investimento não encontrado.")

        if valor_investido is not None:
            self.investimentos.loc[self.investimentos['Nome'] == nome, 'Valor Investido'] = valor_investido

        if rendimento_mensal is not None:
            self.investimentos.loc[self.investimentos['Nome'] == nome, 'Rendimento Mensal'] = rendimento_mensal

        if data is not None:
            try:
                data = datetime.datetime.strptime(data, '%Y-%m-%d')
                self.investimentos.loc[self.investimentos['Nome'] == nome, 'Data'] = data
            except ValueError:
                raise ValueError("Data deve estar no formato YYYY-MM-DD")

    def excluir_investimento(self, nome):
        if nome not in self.investimentos['Nome'].values:
            raise ValueError("Investimento não encontrado.")

        self.investimentos = self.investimentos[self.investimentos['Nome'] != nome]

    def exportar_dados(self, caminho):
        self.investimentos.to_csv(caminho, index=False)

    def importar_dados(self, caminho):
        self.investimentos = pd.read_csv(caminho, parse_dates=['Data'])

class InterfaceGrafica:
    def __init__(self, root):
        self.gerenciador = GerenciadorInvestimentos()

        self.root = root
        self.root.title("Gerenciador de Investimentos")

        self.tree = ttk.Treeview(root, columns=("Tipo", "Nome", "Valor Investido", "Rendimento Mensal", "Data"), show="headings")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Valor Investido", text="Valor Investido")
        self.tree.heading("Rendimento Mensal", text="Rendimento Mensal")
        self.tree.heading("Data", text="Data")
        self.tree.pack(fill=tk.BOTH, expand=True)

        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Button(frame, text="Adicionar", command=self.adicionar_investimento).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Excluir", command=self.excluir_investimento).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Gerar Gráfico", command=self.gerar_grafico).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Exportar", command=self.exportar_dados).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Importar", command=self.importar_dados).pack(side=tk.LEFT, padx=5)

    def adicionar_investimento(self):
        popup = tk.Toplevel(self.root)
        popup.title("Adicionar Investimento")

        tk.Label(popup, text="Tipo:").grid(row=0, column=0, padx=5, pady=5)
        tipo_entry = tk.Entry(popup)
        tipo_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(popup, text="Nome:").grid(row=1, column=0, padx=5, pady=5)
        nome_entry = tk.Entry(popup)
        nome_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(popup, text="Valor Investido:").grid(row=2, column=0, padx=5, pady=5)
        valor_entry = tk.Entry(popup)
        valor_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(popup, text="Rendimento Mensal:").grid(row=3, column=0, padx=5, pady=5)
        rendimento_entry = tk.Entry(popup)
        rendimento_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(popup, text="Data (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5)
        data_entry = tk.Entry(popup)
        data_entry.grid(row=4, column=1, padx=5, pady=5)

        def salvar():
            try:
                self.gerenciador.adicionar_investimento(
                    tipo_entry.get(), nome_entry.get(), float(valor_entry.get()), float(rendimento_entry.get()), data_entry.get()
                )
                self.atualizar_tabela()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(popup, text="Salvar", command=salvar).grid(row=5, column=0, columnspan=2, pady=10)

    def excluir_investimento(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um investimento para excluir.")
            return

        nome = self.tree.item(selecionado, "values")[1]
        try:
            self.gerenciador.excluir_investimento(nome)
            self.atualizar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def gerar_grafico(self):
        try:
            self.gerenciador.gerar_grafico()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def exportar_dados(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if caminho:
            self.gerenciador.exportar_dados(caminho)

    def importar_dados(self):
        caminho = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if caminho:
            self.gerenciador.importar_dados(caminho)
            self.atualizar_tabela()

    def atualizar_tabela(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, investimento in self.gerenciador.investimentos.iterrows():
            self.tree.insert("", tk.END, values=investimento.tolist())

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
