from api_client import APIClient

# Probar con 10 registros primero
api = APIClient()
datos = api.consultar(limite=10)

if datos:
    print(f"✅ Funciona! {len(datos)} registros obtenidos")
    print("\n📄 Primer registro:")
    import json
    print(json.dumps(datos[0], indent=2, ensure_ascii=False))
    
    print("\n📋 Campos disponibles:")
    print(list(datos[0].keys()))
else:
    print("❌ Error")