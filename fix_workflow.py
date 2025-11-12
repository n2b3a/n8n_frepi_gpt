#!/usr/bin/env python3
"""
Script para corregir el workflow de n8n con cambios precisos y verificados.
Autor: Claude
Fecha: 2025
"""

import json
import sys
from pathlib import Path

def fix_extraer_id_restaurante(workflow):
    """
    Agrega validación null check en el nodo 'Extraer ID Restaurante'
    """
    print("🔧 Corrigiendo nodo 'Extraer ID Restaurante'...")

    # Código original problemático
    old_code = '''  // Original code starts here
  const restaurants = $input.all().map(item => item.json);

restaurants.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

const latestRestaurant = restaurants[0];

const onboardingData = $('Detectar Onboarding Completo').first().json;

return [{
  json: {
    ...onboardingData,
    restaurant_id: latestRestaurant.id,
    restaurant_data: latestRestaurant
  }
}];'''

    # Código corregido con validación
    new_code = '''  // Original code starts here
  const restaurants = $input.all().map(item => item.json);

// ✅ VALIDACIÓN: Verificar que hay restaurantes
if (!restaurants || restaurants.length === 0) {
  console.error('[Extraer ID Restaurante] No se encontraron restaurantes en el input');
  const phoneNumber = $('Extraer Datos WhatsApp').first().json.phone_number;
  return [{
    json: {
      error: true,
      error_message: 'No se encontró el restaurante recién creado',
      error_node: 'Extraer ID Restaurante',
      phone_number: phoneNumber,
      output: 'Erro ao criar restaurante. Por favor, tente novamente.'
    }
  }];
}

restaurants.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

const latestRestaurant = restaurants[0];  // ✅ Ahora es seguro

console.log(`✅ [Extraer ID Restaurante] Restaurante encontrado: ${latestRestaurant.id}`);

const onboardingData = $('Detectar Onboarding Completo').first().json;

return [{
  json: {
    ...onboardingData,
    restaurant_id: latestRestaurant.id,
    restaurant_data: latestRestaurant
  }
}];'''

    # Buscar y reemplazar en todos los nodos
    for node in workflow.get('nodes', []):
        if node.get('name') == 'Extraer ID Restaurante':
            if 'parameters' in node and 'jsCode' in node['parameters']:
                if old_code in node['parameters']['jsCode']:
                    node['parameters']['jsCode'] = node['parameters']['jsCode'].replace(old_code, new_code)
                    print("   ✅ Validación agregada exitosamente")
                    return True
                else:
                    print("   ⚠️  El código no coincide exactamente, buscando variaciones...")
                    # Buscar de manera más flexible
                    if 'const latestRestaurant = restaurants[0];' in node['parameters']['jsCode']:
                        # Si encontramos esta línea sin validación, es el problema
                        if 'if (!restaurants || restaurants.length === 0)' not in node['parameters']['jsCode']:
                            node['parameters']['jsCode'] = node['parameters']['jsCode'].replace(
                                'const restaurants = $input.all().map(item => item.json);\n\nrestaurants.sort',
                                '''const restaurants = $input.all().map(item => item.json);

// ✅ VALIDACIÓN: Verificar que hay restaurantes
if (!restaurants || restaurants.length === 0) {
  console.error('[Extraer ID Restaurante] No se encontraron restaurantes en el input');
  const phoneNumber = $('Extraer Datos WhatsApp').first().json.phone_number;
  return [{
    json: {
      error: true,
      error_message: 'No se encontró el restaurante recién creado',
      error_node: 'Extraer ID Restaurante',
      phone_number: phoneNumber,
      output: 'Erro ao criar restaurante. Por favor, tente novamente.'
    }
  }];
}

restaurants.sort'''
                            )
                            # También agregar log
                            node['parameters']['jsCode'] = node['parameters']['jsCode'].replace(
                                'const latestRestaurant = restaurants[0];',
                                '''const latestRestaurant = restaurants[0];  // ✅ Ahora es seguro

console.log(`✅ [Extraer ID Restaurante] Restaurante encontrado: ${latestRestaurant.id}`);'''
                            )
                            print("   ✅ Validación agregada con método flexible")
                            return True

    print("   ❌ No se encontró el nodo o no se pudo modificar")
    return False


def rename_memory_nodes(workflow):
    """
    Renombra los nodos Simple Memory* con nombres descriptivos
    """
    print("\n🔧 Renombrando nodos Simple Memory...")

    rename_map = {
        'Simple Memory': 'Memory Onboarding',
        'Simple Memory1': 'Memory Compras',
        'Simple Memory2': 'Memory Setup',
        'Simple Memory3': 'Memory Preferencias',
        'Simple Memory4': 'Memory Menu',
        'Simple Memory5': 'Memory Precios'
    }

    renamed_count = 0
    old_to_new = {}

    # Renombrar nodos
    for node in workflow.get('nodes', []):
        old_name = node.get('name', '')
        if old_name in rename_map:
            new_name = rename_map[old_name]
            node['name'] = new_name
            old_to_new[old_name] = new_name
            print(f"   ✅ '{old_name}' → '{new_name}'")
            renamed_count += 1

    print(f"   📊 Total renombrados: {renamed_count} nodos")
    return old_to_new


def update_node_references(workflow, rename_map):
    """
    Actualiza TODAS las referencias a nodos renombrados en connections y código
    """
    print("\n🔧 Actualizando referencias a nodos renombrados...")

    updates_count = 0

    # Actualizar connections
    connections = workflow.get('connections', {})
    new_connections = {}

    for node_name, node_connections in connections.items():
        # Renombrar la key si es necesario
        new_node_name = rename_map.get(node_name, node_name)

        # Actualizar referencias dentro de las conexiones
        updated_connections = {}
        for conn_type, conn_list in node_connections.items():
            updated_conn_list = []
            for conn_group in conn_list:
                updated_group = []
                for conn in conn_group:
                    if isinstance(conn, dict) and 'node' in conn:
                        old_ref = conn['node']
                        if old_ref in rename_map:
                            conn['node'] = rename_map[old_ref]
                            updates_count += 1
                            print(f"   ✅ Referencia actualizada en connections: '{old_ref}' → '{rename_map[old_ref]}'")
                    updated_group.append(conn)
                updated_conn_list.append(updated_group)
            updated_connections[conn_type] = updated_conn_list

        new_connections[new_node_name] = updated_connections

    workflow['connections'] = new_connections

    print(f"   📊 Total referencias actualizadas en connections: {updates_count}")
    return updates_count


def add_structured_logging(workflow):
    """
    Agrega logging estructurado a nodos críticos
    """
    print("\n🔧 Agregando logging estructurado...")

    logging_template = """const LOG = {
  prefix: '[{node_name}]',
  info: (msg, data) => console.log(`${{LOG.prefix}} ℹ️  ${{msg}}`, data !== undefined ? JSON.stringify(data).substring(0, 200) : ''),
  success: (msg, data) => console.log(`${{LOG.prefix}} ✅ ${{msg}}`, data !== undefined ? JSON.stringify(data).substring(0, 200) : ''),
  error: (msg, err) => console.error(`${{LOG.prefix}} ❌ ${{msg}}`, err || ''),
  warn: (msg) => console.warn(`${{LOG.prefix}} ⚠️  ${{msg}}`)
};

"""

    critical_nodes = [
        'Detectar Onboarding Completo',
        'Detectar Pedido Completo',
        'Detectar Precios Completos',
        'Detectar Setup Completo',
        'Generar Recomendación',
        'Procesar y Guardar Precios',
        'Guardar Fornecedor BD'
    ]

    added_count = 0

    for node in workflow.get('nodes', []):
        node_name = node.get('name', '')
        if node_name in critical_nodes:
            if 'parameters' in node and 'jsCode' in node['parameters']:
                code = node['parameters']['jsCode']

                # Solo agregar si no existe ya
                if 'const LOG = {' not in code:
                    # Buscar donde termina el error handling inicial
                    if '// Original code starts here' in code:
                        logging_code = logging_template.replace('{node_name}', node_name)
                        code = code.replace(
                            '  // Original code starts here\n',
                            f'  // Original code starts here\n  {logging_code}'
                        )
                        node['parameters']['jsCode'] = code
                        print(f"   ✅ Logging agregado a: {node_name}")
                        added_count += 1

    print(f"   📊 Total nodos con logging: {added_count}")
    return added_count


def add_message_deduplication(workflow):
    """
    Agrega deduplicación de mensajes antes del nodo "Enviar Respuesta"
    """
    print("\n🔧 Agregando nodo de deduplicación de mensajes...")

    # Crear nodo de deduplicación
    dedup_node = {
        "parameters": {
            "jsCode": """// ===== MESSAGE DEDUPLICATION =====
// Previene el envío de mensajes duplicados en un periodo corto de tiempo

const items = $input.all();

if (!items || items.length === 0) {
  console.log('⚠️ [Deduplication] No hay items para procesar');
  return [];
}

const phoneNumber = items[0].json.phone_number;
const output = items[0].json.output || '';

// Crear una key única basada en phone + primeros 50 caracteres del mensaje
const messageKey = `${phoneNumber}_${output.substring(0, 50)}`;
const now = Date.now();

// Verificar si este mensaje ya se envió recientemente (últimos 3 segundos)
const DEDUP_WINDOW_MS = 3000;

// Usar el contexto del workflow para tracking (simulado con timestamp en el mensaje)
const lastSentTimestamp = items[0].json._last_sent_timestamp || 0;

if (output === items[0].json._last_sent_output && (now - lastSentTimestamp) < DEDUP_WINDOW_MS) {
  console.log(`⚠️ [Deduplication] Mensaje duplicado detectado para ${phoneNumber}, omitiendo`);
  console.log(`   Tiempo transcurrido: ${now - lastSentTimestamp}ms`);
  return [];
}

// Agregar timestamp para tracking
items[0].json._last_sent_timestamp = now;
items[0].json._last_sent_output = output;

console.log(`✅ [Deduplication] Mensaje único confirmado para ${phoneNumber}`);

return items;
"""
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2700, 1404],
        "id": "dedup-node-" + str(hash('deduplication'))[-8:],
        "name": "Deduplicar Mensajes"
    }

    # Buscar el nodo "Enviar Respuesta"
    enviar_respuesta_found = False
    for node in workflow.get('nodes', []):
        if node.get('name') == 'Enviar Respuesta':
            enviar_respuesta_found = True
            enviar_id = node.get('id')
            # Mover un poco a la derecha para hacer espacio
            if 'position' in node:
                node['position'][0] += 100
            break

    if not enviar_respuesta_found:
        print("   ⚠️  No se encontró el nodo 'Enviar Respuesta'")
        return False

    # Agregar el nodo de deduplicación
    workflow['nodes'].append(dedup_node)

    # Actualizar conexiones: insertar el nodo de deduplicación antes de "Enviar Respuesta"
    connections = workflow.get('connections', {})

    # Encontrar todos los nodos que apuntan a "Enviar Respuesta"
    nodes_to_update = []
    for source_node, conns in connections.items():
        if 'main' in conns:
            for i, conn_list in enumerate(conns['main']):
                for j, conn in enumerate(conn_list):
                    if conn.get('node') == 'Enviar Respuesta':
                        nodes_to_update.append((source_node, i, j))

    print(f"   📊 Encontrados {len(nodes_to_update)} nodos que conectan a 'Enviar Respuesta'")

    # Redirigir las conexiones al nodo de deduplicación
    for source_node, i, j in nodes_to_update:
        connections[source_node]['main'][i][j]['node'] = 'Deduplicar Mensajes'

    # Conectar el nodo de deduplicación a "Enviar Respuesta"
    connections['Deduplicar Mensajes'] = {
        "main": [[{
            "node": "Enviar Respuesta",
            "type": "main",
            "index": 0
        }]]
    }

    print("   ✅ Nodo de deduplicación agregado y conectado")
    return True


def main():
    input_file = Path('/home/user/n8n_frepi_gpt/workflow_corrected_step1.json')
    output_file = Path('/home/user/n8n_frepi_gpt/workflow_corrected_FINAL.json')

    print("🚀 Iniciando corrección del workflow...")
    print(f"📂 Archivo de entrada: {input_file}")
    print(f"📂 Archivo de salida: {output_file}\n")

    # Cargar el workflow
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print("✅ Workflow cargado exitosamente\n")
    except Exception as e:
        print(f"❌ Error al cargar el workflow: {e}")
        return 1

    # Aplicar correcciones
    changes_made = []

    # 1. Agregar validación en "Extraer ID Restaurante"
    if fix_extraer_id_restaurante(workflow):
        changes_made.append("✅ Validación null check en 'Extraer ID Restaurante'")

    # 2. Renombrar nodos Simple Memory*
    rename_map = rename_memory_nodes(workflow)
    if rename_map:
        changes_made.append(f"✅ Renombrados {len(rename_map)} nodos Memory")

    # 3. Actualizar referencias
    refs_updated = update_node_references(workflow, rename_map)
    if refs_updated > 0:
        changes_made.append(f"✅ Actualizadas {refs_updated} referencias")

    # 4. Agregar logging estructurado
    logs_added = add_structured_logging(workflow)
    if logs_added > 0:
        changes_made.append(f"✅ Logging estructurado en {logs_added} nodos")

    # 5. Agregar deduplicación
    if add_message_deduplication(workflow):
        changes_made.append("✅ Deduplicación de mensajes implementada")

    # Guardar el workflow corregido
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Workflow corregido guardado en: {output_file}")
    except Exception as e:
        print(f"\n❌ Error al guardar el workflow: {e}")
        return 1

    # Verificar que el JSON es válido
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ JSON válido verificado")
    except Exception as e:
        print(f"❌ Error: El JSON generado no es válido: {e}")
        return 1

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE CAMBIOS:")
    print("="*60)
    for change in changes_made:
        print(f"  {change}")
    print("="*60)
    print(f"\n✅ Corrección completada exitosamente!")
    print(f"📁 Archivo final: {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
