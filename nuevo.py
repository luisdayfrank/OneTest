import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ComparadorTenisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Tenistas")
        self.root.geometry("1000x800")
        
        # Variables
        self.archivo_excel = None
        self.datos_jugador1 = None
        self.datos_jugador2 = None
        self.nombre_jugador1 = ""
        self.nombre_jugador2 = ""
        
        # Crear interfaz
        self.crear_widgets()
        
    def crear_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botón para cargar archivo
        ttk.Button(self.main_frame, text="Cargar Archivo Excel", 
                  command=self.cargar_archivo).grid(row=0, column=0, pady=10)
        
        # Labels para nombres de jugadores
        self.label_jugadores = ttk.LabelFrame(self.main_frame, text="Jugadores", padding="10")
        self.label_jugadores.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Frame para mostrar estadísticas
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Estadísticas Detalladas", padding="10")
        self.stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Frame para gráficas
        self.grafica_frame = ttk.LabelFrame(self.main_frame, text="Análisis Visual", padding="10")
        self.grafica_frame.grid(row=3, column=0, pady=10)
        
        # Área de resultados
        self.resultado_text = tk.Text(self.main_frame, height=8, width=80)
        self.resultado_text.grid(row=4, column=0, pady=10)
        
    def cargar_archivo(self):
        try:
            filename = filedialog.askopenfilename(
                title="Seleccionar archivo Excel",
                filetypes=[("Archivos Excel", "*.xlsx")]
            )
            
            if filename:
                self.archivo_excel = filename
                self.cargar_datos()
                self.analizar_jugadores()
                self.mostrar_graficas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")
    
    def cargar_datos(self):
        try:
            # Cargar datos de ambas hojas
            self.datos_jugador1 = pd.read_excel(self.archivo_excel, sheet_name='Hoja1')
            self.datos_jugador2 = pd.read_excel(self.archivo_excel, sheet_name='Hoja2')
            
            # Obtener nombres de los jugadores (primera fila)
            self.nombre_jugador1 = self.datos_jugador1.iloc[0]['TENISTAS']
            self.nombre_jugador2 = self.datos_jugador2.iloc[0]['TENISTAS']
            
            # Actualizar labels de jugadores
            for widget in self.label_jugadores.winfo_children():
                widget.destroy()
            ttk.Label(self.label_jugadores, text=f"Comparando: {self.nombre_jugador1} vs {self.nombre_jugador2}",
                     font=('Helvetica', 12, 'bold')).grid(row=0, column=0, padx=5)
            
            # Mostrar estadísticas
            self.mostrar_estadisticas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar datos: {str(e)}")
    
    def mostrar_estadisticas(self):
        if self.datos_jugador1 is not None and self.datos_jugador2 is not None:
            # Limpiar stats_frame
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            
            # Calcular estadísticas
            stats1 = self.calcular_estadisticas(self.datos_jugador1)
            stats2 = self.calcular_estadisticas(self.datos_jugador2)
            
            # Crear tabla de estadísticas
            headers = ['Estadística', self.nombre_jugador1, self.nombre_jugador2]
            for col, header in enumerate(headers):
                ttk.Label(self.stats_frame, text=header, font=('Helvetica', 10, 'bold')).grid(
                    row=0, column=col, padx=5, pady=5)
            
            row = 1
            for stat_name in stats1.keys():
                ttk.Label(self.stats_frame, text=stat_name).grid(row=row, column=0, padx=5)
                ttk.Label(self.stats_frame, text=f"{stats1[stat_name]}").grid(row=row, column=1, padx=5)
                ttk.Label(self.stats_frame, text=f"{stats2[stat_name]}").grid(row=row, column=2, padx=5)
                row += 1
    
    def calcular_estadisticas(self, datos):
        stats = {
            "Partidos Ganados": len(datos[datos['W o L'] == 'W']),
            "Partidos Perdidos": len(datos[datos['W o L'] == 'L']),
            "% Victoria": f"{(len(datos[datos['W o L'] == 'W']) / len(datos) * 100):.1f}%",
            "Promedio Sets Ganados": f"{datos['Sets Win'].mean():.2f}",
            "ODDS Promedio": f"{datos['ODDS'].mean():.2f}",
            "Sets Ganados Total": int(datos['Sets Win'].sum()),
            "Promedio Puntos Set 1": f"{datos['Set 1'].mean():.1f}",
            "Promedio Puntos Set 2": f"{datos['Set 2'].mean():.1f}",
            "Promedio Puntos Set 3": f"{datos['Set 3'].mean():.1f}"
        }
        return stats
    
    def mostrar_graficas(self):
        if self.datos_jugador1 is not None and self.datos_jugador2 is not None:
            # Limpiar gráficas anteriores
            for widget in self.grafica_frame.winfo_children():
                widget.destroy()
            
            # Crear nueva figura con 2x2 subplots
            fig = plt.figure(figsize=(12, 8))
            
            # Gráfica 1: Victoria/Derrota
            ax1 = fig.add_subplot(221)
            self.graficar_resultados(ax1)
            
            # Gráfica 2: Sets Ganados
            ax2 = fig.add_subplot(222)
            self.graficar_sets(ax2)
            
            # Gráfica 3: Promedio de puntos por set
            ax3 = fig.add_subplot(223)
            self.graficar_puntos_set(ax3)
            
            # Gráfica 4: ODDS
            ax4 = fig.add_subplot(224)
            self.graficar_odds(ax4)
            
            plt.tight_layout()
            
            # Mostrar gráficas en la interfaz
            canvas = FigureCanvasTkAgg(fig, master=self.grafica_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
    
    def graficar_resultados(self, ax):
        victorias1 = len(self.datos_jugador1[self.datos_jugador1['W o L'] == 'W'])
        derrotas1 = len(self.datos_jugador1[self.datos_jugador1['W o L'] == 'L'])
        victorias2 = len(self.datos_jugador2[self.datos_jugador2['W o L'] == 'W'])
        derrotas2 = len(self.datos_jugador2[self.datos_jugador2['W o L'] == 'L'])
        
        labels = [self.nombre_jugador1, self.nombre_jugador2]
        victorias = [victorias1, victorias2]
        derrotas = [derrotas1, derrotas2]
        
        x = np.arange(len(labels))
        width = 0.35
        
        ax.bar(x - width/2, victorias, width, label='Victorias', color='green')
        ax.bar(x + width/2, derrotas, width, label='Derrotas', color='red')
        
        ax.set_ylabel('Cantidad')
        ax.set_title('Victorias vs Derrotas')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.legend()
    
    def graficar_sets(self, ax):
        sets1 = self.datos_jugador1['Sets Win']
        sets2 = self.datos_jugador2['Sets Win']
        
        ax.boxplot([sets1, sets2], labels=[self.nombre_jugador1, self.nombre_jugador2])
        ax.set_title('Distribución de Sets Ganados')
        ax.set_ylabel('Cantidad de Sets')
        plt.setp(ax.get_xticklabels(), rotation=45)
    
    def graficar_puntos_set(self, ax):
        sets = ['Set 1', 'Set 2', 'Set 3']
        j1_puntos = [self.datos_jugador1[set].mean() for set in sets]
        j2_puntos = [self.datos_jugador2[set].mean() for set in sets]
        
        x = np.arange(len(sets))
        width = 0.35
        
        ax.bar(x - width/2, j1_puntos, width, label=self.nombre_jugador1)
        ax.bar(x + width/2, j2_puntos, width, label=self.nombre_jugador2)
        
        ax.set_ylabel('Promedio de Puntos')
        ax.set_title('Puntos Promedio por Set')
        ax.set_xticks(x)
        ax.set_xticklabels(sets)
        ax.legend()
    
    def graficar_odds(self, ax):
        odds1 = self.datos_jugador1['ODDS']
        odds2 = self.datos_jugador2['ODDS']
        
        ax.hist(odds1, alpha=0.5, label=self.nombre_jugador1, bins=10)
        ax.hist(odds2, alpha=0.5, label=self.nombre_jugador2, bins=10)
        ax.set_title('Distribución de ODDS')
        ax.set_xlabel('ODDS')
        ax.set_ylabel('Frecuencia')
        ax.legend()
    
    def analizar_jugadores(self):
        if self.datos_jugador1 is not None and self.datos_jugador2 is not None:
            # Calcular métricas clave
            victorias1 = len(self.datos_jugador1[self.datos_jugador1['W o L'] == 'W'])
            victorias2 = len(self.datos_jugador2[self.datos_jugador2['W o L'] == 'W'])
            total_partidos1 = len(self.datos_jugador1)
            total_partidos2 = len(self.datos_jugador2)
            
            win_rate1 = victorias1 / total_partidos1 * 100
            win_rate2 = victorias2 / total_partidos2 * 100
            
            promedio_sets1 = self.datos_jugador1['Sets Win'].mean()
            promedio_sets2 = self.datos_jugador2['Sets Win'].mean()
            
            # Generar análisis
            mensaje = f"Análisis Comparativo:\n\n"
            mensaje += f"{self.nombre_jugador1}:\n"
            mensaje += f"- Tasa de victoria: {win_rate1:.1f}%\n"
            mensaje += f"- Promedio de sets ganados: {promedio_sets1:.2f}\n\n"
            
            mensaje += f"{self.nombre_jugador2}:\n"
            mensaje += f"- Tasa de victoria: {win_rate2:.1f}%\n"
            mensaje += f"- Promedio de sets ganados: {promedio_sets2:.2f}\n\n"
            
            # Determinar jugador con mejor rendimiento
            mensaje += "Conclusión: "
            if win_rate1 > win_rate2:
                mensaje += f"{self.nombre_jugador1} muestra mejor rendimiento general"
            elif win_rate2 > win_rate1:
                mensaje += f"{self.nombre_jugador2} muestra mejor rendimiento general"
            else:
                mensaje += "Ambos jugadores muestran rendimiento similar"
            
            # Mostrar resultado
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, mensaje)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComparadorTenisApp(root)
    root.mainloop()
