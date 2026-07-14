import asyncio
import logging
import random
import math
from asyncua import Server

# Configurar logs para ver qué pasa en la consola del clúster
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PLC_Virtual")

async def main():
    # 1. Inicializar el Servidor OPC-UA
    server = Server()
    await server.init()
    
    # Configurar el puerto y el endpoint
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("PLC Virtual - Nivel 1")

    # 🔑 PASO CLAVE: Iniciamos el servidor primero para que existan los nodos base
    logger.info("⚡ Iniciando Servidor OPC-UA en opc.tcp://0.0.0.0:4840 ...")
    await server.start()
    logger.info("🚀 Servidor OPC-UA corriendo exitosamente.")

    # 2. Registrar el Namespace
    uri = "http://lab.industrial.scada/plc"
    idx = await server.register_namespace(uri)

    # 3. Crear la estructura de objetos en el PLC
    objects_node = server.get_objects_node()
    banda_objeto = await objects_node.add_object(idx, "Banda_Transportadora")

    # 4. Añadir las 3 variables (Tags OPC) al objeto
    tag_temp = await banda_objeto.add_variable(idx, "Temperatura", 0.0)
    tag_piezas = await banda_objeto.add_variable(idx, "Contador_Piezas", 0)
    tag_estado = await banda_objeto.add_variable(idx, "Estado_Banda", False)

    # 🔑 CORRECCIÓN: Usamos set_writable() en lugar de make_writable()
    await tag_temp.set_writable()
    await tag_piezas.set_writable()
    await tag_estado.set_writable()

    # 5. Bucle de simulación en vivo
    contador = 0
    tiempo = 0.0

    try:
        while True:
            # --- Simulación de Variables ---
            ruido = random.uniform(-0.5, 0.5)
            temperatura = round(60.0 + (15.0 * math.sin(tiempo)) + ruido, 2)
            
            estado_banda = True if random.random() > 0.05 else False
            
            if estado_banda:
                if random.random() > 0.6:
                    contador += 1

            # --- Actualizar los Tags en el Servidor OPC-UA ---
            await tag_temp.write_value(temperatura)
            await tag_piezas.write_value(contador)
            await tag_estado.write_value(estado_banda)

            # Imprimir logs que DevSpace reflejará en tu terminal
            logger.info(f"📊 [DATA] Temp: {temperatura}°C | Piezas: {contador} | Banda: {estado_banda}")

            tiempo += 0.1
            await asyncio.sleep(1.0)

    except asyncio.CancelledError:
        logger.info("Stopping PLC simulation...")
    finally:
        await server.stop()
        logger.info("🔌 Servidor OPC-UA detenido.")

if __name__ == "__main__":
    asyncio.run(main())