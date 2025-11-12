# Plan de Corrección Detallado - Workflow Frepi

## 🔴 CORRECCIÓN CRÍTICA #1: Modelo de IA Inválido

### Nodos afectados (8 nodos):

```json
// ANTES (INCORRECTO):
{
  "model": {
    "__rl": true,
    "mode": "list",
    "value": "gpt-4.1-mini"  // ❌ NO EXISTE
  }
}

// DESPUÉS (CORRECTO):
{
  "model": {
    "__rl": true,
    "mode": "list",
    "value": "gpt-4o-mini"  // ✅ CORRECTO
  }
}
```

### Lista de nodos a modificar:
1. **OpenAI Chat Model** (id: 4adc9ebe-064b-4b1a-8a36-80b26da17ea7) - Onboarding
2. **OpenAI Chat Model1** (id: c29a2467-80c0-466f-9837-80dd9a9f06ab) - Compras
3. **OpenAI Chat Model2** (id: 9073d24f-c7b7-4a4d-b92c-c7e7bce97d1f) - Setup
4. **OpenAI Chat Model3** (id: fd224baf-29f0-4901-9fc7-6a8dc8b3559b) - Extraer JSON
5. **OpenAI Chat Model4** (id: 6ab5a26d-fa12-44ce-b060-0230d2b2db8b) - Menú Principal
6. **OpenAI Chat Model5** (id: 6dedce5e-7224-442e-9bae-0c93ba93214d) - Subir Precios
7. **OpenAI Config Produtos** (id: ce38177c-00b1-4208-b806-28630e89fea3)
8. **OpenAI Register Fornecedor** (id: bcf8cf3a-5566-4a3b-871a-07a46ae647a5)

---

## 🔧 CORRECCIÓN #2: Bug en "Extraer ID Restaurante"

### Ubicación:
Nodo "Extraer ID Restaurante" (id: ce304298-e0d5-4255-ae9a-30f1cdf1ce15)

### Código actual (PROBLEMÁTICO):
```javascript
const restaurants = $input.all().map(item => item.json);
restaurants.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
const latestRestaurant = restaurants[0];  // ❌ Puede ser undefined
```

### Código corregido:
```javascript
const restaurants = $input.all().map(item => item.json);

if (!restaurants || restaurants.length === 0) {
  console.error('[Extraer ID Restaurante] No se encontró ningún restaurante');
  return [{
    json: {
      error: true,
      error_message: 'No se encontró el restaurante recién creado',
      error_node: 'Extraer ID Restaurante',
      phone_number: $('Extraer Datos WhatsApp').first().json.phone_number,
      output: 'Erro ao criar restaurante. Tente novamente.'
    }
  }];
}

restaurants.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
const latestRestaurant = restaurants[0];  // ✅ Seguro ahora

const onboardingData = $('Detectar Onboarding Completo').first().json;

return [{
  json: {
    ...onboardingData,
    restaurant_id: latestRestaurant.id,
    restaurant_data: latestRestaurant
  }
}];
```

---

## 🔧 CORRECCIÓN #3: Verificación de Función RPC Supabase

### Ubicación:
Nodo "Vector Search Products" (id: 6af2043e-00ba-49d5-a047-989c3227ade0)

### SQL para verificar/crear la función en Supabase:

```sql
-- VERIFICAR SI EXISTE:
SELECT routine_name
FROM information_schema.routines
WHERE routine_name = 'match_products_v2'
  AND routine_schema = 'public';

-- SI NO EXISTE, CREAR:
CREATE OR REPLACE FUNCTION match_products_v2(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  product_name text,
  brand text,
  alternative_names text[],
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.id,
    m.product_name,
    m.brand,
    m.alternative_names,
    1 - (m.embedding <=> query_embedding) as similarity
  FROM master_list m
  WHERE 1 - (m.embedding <=> query_embedding) > match_threshold
  ORDER BY m.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### Código mejorado con validación:
```javascript
// En el nodo "Vector Search Products", agregar después de la línea 46:

let matchingProducts = [];
try {
  const { data, error } = await $supabase.rpc('match_products_v2', {
    query_embedding: queryEmbedding,
    match_threshold: 0.65,
    match_count: 5
  });

  if (error) {
    console.error('❌ [Vector Search] Supabase RPC error:', error.message);

    // ✅ AGREGAR: Verificar si es error de función no existente
    if (error.message.includes('function') && error.message.includes('does not exist')) {
      console.error('❌ [Vector Search] La función match_products_v2 no existe en Supabase');
      console.error('   Por favor, ejecuta el script SQL de creación de la función');
    }

    matchingProducts = [];
  } else {
    matchingProducts = data || [];
    console.log(`✅ [Vector Search] ${matchingProducts.length} productos encontrados`);
  }

} catch (error) {
  console.error('❌ [Vector Search] Error en búsqueda vectorial:', error);
  matchingProducts = [];
}
```

---

## 📋 CORRECCIÓN #4: Renombrar Nodos de Memoria

### Cambios recomendados:

| ID | Nombre Actual | Nombre Sugerido | SessionKey |
|----|---------------|-----------------|------------|
| e02e7596-01a8-435d-9883-3784f5f0afa7 | Simple Memory | Memory Onboarding | `{phone}_onboarding` |
| ae75b605-fb2f-4ff3-98e7-19abbfead8a1 | Simple Memory1 | Memory Compras | `{phone}` |
| 28ef3abe-e4c8-42c7-b645-230c74bdbc6a | Simple Memory2 | Memory Setup | `{phone}` |
| 2994f796-e33c-45a5-8ce0-4a566abacb89 | Simple Memory3 | Memory Preferencias | `{phone}` |
| 862cff7d-fb86-41d0-a9f4-0e910d011c61 | Simple Memory4 | Memory Menu | `{phone}_menu` |
| 43537cee-bc99-449a-af3f-d37bcb6880be | Simple Memory5 | Memory Precios | `{phone}_prices` |

⚠️ **IMPORTANTE:** Después de renombrar, actualizar TODAS las referencias en el workflow.

---

## 🎯 CORRECCIÓN #5: Simplificar Referencias a Nodos

### Nodos con nombres largos que se usan frecuentemente:

#### Opción A: Renombrar nodos
```
"Extraer Datos WhatsApp" → "Extract WA Data"
"Detectar Onboarding Completo" → "Detect Onboarding Done"
"Buscar Restaurante Recién Creado" → "Get New Restaurant"
"Preparar Datos Subir Precios" → "Prepare Price Data"
```

#### Opción B: Usar variables intermedias en Code nodes
```javascript
// ANTES:
const phone = $('Extraer Datos WhatsApp').first().json.phone_number;
const message = $('Extraer Datos WhatsApp').first().json.message;
const userName = $('Extraer Datos WhatsApp').first().json.user_name;

// DESPUÉS:
const waData = $('Extraer Datos WhatsApp').first().json;
const { phone_number: phone, message, user_name: userName } = waData;
```

---

## 🔄 CORRECCIÓN #6: Centralizar Validación de Errores

### Crear Function Node reutilizable:

```javascript
// Nuevo nodo: "Validate Input Function"
function validateInput(input, nodeName) {
  if (!input || !input.json) {
    console.error(`[${nodeName}] Input vacío o inválido`);
    return {
      valid: false,
      error: {
        error: true,
        error_message: 'Input inválido',
        error_node: nodeName,
        phone_number: 'unknown'
      }
    };
  }

  return {
    valid: true,
    data: input.json
  };
}

// Exportar para uso en otros nodos
return { validateInput };
```

### Usar en otros nodos:
```javascript
// En lugar de 60 líneas de try-catch...
const validation = $('Validate Input Function').validateInput($input.first(), 'Mi Nodo');
if (!validation.valid) {
  return [{ json: validation.error }];
}

const data = validation.data;
// ... continuar con lógica normal ...
```

---

## 📊 CORRECCIÓN #7: Prevenir Mensajes Duplicados

### Problema:
El nodo "Enviar Respuesta" recibe de 14+ fuentes diferentes.

### Solución: Agregar nodo "Merge Messages" antes de "Enviar Respuesta"

```
[Todos los nodos]
    ↓
[Merge Messages] (Tipo: Merge By Position, Output Data: All)
    ↓
[Deduplication Check] (Code node)
    ↓
[Enviar Respuesta]
```

### Código para "Deduplication Check":
```javascript
const items = $input.all();
const phoneNumber = items[0].json.phone_number;
const output = items[0].json.output;

// Verificar si ya se envió este mensaje recientemente (últimos 5 segundos)
const now = Date.now();
const cacheKey = `sent_${phoneNumber}_${output.substring(0, 50)}`;

// Usar variable de workflow o external storage
const lastSent = $workflow.getVariable(cacheKey) || 0;

if (now - lastSent < 5000) {
  console.log('⚠️ [Deduplication] Mensaje duplicado detectado, omitiendo');
  return [];
}

// Guardar timestamp
$workflow.setVariable(cacheKey, now);

return items;
```

---

## 🧪 CORRECCIÓN #8: Agregar Logging Estructurado

### Crear constante de logging en nodos críticos:

```javascript
// Al inicio de cada Code node importante:
const LOG = {
  prefix: '[Nombre del Nodo]',
  info: (msg, data) => console.log(`${LOG.prefix} ℹ️  ${msg}`, data ? JSON.stringify(data).substring(0, 200) : ''),
  success: (msg, data) => console.log(`${LOG.prefix} ✅ ${msg}`, data ? JSON.stringify(data).substring(0, 200) : ''),
  error: (msg, err) => console.error(`${LOG.prefix} ❌ ${msg}`, err || ''),
  warn: (msg) => console.warn(`${LOG.prefix} ⚠️  ${msg}`)
};

// Usar en lugar de console.log directo:
LOG.info('Procesando usuario', { phone, name });
LOG.success('Usuario encontrado');
LOG.error('Error en base de datos', error.message);
LOG.warn('Precio fuera de rango');
```

---

## 📚 PREREQUISITOS DOCUMENTADOS

### Funciones RPC de Supabase necesarias:
1. ✅ `match_products_v2(vector, float, int)` - Búsqueda vectorial de productos

### Estructura de Base de Datos necesaria:
```sql
-- Tablas requeridas:
- restaurants
- restaurant_people
- line_sessions
- suppliers
- master_list
- supplier_mapped_products
- pricing_history

-- Extensiones requeridas:
CREATE EXTENSION IF NOT EXISTS vector;
```

### Credenciales necesarias:
1. ✅ WhatsApp Business API credentials ("Frepi bot")
2. ✅ Supabase API credentials ("Frepi Supabase")
3. ✅ OpenAI API credentials ("OpenAi account")
4. ✅ WhatsApp API credentials ("Frepi Account")

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Fase 1: CRÍTICO (Hoy) - 30 min
- [ ] Cambiar todos los modelos de `gpt-4.1-mini` a `gpt-4o-mini`
- [ ] Verificar función RPC `match_products_v2` en Supabase
- [ ] Agregar validación en "Extraer ID Restaurante"
- [ ] Probar flujo básico de onboarding

### Fase 2: IMPORTANTE (Esta semana) - 3 horas
- [ ] Renombrar nodos "Simple Memory*"
- [ ] Acortar nombres de nodos frecuentes
- [ ] Agregar logging estructurado
- [ ] Implementar deduplicación de mensajes
- [ ] Actualizar todas las referencias

### Fase 3: MEJORAS (Próxima semana) - 8 horas
- [ ] Centralizar validación de errores
- [ ] Unificar idioma (código en inglés, UI en portugués)
- [ ] Documentar prerequisitos y setup
- [ ] Crear tests para flujos principales
- [ ] Optimizar lógica de sesiones

### Fase 4: OPCIONAL (Futuro)
- [ ] Migrar a arquitectura más modular
- [ ] Implementar sistema de plugins
- [ ] Agregar dashboard de monitoring
- [ ] Implementar rollback automático

---

## ✅ CHECKLIST DE VERIFICACIÓN POST-CORRECCIÓN

```
[ ] Workflow se activa correctamente con mensaje de WhatsApp
[ ] Nuevo usuario puede completar onboarding
[ ] Usuario existente puede hacer una compra
[ ] Sistema de precios funciona correctamente
[ ] No hay mensajes duplicados
[ ] Logs son claros y estructurados
[ ] Errores se manejan gracefully
[ ] Sesiones se limpian correctamente
[ ] Timeouts funcionan como esperado
[ ] No hay memory leaks en sesiones
```

---

## 📞 SOPORTE

Si encuentras problemas adicionales:
1. Revisar logs de n8n en: Executions → Ver detalles de ejecución fallida
2. Verificar Supabase logs en: Dashboard → Logs
3. Revisar uso de API de OpenAI en: platform.openai.com/usage
4. Consultar documentación de n8n: docs.n8n.io
