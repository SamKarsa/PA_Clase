from apscheduler.schedulers.background import BackgroundScheduler
from api_client import APIClient
from database import DatabaseClient
from datetime import datetime
import time

# Configuración
INTERVALO_HORAS = 8 # Intervalo de sincronización en horas

def sincronizar_datos():
    print("\n" + "="*50)
    print(f"🔄 SINCRONIZACIÓN AUTOMÁTICA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    try:
        # 1. Obtener datos de la API
        print("📡 Paso 1/4: Obteniendo datos de la API...")
        api = APIClient()
        datos_api = api.consultar(limite=500000)
        
        if not datos_api:
            print("❌ Error: No se pudieron obtener datos de la API")
            return False
        
        print(f"✅ Paso 1/4: {len(datos_api):,} registros obtenidos")
        
        # 2. Conectar a MongoDB
        print("💾 Paso 2/4: Conectando a MongoDB...")
        db = DatabaseClient()
        
        if not db.conectar():
            print("❌ Error: No se pudo conectar a MongoDB")
            return False
        
        print("✅ Paso 2/4: Conectado a MongoDB")
        
        # 3. Limpiar colección
        print("🗑️ Paso 3/4: Limpiando datos antiguos...")
        eliminados = db.limpiar_coleccion()
        print(f"✅ Paso 3/4: {eliminados:,} registros eliminados")
        
        # 4. Insertar nuevos datos
        print(f"💾 Paso 4/4: Insertando {len(datos_api):,} registros...")
        insertados = db.insertar_datos(datos_api)
        
        if insertados > 0:
            print(f"✅ Paso 4/4: {insertados:,} registros insertados")
            print("\n🎉 SINCRONIZACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📊 Resumen: {eliminados:,} eliminados | {insertados:,} insertados")
        else:
            print("❌ Error al insertar datos")
            return False
        
        # Desconectar
        db.desconectar()
        
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ Error en la sincronización automática: {e}")
        return False
    
def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    
    # Programar la tarea
    scheduler.add_job(
        sincronizar_datos,
        'interval',
        hours=INTERVALO_HORAS,
        id='sync_job',
        name='Sincronización automática API → MongoDB',
        replace_existing=True
    )
    
    # Iniciar el scheduler
    scheduler.start()
    
    print("="*50)
    print("🚀 SCHEDULER INICIADO")
    print(f"⏰ Sincronización automática cada {INTERVALO_HORAS} horas")
    print(f"🕐 Próxima ejecución: en {INTERVALO_HORAS} horas")
    print("="*50 + "\n")
    
    return scheduler

def obtener_info_scheduler(scheduler):
    jobs = scheduler.get_jobs()
    
    if not jobs:
        return {
            'activo': False,
            'proxima_ejecucion': None,
            'intervalo_horas': INTERVALO_HORAS
        }
    
    job = jobs[0]
    
    return {
        'activo': True,
        'proxima_ejecucion': job.next_run_time,
        'intervalo_horas': INTERVALO_HORAS
    }