import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import shutil
from PIL import Image, ImageTk
import re

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Productos - Inversiones Cristian Aaron")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)

        # ========== CONFIGURACIÓN DE ESTILO OSCURO MODERNO ==========
        self.root.configure(bg='#0d1117')  # Fondo principal tipo GitHub dark

        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')

        # Colores base
        bg_oscuro = '#0d1117'
        bg_panel = '#161b22'
        bg_input = '#0d1117'
        fg_texto = '#c9d1d9'
        fg_muted = '#8b949e'
        acento = '#ff6a00'
        acento_hover = '#ff8533'
        borde = '#30363d'

        # Configurar estilos
        self.estilo.configure('TFrame', background=bg_oscuro)
        self.estilo.configure('TLabel', background=bg_oscuro, foreground=fg_texto, font=('Segoe UI', 10))
        self.estilo.configure('TButton', background=bg_panel, foreground=acento, borderwidth=1,
                              relief='solid', focusthickness=0, padding=(8, 4))
        self.estilo.map('TButton',
                        background=[('active', acento), ('pressed', '#cc5500')],
                        foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

        self.estilo.configure('TEntry', fieldbackground=bg_input, foreground=fg_texto,
                              insertcolor=acento, borderwidth=1, relief='solid')
        self.estilo.map('TEntry', fieldbackground=[('focus', bg_input)])

        self.estilo.configure('TCombobox', fieldbackground=bg_input, foreground=fg_texto,
                              arrowcolor=acento, borderwidth=1, relief='solid')
        self.estilo.map('TCombobox', fieldbackground=[('focus', bg_input)])

        self.estilo.configure('TListbox', background=bg_panel, foreground=fg_texto,
                              selectbackground=acento, selectforeground='#ffffff',
                              borderwidth=1, relief='solid')

        self.estilo.configure('TSeparator', background=borde)

        # Estilo para Checkbutton
        self.estilo.configure('TCheckbutton', background=bg_oscuro, foreground=fg_texto)

        # Variables de ruta
        self.json_path = "productos.json"
        self.img_dir = "img"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        # Datos
        self.productos = []
        self.tipos_producto = []
        self.cargar_json()
        self.categorias = self.obtener_categorias()

        self.producto_actual = None
        self.categoria_actual = None
        self.imagen_principal_path = None
        self.imagenes_extra_paths = []

        # Construir interfaz
        self.crear_widgets()
        self.cargar_lista_categorias()
        self.cargar_lista_tipos()

    # ========== CARGA Y GUARDADO ==========

    def cargar_json(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict) and 'tipos_producto' in data:
                        self.tipos_producto = data.get('tipos_producto', [])
                        self.productos = data.get('productos', [])
                    else:
                        self.productos = data if isinstance(data, list) else []
                        self.tipos_producto = []
                except:
                    self.productos = []
                    self.tipos_producto = []
        else:
            self.productos = []
            self.tipos_producto = ["pan de perro", "pan de hamburguesa", "salchicha", "queso", "bebida", "snack"]
            self.guardar_json()

        for p in self.productos:
            if 'cantidad_por_paquete' not in p:
                p['cantidad_por_paquete'] = 1
            if 'tipo_producto' not in p:
                p['tipo_producto'] = ''
            if 'disponible' not in p:
                p['disponible'] = True

    def guardar_json(self):
        data = {
            'tipos_producto': self.tipos_producto,
            'productos': self.productos
        }
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def obtener_categorias(self):
        cats = set()
        for p in self.productos:
            if 'categoria' in p and p['categoria']:
                cats.add(p['categoria'])
        return sorted(list(cats))

    def actualizar_categorias(self):
        self.categorias = self.obtener_categorias()
        self.cargar_lista_categorias()

    # ========== CONSTRUCCIÓN DE LA INTERFAZ ==========

    def crear_widgets(self):
        # Contenedor principal con padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ---------- PANEL SUPERIOR (título) ----------
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 15))

        titulo = ttk.Label(top_frame, text="⚡ GESTOR DE PRODUCTOS", font=('Segoe UI', 16, 'bold'), foreground='#ff6a00')
        titulo.pack(side=tk.LEFT)

        # Separador
        sep = ttk.Separator(main_container, orient='horizontal')
        sep.pack(fill=tk.X, pady=(0, 15))

        # ---------- PANEL PRINCIPAL (3 columnas con PanedWindow) ----------
        main_pane = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # ---- COLUMNA 1: CATEGORÍAS (ancho fijo 250) ----
        left_frame = ttk.Frame(main_pane, width=250)
        main_pane.add(left_frame, weight=0)

        # Título con fondo sutil
        titulo_cat = ttk.Label(left_frame, text="📂 CATEGORÍAS", font=('Segoe UI', 12, 'bold'), foreground='#ff6a00')
        titulo_cat.pack(pady=(0, 8))

        self.lista_categorias = tk.Listbox(left_frame, bg='#161b22', fg='#c9d1d9',
                                           selectbackground='#ff6a00', selectforeground='#ffffff',
                                           font=('Segoe UI', 10), height=22, relief='flat',
                                           highlightthickness=1, highlightcolor='#ff6a00')
        self.lista_categorias.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.lista_categorias.bind('<<ListboxSelect>>', self.on_seleccionar_categoria)

        # Botones de categorías
        btn_cat_frame = ttk.Frame(left_frame)
        btn_cat_frame.pack(fill=tk.X, pady=4)
        ttk.Button(btn_cat_frame, text="➕ Nueva", command=self.crear_categoria).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_cat_frame, text="✖ Eliminar", command=self.eliminar_categoria).pack(side=tk.LEFT, padx=2)

        # ---- COLUMNA 2: PRODUCTOS (se expande) ----
        center_frame = ttk.Frame(main_pane)
        main_pane.add(center_frame, weight=1)

        # Título de categoría seleccionada
        self.label_categoria_seleccionada = ttk.Label(center_frame, text="📦 Selecciona una categoría",
                                                      font=('Segoe UI', 12, 'bold'), foreground='#ff6a00')
        self.label_categoria_seleccionada.pack(pady=(0, 8))

        # Lista de productos con scroll
        list_frame = ttk.Frame(center_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.lista_productos = tk.Listbox(list_frame, bg='#161b22', fg='#c9d1d9',
                                          selectbackground='#ff6a00', selectforeground='#ffffff',
                                          font=('Segoe UI', 10), height=20, relief='flat',
                                          highlightthickness=1, highlightcolor='#ff6a00')
        self.lista_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_prod = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.lista_productos.yview)
        scroll_prod.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_productos.config(yscrollcommand=scroll_prod.set)
        self.lista_productos.bind('<<ListboxSelect>>', self.on_seleccionar_producto)

        # Botones de producto
        btn_prod_frame = ttk.Frame(center_frame)
        btn_prod_frame.pack(fill=tk.X, pady=4)
        ttk.Button(btn_prod_frame, text="➕ Nuevo Producto", command=self.nuevo_producto).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_prod_frame, text="🗑 Eliminar", command=self.eliminar_producto).pack(side=tk.LEFT, padx=2)

        # ---- COLUMNA 3: EDICIÓN (ancho fijo 480) ----
        right_frame = ttk.Frame(main_pane, width=480)
        main_pane.add(right_frame, weight=0)

        # Título de edición
        ttk.Label(right_frame, text="✏️ EDICIÓN DE PRODUCTO", font=('Segoe UI', 12, 'bold'), foreground='#ff6a00').pack(pady=(0, 8))

        # Canvas con scroll para el contenido
        canvas = tk.Canvas(right_frame, bg='#0d1117', highlightthickness=0)
        scroll_y = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.edit_frame = ttk.Frame(canvas)

        self.edit_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.edit_frame, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- CAMPOS DE EDICIÓN (organizados en secciones) ----------
        row = 0

        # --- Sección: Información básica ---
        self._crear_separador(self.edit_frame, row, "INFORMACIÓN BÁSICA")
        row += 1

        # Nombre
        ttk.Label(self.edit_frame, text="Nombre:").grid(row=row, column=0, sticky='w', pady=4)
        self.entry_nombre = ttk.Entry(self.edit_frame, width=40)
        self.entry_nombre.grid(row=row, column=1, columnspan=2, sticky='ew', pady=4, padx=(0, 10))
        row += 1

        # Categoría
        ttk.Label(self.edit_frame, text="Categoría:").grid(row=row, column=0, sticky='w', pady=4)
        self.combo_categoria = ttk.Combobox(self.edit_frame, values=self.categorias, width=30)
        self.combo_categoria.grid(row=row, column=1, sticky='w', pady=4)
        ttk.Button(self.edit_frame, text="+", width=3, command=self.crear_categoria_desde_combo).grid(row=row, column=2, padx=4)
        row += 1

        # --- Sección: Atributos del producto ---
        self._crear_separador(self.edit_frame, row, "ATRIBUTOS DEL PRODUCTO")
        row += 1

        # Tipo de producto
        ttk.Label(self.edit_frame, text="Tipo:").grid(row=row, column=0, sticky='w', pady=4)
        self.combo_tipo = ttk.Combobox(self.edit_frame, values=self.tipos_producto, width=30)
        self.combo_tipo.grid(row=row, column=1, sticky='w', pady=4)
        ttk.Button(self.edit_frame, text="⚙", width=3, command=self.gestionar_tipos).grid(row=row, column=2, padx=4)
        row += 1

        # Cantidad por paquete
        ttk.Label(self.edit_frame, text="Cant. por paquete:").grid(row=row, column=0, sticky='w', pady=4)
        self.entry_cantidad = ttk.Entry(self.edit_frame, width=20)
        self.entry_cantidad.grid(row=row, column=1, sticky='w', pady=4)
        row += 1

        # Precio
        ttk.Label(self.edit_frame, text="Precio ($):").grid(row=row, column=0, sticky='w', pady=4)
        self.entry_precio = ttk.Entry(self.edit_frame, width=20)
        self.entry_precio.grid(row=row, column=1, sticky='w', pady=4)
        row += 1

        # Disponible
        self.var_disponible = tk.BooleanVar(value=True)
        ttk.Label(self.edit_frame, text="Disponible:").grid(row=row, column=0, sticky='w', pady=4)
        ttk.Checkbutton(self.edit_frame, variable=self.var_disponible, style='TCheckbutton').grid(row=row, column=1, sticky='w', pady=4)
        row += 1

        # --- Sección: Descripciones ---
        self._crear_separador(self.edit_frame, row, "DESCRIPCIONES")
        row += 1

        ttk.Label(self.edit_frame, text="Descripción corta:").grid(row=row, column=0, sticky='nw', pady=4)
        self.text_desc = tk.Text(self.edit_frame, height=3, width=40, bg='#0d1117', fg='#c9d1d9',
                                 insertbackground='#ff6a00', relief='solid', borderwidth=1,
                                 highlightthickness=1, highlightcolor='#ff6a00')
        self.text_desc.grid(row=row, column=1, columnspan=2, sticky='ew', pady=4, padx=(0, 10))
        row += 1

        ttk.Label(self.edit_frame, text="Descripción larga:").grid(row=row, column=0, sticky='nw', pady=4)
        self.text_desc_larga = tk.Text(self.edit_frame, height=5, width=40, bg='#0d1117', fg='#c9d1d9',
                                       insertbackground='#ff6a00', relief='solid', borderwidth=1,
                                       highlightthickness=1, highlightcolor='#ff6a00')
        self.text_desc_larga.grid(row=row, column=1, columnspan=2, sticky='ew', pady=4, padx=(0, 10))
        row += 1

        # --- Sección: Imágenes ---
        self._crear_separador(self.edit_frame, row, "IMÁGENES")
        row += 1

        # Imagen principal
        ttk.Label(self.edit_frame, text="Principal:").grid(row=row, column=0, sticky='w', pady=4)
        self.label_img_principal = ttk.Label(self.edit_frame, text="(sin imagen)", foreground='#8b949e')
        self.label_img_principal.grid(row=row, column=1, sticky='w', pady=4)
        ttk.Button(self.edit_frame, text="📷 Cargar", command=self.cargar_imagen_principal).grid(row=row, column=2, padx=4)
        row += 1

        # Imágenes extra
        ttk.Label(self.edit_frame, text="Extra:").grid(row=row, column=0, sticky='nw', pady=4)
        self.lista_imagenes_extra = tk.Listbox(self.edit_frame, height=4, width=40, bg='#0d1117', fg='#c9d1d9',
                                               relief='solid', borderwidth=1, highlightthickness=1,
                                               highlightcolor='#ff6a00')
        self.lista_imagenes_extra.grid(row=row, column=1, columnspan=2, sticky='ew', pady=4, padx=(0, 10))
        row += 1

        # Botones de imágenes extra
        btn_extra_frame = ttk.Frame(self.edit_frame)
        btn_extra_frame.grid(row=row, column=1, columnspan=2, sticky='w', pady=4)
        ttk.Button(btn_extra_frame, text="➕ Añadir", command=self.cargar_imagen_extra).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_extra_frame, text="✖ Eliminar", command=self.eliminar_imagen_extra).pack(side=tk.LEFT, padx=2)
        row += 1

        # --- Vista previa ---
        self.preview_frame = ttk.Frame(self.edit_frame)
        self.preview_frame.grid(row=row, column=0, columnspan=3, pady=10)
        self.preview_label = ttk.Label(self.preview_frame, text="🖼 Vista previa", foreground='#8b949e')
        self.preview_label.pack()
        row += 1

        # --- Botones de acción ---
        btn_guardar_frame = ttk.Frame(self.edit_frame)
        btn_guardar_frame.grid(row=row, column=0, columnspan=3, pady=20)
        ttk.Button(btn_guardar_frame, text="💾 Guardar Cambios", command=self.guardar_producto).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_guardar_frame, text="↩ Cancelar", command=self.cancelar_edicion).pack(side=tk.LEFT, padx=10)
        row += 1

        # --- Estado ---
        self.label_estado = ttk.Label(self.edit_frame, text="", foreground='#ff6a00')
        self.label_estado.grid(row=row, column=0, columnspan=3, pady=8)

        # Configurar pesos para expansión
        self.edit_frame.columnconfigure(1, weight=1)

    def _crear_separador(self, parent, row, texto):
        """Crea un separador con título en una fila"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=(10, 5))
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 10))
        lbl = ttk.Label(frame, text=texto, foreground='#8b949e', font=('Segoe UI', 9, 'bold'))
        lbl.pack(side=tk.RIGHT)

    # ========== FUNCIONES DE LISTA ==========

    def cargar_lista_categorias(self):
        self.lista_categorias.delete(0, tk.END)
        for cat in self.categorias:
            count = len([p for p in self.productos if p.get('categoria') == cat])
            self.lista_categorias.insert(tk.END, f"{cat} ({count})")

    def on_seleccionar_categoria(self, event):
        seleccion = self.lista_categorias.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        cat_text = self.lista_categorias.get(index)
        self.categoria_actual = cat_text.split(' (')[0]
        self.label_categoria_seleccionada.config(text=f"📦 {self.categoria_actual}")
        self.cargar_productos_por_categoria(self.categoria_actual)

    def cargar_productos_por_categoria(self, categoria):
        self.lista_productos.delete(0, tk.END)
        productos_cat = [p for p in self.productos if p.get('categoria') == categoria]
        for p in productos_cat:
            disponible = "✅" if p.get('disponible', True) else "❌"
            tipo = p.get('tipo_producto', '')
            cantidad = p.get('cantidad_por_paquete', 1)
            nombre = p.get('nombre', 'Sin nombre')
            self.lista_productos.insert(tk.END, f"{nombre}  |  {tipo}  |  {cantidad} und  |  {disponible}")

    def on_seleccionar_producto(self, event):
        seleccion = self.lista_productos.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        productos_cat = [p for p in self.productos if p.get('categoria') == self.categoria_actual]
        if index < len(productos_cat):
            producto = productos_cat[index]
            self.producto_actual = self.productos.index(producto)
            self.cargar_datos_producto(self.producto_actual)

    # ========== CARGA DE DATOS EN EL FORMULARIO ==========

    def cargar_datos_producto(self, indice):
        p = self.productos[indice]
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, p.get('nombre', ''))

        cat = p.get('categoria', '')
        self.combo_categoria.set(cat if cat in self.categorias else '')

        tipo = p.get('tipo_producto', '')
        self.combo_tipo.set(tipo if tipo in self.tipos_producto else '')

        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, str(p.get('cantidad_por_paquete', 1)))

        self.entry_precio.delete(0, tk.END)
        self.entry_precio.insert(0, str(p.get('precio', 0)))

        self.var_disponible.set(p.get('disponible', True))

        self.text_desc.delete(1.0, tk.END)
        self.text_desc.insert(1.0, p.get('descripcion', ''))

        self.text_desc_larga.delete(1.0, tk.END)
        self.text_desc_larga.insert(1.0, p.get('descripcion_larga', ''))

        self.imagen_principal_path = p.get('imagen', '')
        self.label_img_principal.config(text=os.path.basename(self.imagen_principal_path) if self.imagen_principal_path else "(sin imagen)")
        self.mostrar_preview_imagen(self.imagen_principal_path)

        self.lista_imagenes_extra.delete(0, tk.END)
        self.imagenes_extra_paths = p.get('imagenes_extra', [])
        for extra in self.imagenes_extra_paths:
            self.lista_imagenes_extra.insert(tk.END, os.path.basename(extra))

        self.label_estado.config(text="✅ Producto cargado")

    # ========== GUARDAR ==========

    def guardar_producto(self):
        if self.producto_actual is None:
            messagebox.showwarning("Aviso", "Selecciona un producto primero.")
            return

        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return

        try:
            precio = float(self.entry_precio.get().strip())
        except:
            messagebox.showerror("Error", "El precio debe ser un número.")
            return

        try:
            cantidad = int(self.entry_cantidad.get().strip())
        except:
            cantidad = 1

        categoria = self.combo_categoria.get().strip()
        if not categoria:
            messagebox.showerror("Error", "La categoría es obligatoria.")
            return

        tipo_producto = self.combo_tipo.get().strip()
        descripcion = self.text_desc.get(1.0, tk.END).strip()
        descripcion_larga = self.text_desc_larga.get(1.0, tk.END).strip()
        disponible = self.var_disponible.get()

        p = self.productos[self.producto_actual]
        p['nombre'] = nombre
        p['categoria'] = categoria
        p['precio'] = precio
        p['cantidad_por_paquete'] = cantidad
        p['tipo_producto'] = tipo_producto
        p['disponible'] = disponible
        p['descripcion'] = descripcion
        p['descripcion_larga'] = descripcion_larga
        if self.imagen_principal_path:
            p['imagen'] = self.imagen_principal_path
        if self.imagenes_extra_paths:
            p['imagenes_extra'] = self.imagenes_extra_paths

        self.guardar_json()
        self.actualizar_categorias()
        self.cargar_productos_por_categoria(categoria)
        self.cargar_lista_categorias()
        self.label_estado.config(text="✅ Producto guardado correctamente")
        messagebox.showinfo("Éxito", "Producto guardado.")

    # ========== NUEVO Y ELIMINAR PRODUCTO ==========

    def nuevo_producto(self):
        if not self.categoria_actual:
            messagebox.showwarning("Aviso", "Selecciona una categoría primero.")
            return
        nuevo_id = max([p.get('id', 0) for p in self.productos]) + 1 if self.productos else 1
        nuevo = {
            "id": nuevo_id,
            "nombre": "Nuevo Producto",
            "categoria": self.categoria_actual,
            "precio": 0.0,
            "cantidad_por_paquete": 1,
            "tipo_producto": "",
            "disponible": True,
            "descripcion": "",
            "descripcion_larga": "",
            "imagen": "",
            "imagenes_extra": []
        }
        self.productos.append(nuevo)
        self.guardar_json()
        self.cargar_productos_por_categoria(self.categoria_actual)
        productos_cat = [p for p in self.productos if p.get('categoria') == self.categoria_actual]
        indice = len(productos_cat) - 1
        self.lista_productos.selection_set(indice)
        self.producto_actual = self.productos.index(productos_cat[indice])
        self.cargar_datos_producto(self.producto_actual)
        self.label_estado.config(text="✅ Nuevo producto creado")

    def eliminar_producto(self):
        if self.producto_actual is None:
            messagebox.showwarning("Aviso", "Selecciona un producto para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{self.productos[self.producto_actual].get('nombre')}'?"):
            del self.productos[self.producto_actual]
            self.guardar_json()
            self.cargar_productos_por_categoria(self.categoria_actual)
            self.producto_actual = None
            self.limpiar_campos()
            self.actualizar_categorias()
            self.label_estado.config(text="🗑 Producto eliminado")

    # ========== GESTIÓN DE CATEGORÍAS ==========

    def crear_categoria_desde_combo(self):
        nueva = simpledialog.askstring("Nueva categoría", "Nombre de la nueva categoría:")
        if nueva and nueva.strip():
            nueva = nueva.strip()
            if nueva not in self.categorias:
                self.categorias.append(nueva)
                self.categorias.sort()
                self.actualizar_combo_categorias()
                self.combo_categoria.set(nueva)
                self.cargar_lista_categorias()
                self.label_estado.config(text=f"✅ Categoría '{nueva}' creada")
            else:
                messagebox.showinfo("Info", "La categoría ya existe.")

    def crear_categoria(self):
        self.crear_categoria_desde_combo()

    def eliminar_categoria(self):
        if not self.categorias:
            messagebox.showinfo("Info", "No hay categorías para eliminar.")
            return
        cat_seleccionada = simpledialog.askstring("Eliminar categoría",
            f"Categorías disponibles: {', '.join(self.categorias)}\nEscribe el nombre exacto:")
        if cat_seleccionada:
            cat_seleccionada = cat_seleccionada.strip()
            if cat_seleccionada in self.categorias:
                productos_en_cat = [p for p in self.productos if p.get('categoria') == cat_seleccionada]
                if productos_en_cat:
                    messagebox.showerror("Error",
                        f"No se puede eliminar '{cat_seleccionada}' porque tiene {len(productos_en_cat)} producto(s).")
                    return
                self.categorias.remove(cat_seleccionada)
                self.actualizar_combo_categorias()
                self.cargar_lista_categorias()
                self.label_estado.config(text=f"🗑 Categoría '{cat_seleccionada}' eliminada")
            else:
                messagebox.showerror("Error", f"La categoría '{cat_seleccionada}' no existe.")

    def actualizar_combo_categorias(self):
        self.combo_categoria['values'] = self.categorias

    # ========== GESTIÓN DE TIPOS DE PRODUCTO ==========

    def gestionar_tipos(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Gestionar tipos de producto")
        ventana.geometry("450x450")
        ventana.configure(bg='#0d1117')
        ventana.transient(self.root)
        ventana.grab_set()

        ttk.Label(ventana, text="📋 TIPOS DE PRODUCTO", font=('Segoe UI', 14, 'bold'), foreground='#ff6a00').pack(pady=15)

        frame_lista = ttk.Frame(ventana)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        lista_tipos = tk.Listbox(frame_lista, bg='#161b22', fg='#c9d1d9', selectbackground='#ff6a00',
                                 selectforeground='#ffffff', font=('Segoe UI', 10), relief='flat',
                                 highlightthickness=1, highlightcolor='#ff6a00')
        lista_tipos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=lista_tipos.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        lista_tipos.config(yscrollcommand=scroll.set)

        for t in self.tipos_producto:
            lista_tipos.insert(tk.END, t)

        def añadir_tipo():
            nuevo = simpledialog.askstring("Nuevo tipo", "Nombre del nuevo tipo:")
            if nuevo and nuevo.strip():
                nuevo = nuevo.strip()
                if nuevo not in self.tipos_producto:
                    self.tipos_producto.append(nuevo)
                    self.tipos_producto.sort()
                    lista_tipos.insert(tk.END, nuevo)
                    self.actualizar_combo_tipos()
                    self.guardar_json()
                    self.label_estado.config(text=f"✅ Tipo '{nuevo}' añadido")
                else:
                    messagebox.showinfo("Info", "El tipo ya existe.")

        def eliminar_tipo():
            seleccion = lista_tipos.curselection()
            if seleccion:
                tipo = lista_tipos.get(seleccion[0])
                usado = any(p.get('tipo_producto') == tipo for p in self.productos)
                if usado:
                    messagebox.showerror("Error", f"No se puede eliminar '{tipo}' porque está en uso.")
                    return
                self.tipos_producto.remove(tipo)
                lista_tipos.delete(seleccion[0])
                self.actualizar_combo_tipos()
                self.guardar_json()
                self.label_estado.config(text=f"🗑 Tipo '{tipo}' eliminado")

        btn_frame = ttk.Frame(ventana)
        btn_frame.pack(fill=tk.X, pady=15)
        ttk.Button(btn_frame, text="➕ Añadir", command=añadir_tipo).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="✖ Eliminar", command=eliminar_tipo).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cerrar", command=ventana.destroy).pack(side=tk.RIGHT, padx=10)

    def actualizar_combo_tipos(self):
        self.combo_tipo['values'] = self.tipos_producto

    def cargar_lista_tipos(self):
        self.actualizar_combo_tipos()

    # ========== IMÁGENES ==========

    def cargar_imagen_principal(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen principal",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.webp")]
        )
        if file_path:
            nombre_archivo = self.generar_nombre_archivo(file_path)
            destino = os.path.join(self.img_dir, nombre_archivo)
            shutil.copy2(file_path, destino)
            self.imagen_principal_path = destino
            self.label_img_principal.config(text=nombre_archivo)
            self.mostrar_preview_imagen(destino)
            self.label_estado.config(text="✅ Imagen principal actualizada")

    def cargar_imagen_extra(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar imágenes extra",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.webp")]
        )
        for file_path in files:
            nombre_archivo = self.generar_nombre_archivo(file_path)
            destino = os.path.join(self.img_dir, nombre_archivo)
            shutil.copy2(file_path, destino)
            self.imagenes_extra_paths.append(destino)
            self.lista_imagenes_extra.insert(tk.END, nombre_archivo)
        self.label_estado.config(text=f"✅ {len(files)} imagen(es) extra añadidas")

    def eliminar_imagen_extra(self):
        seleccion = self.lista_imagenes_extra.curselection()
        if seleccion:
            indice = seleccion[0]
            del self.imagenes_extra_paths[indice]
            self.lista_imagenes_extra.delete(indice)
            self.label_estado.config(text="🗑 Imagen extra eliminada")

    def generar_nombre_archivo(self, path):
        nombre_base = self.entry_nombre.get().strip() or "producto"
        nombre_limpio = re.sub(r'[^a-zA-Z0-9_]', '_', nombre_base)
        ext = os.path.splitext(path)[1]
        contador = 1
        nuevo_nombre = f"{nombre_limpio}{ext}"
        while os.path.exists(os.path.join(self.img_dir, nuevo_nombre)):
            nuevo_nombre = f"{nombre_limpio}_{contador}{ext}"
            contador += 1
        return nuevo_nombre

    def mostrar_preview_imagen(self, path):
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((180, 180))
                self.preview_img = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.preview_img)
                self.preview_label.image = self.preview_img
            except:
                self.preview_label.config(image='', text="⚠️ No se puede mostrar la imagen")
        else:
            self.preview_label.config(image='', text="🖼 Vista previa")

    # ========== UTILIDADES ==========

    def cancelar_edicion(self):
        if self.producto_actual is not None:
            self.cargar_datos_producto(self.producto_actual)
        self.label_estado.config(text="↩ Edición cancelada")

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.combo_categoria.set('')
        self.combo_tipo.set('')
        self.entry_cantidad.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.var_disponible.set(True)
        self.text_desc.delete(1.0, tk.END)
        self.text_desc_larga.delete(1.0, tk.END)
        self.label_img_principal.config(text="(sin imagen)")
        self.lista_imagenes_extra.delete(0, tk.END)
        self.imagen_principal_path = None
        self.imagenes_extra_paths = []
        self.preview_label.config(image='', text="🖼 Vista previa")

    # ========== EJECUCIÓN ==========

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductManager(root)
    root.mainloop()