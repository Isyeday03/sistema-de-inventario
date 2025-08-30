import json
import os
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime


class Producto:
    """
    Clase que representa un producto en el inventario.
    Utiliza encapsulación para proteger los atributos y validar datos.
    """

    def __init__(self, id_producto: str, nombre: str, cantidad: int, precio: float):
        """
        Inicializa un producto con validación de datos.

        Args:
            id_producto (str): ID único del producto
            nombre (str): Nombre del producto
            cantidad (int): Cantidad en inventario
            precio (float): Precio unitario del producto
        """
        self.__id_producto = self._validar_id(id_producto)
        self.__nombre = self._validar_nombre(nombre)
        self.__cantidad = self._validar_cantidad(cantidad)
        self.__precio = self._validar_precio(precio)
        self.__fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Métodos de validación privados
    def _validar_id(self, id_producto: str) -> str:
        if not isinstance(id_producto, str) or not id_producto.strip():
            raise ValueError("El ID del producto debe ser una cadena no vacía")
        return id_producto.strip().upper()

    def _validar_nombre(self, nombre: str) -> str:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del producto debe ser una cadena no vacía")
        return nombre.strip().title()

    def _validar_cantidad(self, cantidad: int) -> int:
        if not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad debe ser un número entero no negativo")
        return cantidad

    def _validar_precio(self, precio: float) -> float:
        if not isinstance(precio, (int, float)) or precio < 0:
            raise ValueError("El precio debe ser un número no negativo")
        return float(precio)

    # Propiedades (getters y setters) con validación
    @property
    def id_producto(self) -> str:
        return self.__id_producto

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        self.__nombre = self._validar_nombre(valor)

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        self.__cantidad = self._validar_cantidad(valor)

    @property
    def precio(self) -> float:
        return self.__precio

    @precio.setter
    def precio(self, valor: float):
        self.__precio = self._validar_precio(valor)

    @property
    def fecha_creacion(self) -> str:
        return self.__fecha_creacion

    def calcular_valor_total(self) -> float:
        """Calcula el valor total del producto (cantidad * precio)"""
        return self.__cantidad * self.__precio

    def to_dict(self) -> dict:
        """Convierte el producto a diccionario para serialización"""
        return {
            'id_producto': self.__id_producto,
            'nombre': self.__nombre,
            'cantidad': self.__cantidad,
            'precio': self.__precio,
            'fecha_creacion': self.__fecha_creacion
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Crea un producto desde un diccionario"""
        producto = cls(
            data['id_producto'],
            data['nombre'],
            data['cantidad'],
            data['precio']
        )
        producto._Producto__fecha_creacion = data.get('fecha_creacion', producto._Producto__fecha_creacion)
        return producto

    def __str__(self) -> str:
        return f"ID: {self.__id_producto} | {self.__nombre} | Cantidad: {self.__cantidad} | Precio: ${self.__precio:.2f}"

    def __repr__(self) -> str:
        return f"Producto('{self.__id_producto}', '{self.__nombre}', {self.__cantidad}, {self.__precio})"


class Inventario:
    """
    Clase que gestiona el inventario utilizando diferentes colecciones para optimizar operaciones.

    Colecciones utilizadas:
    - Diccionario: Para acceso rápido O(1) por ID
    - Conjunto: Para IDs únicos y verificación rápida de existencia
    - Lista: Para operaciones ordenadas y filtros
    """

    def __init__(self, archivo_inventario: str = "inventario.json"):
        """
        Inicializa el inventario con colecciones optimizadas.

        Args:
            archivo_inventario (str): Ruta del archivo de persistencia
        """
        # Diccionario principal: ID -> Producto (acceso O(1))
        self.__productos: Dict[str, Producto] = {}

        # Conjunto de IDs para verificación rápida de existencia O(1)
        self.__ids_productos: Set[str] = set()

        # Diccionario para búsqueda por nombre (nombre_normalizado -> lista de IDs)
        self.__indice_nombres: Dict[str, List[str]] = {}

        # Archivo de persistencia
        self.__archivo_inventario = archivo_inventario

        # Cargar inventario existente al inicializar
        self.cargar_inventario()

    def _normalizar_nombre(self, nombre: str) -> str:
        """Normaliza nombres para búsqueda insensible a mayúsculas"""
        return nombre.lower().strip()

    def _actualizar_indice_nombres(self, producto: Producto):
        """Actualiza el índice de nombres para búsqueda rápida"""
        nombre_norm = self._normalizar_nombre(producto.nombre)
        if nombre_norm not in self.__indice_nombres:
            self.__indice_nombres[nombre_norm] = []
        if producto.id_producto not in self.__indice_nombres[nombre_norm]:
            self.__indice_nombres[nombre_norm].append(producto.id_producto)

    def _remover_de_indice_nombres(self, producto: Producto):
        """Remueve producto del índice de nombres"""
        nombre_norm = self._normalizar_nombre(producto.nombre)
        if nombre_norm in self.__indice_nombres:
            if producto.id_producto in self.__indice_nombres[nombre_norm]:
                self.__indice_nombres[nombre_norm].remove(producto.id_producto)
            if not self.__indice_nombres[nombre_norm]:
                del self.__indice_nombres[nombre_norm]

    def agregar_producto(self, producto: Producto) -> bool:
        """
        Añade un nuevo producto al inventario.

        Args:
            producto (Producto): Producto a añadir

        Returns:
            bool: True si se añadió exitosamente, False si ya existe
        """
        if producto.id_producto in self.__ids_productos:
            print(f"Error: Ya existe un producto con ID '{producto.id_producto}'")
            return False

        # Agregar a todas las colecciones
        self.__productos[producto.id_producto] = producto
        self.__ids_productos.add(producto.id_producto)
        self._actualizar_indice_nombres(producto)

        print(f"Producto '{producto.nombre}' agregado exitosamente")
        return True

    def eliminar_producto(self, id_producto: str) -> bool:
        """
        Elimina un producto del inventario por ID.

        Args:
            id_producto (str): ID del producto a eliminar

        Returns:
            bool: True si se eliminó exitosamente, False si no existe
        """
        id_producto = id_producto.upper().strip()

        if id_producto not in self.__ids_productos:
            print(f"Error: No existe un producto con ID '{id_producto}'")
            return False

        # Obtener producto antes de eliminar
        producto = self.__productos[id_producto]

        # Eliminar de todas las colecciones
        del self.__productos[id_producto]
        self.__ids_productos.remove(id_producto)
        self._remover_de_indice_nombres(producto)

        print(f"Producto '{producto.nombre}' eliminado exitosamente")
        return True

    def actualizar_cantidad(self, id_producto: str, nueva_cantidad: int) -> bool:
        """
        Actualiza la cantidad de un producto.

        Args:
            id_producto (str): ID del producto
            nueva_cantidad (int): Nueva cantidad

        Returns:
            bool: True si se actualizó exitosamente
        """
        id_producto = id_producto.upper().strip()

        if id_producto not in self.__productos:
            print(f"Error: No existe un producto con ID '{id_producto}'")
            return False

        try:
            cantidad_anterior = self.__productos[id_producto].cantidad
            self.__productos[id_producto].cantidad = nueva_cantidad
            print(f"Cantidad actualizada: {cantidad_anterior} → {nueva_cantidad}")
            return True
        except ValueError as e:
            print(f"Error al actualizar cantidad: {e}")
            return False

    def actualizar_precio(self, id_producto: str, nuevo_precio: float) -> bool:
        """
        Actualiza el precio de un producto.

        Args:
            id_producto (str): ID del producto
            nuevo_precio (float): Nuevo precio

        Returns:
            bool: True si se actualizó exitosamente
        """
        id_producto = id_producto.upper().strip()

        if id_producto not in self.__productos:
            print(f"Error: No existe un producto con ID '{id_producto}'")
            return False

        try:
            precio_anterior = self.__productos[id_producto].precio
            self.__productos[id_producto].precio = nuevo_precio
            print(f"Precio actualizado: ${precio_anterior:.2f} → ${nuevo_precio:.2f}")
            return True
        except ValueError as e:
            print(f"Error al actualizar precio: {e}")
            return False

    def buscar_por_nombre(self, nombre: str) -> List[Producto]:
        """
        Busca productos por nombre (búsqueda insensible a mayúsculas).

        Args:
            nombre (str): Nombre o parte del nombre a buscar

        Returns:
            List[Producto]: Lista de productos encontrados
        """
        nombre_busqueda = self._normalizar_nombre(nombre)
        productos_encontrados = []

        # Búsqueda exacta en el índice
        if nombre_busqueda in self.__indice_nombres:
            for id_producto in self.__indice_nombres[nombre_busqueda]:
                productos_encontrados.append(self.__productos[id_producto])

        # Búsqueda parcial si no se encontró coincidencia exacta
        if not productos_encontrados:
            for nombre_producto, ids in self.__indice_nombres.items():
                if nombre_busqueda in nombre_producto:
                    for id_producto in ids:
                        productos_encontrados.append(self.__productos[id_producto])

        return productos_encontrados

    def obtener_producto_por_id(self, id_producto: str) -> Optional[Producto]:
        """
        Obtiene un producto por su ID.

        Args:
            id_producto (str): ID del producto

        Returns:
            Optional[Producto]: Producto si existe, None si no existe
        """
        id_producto = id_producto.upper().strip()
        return self.__productos.get(id_producto)

    def mostrar_todos_productos(self) -> List[Producto]:
        """
        Obtiene todos los productos ordenados por ID.

        Returns:
            List[Producto]: Lista de todos los productos
        """
        return [self.__productos[id_prod] for id_prod in sorted(self.__productos.keys())]

    def obtener_productos_bajo_stock(self, limite_stock: int = 5) -> List[Producto]:
        """
        Obtiene productos con stock bajo.

        Args:
            limite_stock (int): Límite de stock considerado bajo

        Returns:
            List[Producto]: Lista de productos con stock bajo
        """
        return [producto for producto in self.__productos.values()
                if producto.cantidad <= limite_stock]

    def obtener_estadisticas(self) -> Dict[str, any]:
        """
        Obtiene estadísticas del inventario.

        Returns:
            Dict: Estadísticas del inventario
        """
        if not self.__productos:
            return {
                'total_productos': 0,
                'valor_total_inventario': 0,
                'producto_mas_caro': None,
                'producto_mas_barato': None,
                'stock_total': 0
            }

        productos = list(self.__productos.values())

        return {
            'total_productos': len(productos),
            'valor_total_inventario': sum(p.calcular_valor_total() for p in productos),
            'producto_mas_caro': max(productos, key=lambda p: p.precio),
            'producto_mas_barato': min(productos, key=lambda p: p.precio),
            'stock_total': sum(p.cantidad for p in productos)
        }

    def guardar_inventario(self) -> bool:
        """
        Guarda el inventario en archivo JSON.

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Convertir productos a diccionarios para serialización
            data = {
                'productos': [producto.to_dict() for producto in self.__productos.values()],
                'fecha_guardado': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': '1.0'
            }

            # Crear directorio si no existe
            directorio = os.path.dirname(self.__archivo_inventario)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)

            # Guardar en archivo
            with open(self.__archivo_inventario, 'w', encoding='utf-8') as archivo:
                json.dump(data, archivo, indent=2, ensure_ascii=False)

            print(f"Inventario guardado exitosamente en '{self.__archivo_inventario}'")
            return True

        except Exception as e:
            print(f"Error al guardar inventario: {e}")
            return False

    def cargar_inventario(self) -> bool:
        """
        Carga el inventario desde archivo JSON.

        Returns:
            bool: True si se cargó exitosamente
        """
        if not os.path.exists(self.__archivo_inventario):
            print(f"Archivo de inventario '{self.__archivo_inventario}' no existe. Iniciando con inventario vacío.")
            return True

        try:
            with open(self.__archivo_inventario, 'r', encoding='utf-8') as archivo:
                data = json.load(archivo)

            # Limpiar colecciones existentes
            self.__productos.clear()
            self.__ids_productos.clear()
            self.__indice_nombres.clear()

            # Cargar productos
            productos_cargados = 0
            for producto_data in data.get('productos', []):
                try:
                    producto = Producto.from_dict(producto_data)
                    self.__productos[producto.id_producto] = producto
                    self.__ids_productos.add(producto.id_producto)
                    self._actualizar_indice_nombres(producto)
                    productos_cargados += 1
                except Exception as e:
                    print(f"Error al cargar producto {producto_data.get('id_producto', 'desconocido')}: {e}")

            print(f"Inventario cargado exitosamente: {productos_cargados} productos")
            return True

        except Exception as e:
            print(f"Error al cargar inventario: {e}")
            return False

    def __len__(self) -> int:
        """Retorna la cantidad de productos en el inventario"""
        return len(self.__productos)

    def __contains__(self, id_producto: str) -> bool:
        """Verifica si un producto existe en el inventario"""
        return id_producto.upper().strip() in self.__ids_productos


class InterfazUsuario:
    """
    Interfaz de usuario para interactuar con el sistema de inventario.
    Proporciona un menú interactivo en consola.
    """

    def __init__(self):
        self.inventario = Inventario()
        self.opciones_menu = {
            '1': self.agregar_producto,
            '2': self.eliminar_producto,
            '3': self.actualizar_producto,
            '4': self.buscar_producto,
            '5': self.mostrar_todos_productos,
            '6': self.mostrar_estadisticas,
            '7': self.productos_bajo_stock,
            '8': self.guardar_inventario,
            '9': self.cargar_inventario,
            '0': self.salir
        }

    def mostrar_menu(self):
        """Muestra el menú principal"""
        print("\n" + "=" * 60)
        print("    SISTEMA AVANZADO DE GESTIÓN DE INVENTARIO")
        print("=" * 60)
        print("1. Agregar producto")
        print("2. Eliminar producto")
        print("3. Actualizar producto")
        print("4. Buscar producto")
        print("5. Mostrar todos los productos")
        print("6. Mostrar estadísticas")
        print("7. Productos bajo stock")
        print("8. Guardar inventario")
        print("9. Cargar inventario")
        print("0. Salir")
        print("=" * 60)

    def obtener_opcion(self) -> str:
        """Obtiene la opción seleccionada por el usuario"""
        while True:
            opcion = input("Seleccione una opción: ").strip()
            if opcion in self.opciones_menu:
                return opcion
            print("Opción inválida. Por favor, seleccione una opción válida.")

    def agregar_producto(self):
        """Interfaz para agregar un nuevo producto"""
        print("\n--- AGREGAR PRODUCTO ---")
        try:
            id_producto = input("ID del producto: ").strip()
            if not id_producto:
                print("El ID no puede estar vacío")
                return

            nombre = input("Nombre del producto: ").strip()
            if not nombre:
                print("El nombre no puede estar vacío")
                return

            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: $"))

            producto = Producto(id_producto, nombre, cantidad, precio)
            self.inventario.agregar_producto(producto)

        except ValueError as e:
            print(f"Error en los datos ingresados: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def eliminar_producto(self):
        """Interfaz para eliminar un producto"""
        print("\n--- ELIMINAR PRODUCTO ---")
        id_producto = input("ID del producto a eliminar: ").strip()
        if id_producto:
            # Mostrar información del producto antes de eliminar
            producto = self.inventario.obtener_producto_por_id(id_producto)
            if producto:
                print(f"Producto encontrado: {producto}")
                confirmacion = input("¿Está seguro de eliminar este producto? (s/N): ").strip().lower()
                if confirmacion == 's':
                    self.inventario.eliminar_producto(id_producto)
                else:
                    print("Eliminación cancelada")
            else:
                print(f"No se encontró un producto con ID '{id_producto}'")
        else:
            print("ID no puede estar vacío")

    def actualizar_producto(self):
        """Interfaz para actualizar un producto"""
        print("\n--- ACTUALIZAR PRODUCTO ---")
        id_producto = input("ID del producto a actualizar: ").strip()

        if not id_producto:
            print("ID no puede estar vacío")
            return

        producto = self.inventario.obtener_producto_por_id(id_producto)
        if not producto:
            print(f"No se encontró un producto con ID '{id_producto}'")
            return

        print(f"Producto actual: {producto}")
        print("\n¿Qué desea actualizar?")
        print("1. Cantidad")
        print("2. Precio")
        print("3. Ambos")

        opcion = input("Seleccione una opción (1-3): ").strip()

        try:
            if opcion in ['1', '3']:
                nueva_cantidad = int(input(f"Nueva cantidad (actual: {producto.cantidad}): "))
                self.inventario.actualizar_cantidad(id_producto, nueva_cantidad)

            if opcion in ['2', '3']:
                nuevo_precio = float(input(f"Nuevo precio (actual: ${producto.precio:.2f}): $"))
                self.inventario.actualizar_precio(id_producto, nuevo_precio)

            if opcion not in ['1', '2', '3']:
                print("Opción inválida")

        except ValueError as e:
            print(f"Error en los datos ingresados: {e}")

    def buscar_producto(self):
        """Interfaz para buscar productos"""
        print("\n--- BUSCAR PRODUCTO ---")
        print("1. Buscar por ID")
        print("2. Buscar por nombre")

        opcion = input("Seleccione tipo de búsqueda (1-2): ").strip()

        if opcion == '1':
            id_producto = input("ID del producto: ").strip()
            if id_producto:
                producto = self.inventario.obtener_producto_por_id(id_producto)
                if producto:
                    print(f"\nProducto encontrado:")
                    print(producto)
                    print(f"Valor total: ${producto.calcular_valor_total():.2f}")
                    print(f"Fecha de creación: {producto.fecha_creacion}")
                else:
                    print("Producto no encontrado")
            else:
                print("ID no puede estar vacío")

        elif opcion == '2':
            nombre = input("Nombre del producto (o parte del nombre): ").strip()
            if nombre:
                productos = self.inventario.buscar_por_nombre(nombre)
                if productos:
                    print(f"\nSe encontraron {len(productos)} producto(s):")
                    for i, producto in enumerate(productos, 1):
                        print(f"{i}. {producto}")
                else:
                    print("No se encontraron productos con ese nombre")
            else:
                print("Nombre no puede estar vacío")
        else:
            print("Opción inválida")

    def mostrar_todos_productos(self):
        """Interfaz para mostrar todos los productos"""
        print("\n--- TODOS LOS PRODUCTOS ---")
        productos = self.inventario.mostrar_todos_productos()

        if productos:
            print(f"Total de productos: {len(productos)}")
            print("-" * 80)
            for i, producto in enumerate(productos, 1):
                print(f"{i:2d}. {producto}")
                print(f"     Valor total: ${producto.calcular_valor_total():.2f}")
        else:
            print("No hay productos en el inventario")

    def mostrar_estadisticas(self):
        """Interfaz para mostrar estadísticas del inventario"""
        print("\n--- ESTADÍSTICAS DEL INVENTARIO ---")
        stats = self.inventario.obtener_estadisticas()

        print(f"Total de productos únicos: {stats['total_productos']}")
        print(f"Stock total: {stats['stock_total']} unidades")
        print(f"Valor total del inventario: ${stats['valor_total_inventario']:.2f}")

        if stats['producto_mas_caro']:
            print(f"Producto más caro: {stats['producto_mas_caro'].nombre} (${stats['producto_mas_caro'].precio:.2f})")

        if stats['producto_mas_barato']:
            print(
                f"Producto más barato: {stats['producto_mas_barato'].nombre} (${stats['producto_mas_barato'].precio:.2f})")

    def productos_bajo_stock(self):
        """Interfaz para mostrar productos con stock bajo"""
        print("\n--- PRODUCTOS BAJO STOCK ---")
        try:
            limite = int(input("Ingrese el límite de stock (por defecto 5): ") or "5")
            productos = self.inventario.obtener_productos_bajo_stock(limite)

            if productos:
                print(f"\nProductos con stock ≤ {limite}:")
                for i, producto in enumerate(productos, 1):
                    print(f"{i}. {producto}")
            else:
                print(f"No hay productos con stock bajo (≤ {limite})")

        except ValueError:
            print("Límite inválido, usando valor por defecto (5)")
            productos = self.inventario.obtener_productos_bajo_stock()
            if productos:
                print(f"\nProductos con stock ≤ 5:")
                for i, producto in enumerate(productos, 1):
                    print(f"{i}. {producto}")
            else:
                print("No hay productos con stock bajo")

    def guardar_inventario(self):
        """Interfaz para guardar el inventario"""
        print("\n--- GUARDAR INVENTARIO ---")
        if self.inventario.guardar_inventario():
            print("El inventario se ha guardado correctamente")
        else:
            print("Error al guardar el inventario")

    def cargar_inventario(self):
        """Interfaz para cargar el inventario"""
        print("\n--- CARGAR INVENTARIO ---")
        print("ADVERTENCIA: Esto sobrescribirá el inventario actual")
        confirmacion = input("¿Está seguro? (s/N): ").strip().lower()

        if confirmacion == 's':
            if self.inventario.cargar_inventario():
                print("El inventario se ha cargado correctamente")
            else:
                print("Error al cargar el inventario")
        else:
            print("Carga cancelada")

    def salir(self):
        """Interfaz para salir del programa"""
        print("\n--- SALIR ---")
        print("¿Desea guardar el inventario antes de salir?")
        respuesta = input("(s/N): ").strip().lower()

        if respuesta == 's':
            self.inventario.guardar_inventario()

        print("¡Gracias por usar el Sistema de Gestión de Inventario!")
        return True

    def ejecutar(self):
        """Ejecuta el programa principal"""
        print("¡Bienvenido al Sistema Avanzado de Gestión de Inventario!")

        # Cargar inventario al inicio
        print("Cargando inventario...")
        self.inventario.cargar_inventario()

        while True:
            try:
                self.mostrar_menu()
                opcion = self.obtener_opcion()

                if opcion == '0':
                    if self.salir():
                        break
                else:
                    self.opciones_menu[opcion]()

                input("\nPresione Enter para continuar...")

            except KeyboardInterrupt:
                print("\n\nPrograma interrumpido por el usuario")
                if self.salir():
                    break
            except Exception as e:
                print(f"Error inesperado: {e}")
                input("Presione Enter para continuar...")


# Función principal para demostrar el uso del sistema
def main():
    """
    Función principal que demuestra el uso del sistema de inventario.
    Incluye datos de prueba para mostrar todas las funcionalidades.
    """
    print("Iniciando Sistema de Gestión de Inventario...")

    # Crear datos de prueba si el inventario está vacío
    def crear_datos_prueba(inventario: Inventario):
        productos_prueba = [
            Producto("LAPTOP001", "Laptop Dell XPS 13", 10, 1299.99),
            Producto("MOUSE001", "Mouse Logitech MX Master 3", 25, 99.99),
            Producto("TECLADO001", "Teclado Mecánico Corsair", 15, 149.99),
            Producto("MONITOR001", "Monitor Samsung 24''", 8, 299.99),
            Producto("CABLE001", "Cable USB-C", 50, 19.99),
        ]

        for producto in productos_prueba:
            inventario.agregar_producto(producto)

        print("Se han creado productos de prueba")

    # Inicializar interfaz
    interfaz = InterfazUsuario()

    # Si el inventario está vacío, ofrecer crear datos de prueba
    if len(interfaz.inventario) == 0:
        respuesta = input("¿Desea crear productos de prueba? (s/N): ").strip().lower()
        if respuesta == 's':
            crear_datos_prueba(interfaz.inventario)

    # Ejecutar la interfaz principal
    interfaz.ejecutar()


if __name__ == "__main__":
    main()