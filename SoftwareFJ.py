# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas
# Autor: Luis David Rodriguez Bayona - UNAD
from abc import ABC, abstractmethod
from datetime import datetime

# 1. EXCEPCIONES PERSONALIZADAS
class DatoInvalidoError(Exception):
    pass
class ServicioNoDisponibleError(Exception):
    pass
class ReservaFallidaError(Exception):
    pass

# 2. LOG
def registrar_log(mensaje):
    try:
        with open("logs.txt", "a", encoding="utf-8") as archivo:
            archivo.write(f"{datetime.now()} - {mensaje}\n")
    except Exception as e:
        print(f"No se pudo escribir en el log: {e}")
    finally:
        pass

# 3. CLASE ABSTRACTA
class Entidad(ABC):
    def __init__(self, id_entidad):
        self._id = id_entidad
    @abstractmethod
    def mostrar_info(self):
        pass

# 4. CLIENTE
class Cliente(Entidad):
    def __init__(self, id_cliente, nombre, correo, edad):
        super().__init__(id_cliente)
        if not nombre or len(nombre.strip()) < 3:
            raise DatoInvalidoError("El nombre debe tener minimo 3 caracteres")
        if "@" not in correo:
            raise DatoInvalidoError("El correo debe contener @")
        if edad < 18:
            raise DatoInvalidoError("El cliente debe ser mayor de 18 anos")
        self._nombre = nombre
        self._correo = correo
        self._edad = edad
    def mostrar_info(self):
        return f"Cliente [{self._id}] {self._nombre} - {self._correo} - Edad: {self._edad}"

# 5. SERVICIO ABSTRACTO
class Servicio(Entidad):
    def __init__(self, id_servicio, nombre, precio_base, disponible=True):
        super().__init__(id_servicio)
        if precio_base <= 0:
            raise DatoInvalidoError("El precio debe ser mayor a 0")
        self._nombre = nombre
        self._precio_base = precio_base
        self._disponible = disponible
    @abstractmethod
    def calcular_costo(self, duracion=1, descuento=0):
        pass
    def mostrar_info(self):
        return f"Servicio [{self._id}] {self._nombre} - ${self._precio_base} - Disponible: {self._disponible}"

# 3 SERVICIOS
class ReservaSala(Servicio):
    def calcular_costo(self, duracion=1, descuento=0):
        total = self._precio_base * duracion
        return total - (total * descuento / 100)

class ReservaEquipo(Servicio):
    def calcular_costo(self, duracion=1, descuento=0):
        total = (self._precio_base * duracion) * 1.19
        return total - (total * descuento / 100)

class Asesoria(Servicio):
    def calcular_costo(self, duracion=1, descuento=0):
        if duracion <= 0:
            raise DatoInvalidoError("La duracion debe ser mayor a 0")
        total = self._precio_base * duracion
        return total - (total * descuento / 100)

# 6. RESERVA
class Reserva(Entidad):
    def __init__(self, id_reserva, cliente, servicio, duracion):
        super().__init__(id_reserva)
        if not servicio._disponible:
            raise ServicioNoDisponibleError(f"Servicio {servicio._nombre} no disponible")
        if duracion <= 0:
            raise DatoInvalidoError("Duracion invalida para la reserva")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "Confirmada"
        self._costo = servicio.calcular_costo(duracion)
    def cancelar(self):
        try:
            self._estado = "Cancelada"
            registrar_log(f"Reserva {self._id} cancelada")
        except Exception as e:
            registrar_log(f"Error al cancelar reserva {self._id}: {e}")
            raise ReservaFallidaError("No se pudo cancelar la reserva")
    def mostrar_info(self):
        return f"Reserva [{self._id}] {self._cliente._nombre} -> {self._servicio._nombre} - {self._duracion}h - ${self._costo:.2f} - Estado: {self._estado}"

# 7. PROGRAMA PRINCIPAL - 10 OPERACIONES
def main():
    clientes = []
    servicios = []
    reservas = []
    print("=== SOFTWARE FJ - INICIO DEL SISTEMA ===")
    registrar_log("Inicio del sistema Software FJ")
    try:
        c1 = Cliente(1, "Luis Rodriguez", "luis@gmail.com", 25)
        c2 = Cliente(2, "Maria Lopez", "maria@gmail.com", 30)
        clientes.extend([c1, c2])
        print(f"1-2. OK: {c1.mostrar_info()} | {c2.mostrar_info()}")
        registrar_log("Clientes 1 y 2 registrados")
    except DatoInvalidoError as e:
        print(f"Error cliente valido: {e}")
    try:
        c_malo = Cliente(3, "Ju", "sinarroba", 15)
        clientes.append(c_malo)
    except DatoInvalidoError as e:
        print(f"3. ERROR CONTROLADO (esperado): {e}")
        registrar_log(f"Error controlado cliente invalido: {e}")
    finally:
        print("3. Finally: La validacion termino, el sistema sigue activo")
    try:
        s1 = ReservaSala(101, "Sala de Juntas", 50000)
        s2 = ReservaEquipo(102, "Alquiler Portatil", 30000)
        s3 = Asesoria(103, "Asesoria Tecnica", 80000)
        servicios.extend([s1, s2, s3])
        print(f"4-6. OK: {s1.mostrar_info()} | {s2.mostrar_info()} | {s3.mostrar_info()}")
        registrar_log("3 servicios creados")
    except DatoInvalidoError as e:
        print(f"Error servicio: {e}")
    try:
        r1 = Reserva(1001, c1, s1, 2)
        reservas.append(r1)
        print(f"7. OK: {r1.mostrar_info()}")
        registrar_log(f"Reserva {r1._id} exitosa")
    except (ServicioNoDisponibleError, DatoInvalidoError) as e:
        print(f"Error reserva 7: {e}")
    try:
        s2._disponible = False
        r2 = Reserva(1002, c2, s2, 1)
        reservas.append(r2)
    except ServicioNoDisponibleError as e:
        print(f"8. ERROR CONTROLADO (esperado): {e}")
        registrar_log(f"Error controlado servicio no disponible: {e}")
    try:
        print(f"9. Costo Sala sin descuento: ${s1.calcular_costo(2)}")
        print(f"9. Costo Sala con 10% descuento: ${s1.calcular_costo(2, 10)}")
        print(f"9. Costo Equipo con IVA: ${s2.calcular_costo(3)}")
        registrar_log("Metodos sobrecargados probados")
    except Exception as e:
        print(f"Error calculo: {e}")
    try:
        r1.cancelar()
        print(f"10. OK: {r1.mostrar_info()}")
    except ReservaFallidaError as e:
        print(f"Error cancelacion: {e}")
    finally:
        print("10. Finally: Proceso de cancelacion finalizado")
    print(f"\n=== RESUMEN FINAL ===")
    print(f"Clientes: {len(clientes)} | Servicios: {len(servicios)} | Reservas: {len(reservas)}")
    print("Revisa el archivo logs.txt")
    registrar_log("Fin del sistema - 10 operaciones completadas")

if __name__ == "__main__":
    main()