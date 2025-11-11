# 🔍 Análisis de GAPs y Plan de Mejoras - Frepi MVP1

**Fecha**: 2025-11-11
**Propósito**: Comparar estado actual vs visión deseada e implementar mejoras sin romper funcionalidad existente

---

## 📊 ANÁLISIS COMPARATIVO: ACTUAL vs DESEADO

### **1. MENÚ PRINCIPAL**

#### **ACTUAL:**
```
1️⃣ Fazer uma compra
2️⃣ Atualizar preços de fornecedor
3️⃣ Registrar/Atualizar fornecedor
4️⃣ Configurar preferências
```

#### **DESEADO:**
```
1️⃣ Atualizar preços
   ├─ 1.1 Ver status de preços
   └─ 1.2 Actualizar preços

2️⃣ Fazer uma compra
   └─ Flujo detallado con análisis y segmentación

3️⃣ Registrar fornecedor
   ├─ 3.1 Criar fornecedor
   ├─ 3.2 Atualizar fornecedor
   └─ 3.3 Ver fornecedores atuais

4️⃣ Configuração
   ├─ 4.1 Setup inicial
   ├─ 4.2 Cambiar preferências
   │   ├─ master_list (9 campos por producto)
   │   ├─ dias_compra
   │   └─ Preferencia de compra por día
   └─ 4.3 Volver al menú principal
```

**GAP**:
- ❌ Menú actual es plano (sin submenús)
- ❌ Orden diferente (compra está primero, debería ser precios)
- ❌ Configuración muy simple vs muy compleja deseada

---

### **2. FLUJO DE HACER COMPRA**

#### **ACTUAL (línea 752 - Agente de Compras):**

**Prompt resumido**:
```
"Você é Frepi, especialista em compras.
Coleta: produtos, quantidades, unidades
Output: PEDIDO_COMPLETO + JSON"
```

**Procesamiento**:
1. Agente recoge lista
2. Vector search de productos
3. Buscar precios de todos proveedores
4. Generar recomendación simple

**Output actual**:
```
✅ Tomate
📦 5 kg
🏪 Fornecedor DEF
💰 R$ 4.80/kg = R$ 24.00

Outras opções:
   • Fornecedor ABC: R$ 5.00 (+4%)
```

#### **DESEADO:**

**Fases**:
1. **Confirmación inmediata** → "✅ Lista recibida, analisando..."
2. **Análisis de mejores precios** → Mostrar ahorros por producto
3. **Lista segmentada por proveedor** → Agrupar productos por proveedor
4. **Resumen total** → Total, ahorro, opciones de confirmar/modificar

**Output deseado**:
```
📊 ANÁLISIS DE MEJORES PRECIOS

🏆 Mayor ahorro:
- Arroz (2kg): Proveedor B - $4.50/kg vs $5.20 promedio
  Ahorro: $1.40 (27%)

💰 Ahorro total estimado: $12.50 (18%)

---

🛍️ TU LISTA OPTIMIZADA

📍 PROVEEDOR A - Supermercado El Ahorro
Total estimado: $42.30

- Aceite 1L - $8.90
- Pasta 500g - $2.40

Tiempo de entrega: 24-48hrs
Mínimo de compra: Cumplido ✅

---

📍 PROVEEDOR B - Distribuidora La Económica
Total estimado: $38.70

- Arroz 2kg - $9.00
- Frijoles 1kg - $4.80

Envío gratis >$30 🚚

---

💵 RESUMEN TOTAL
Subtotal: $109.50
Ahorro vs promedio: $12.50

¿Deseas proceder? [Confirmar] [Modificar] [Ver alternativas]
```

**GAP**:
- ❌ NO hay confirmación inmediata
- ❌ NO calcula promedio de mercado
- ❌ NO calcula % de ahorro
- ❌ NO segmenta por proveedor
- ❌ NO incluye info de entrega/mínimos
- ❌ NO tiene opciones de confirmar/modificar

---

### **3. FLUJO DE ACTUALIZAR PRECIOS**

#### **ACTUAL (línea 1371 - Agente Subir Precios):**

**Estructura**:
- Input: Lista de precios en texto
- Procesamiento: Parser con IA
- Output: "✅ Preços cadastrados"

**NO tiene**:
- ❌ Opción de "Ver status de precios"
- ❌ Información de cuántos precios están desactualizados

#### **DESEADO:**

**Submenú**:
```
📊 ATUALIZAR PREÇOS

1️⃣ Ver status de preços
   → Mostrar qué precios están desactualizados
   → Cuántos días sin actualizar por proveedor

2️⃣ Actualizar preços
   → Flujo actual (ya funciona)
```

**GAP**:
- ❌ Falta submenú
- ❌ Falta opción de ver status

---

### **4. FLUJO DE REGISTRAR FORNECEDOR**

#### **ACTUAL (línea 1802 - Agente Registrar Fornecedor):**

**Estructura**:
- Input: Nombre, teléfono, días, productos
- Output: "✅ Fornecedor cadastrado"

**NO tiene**:
- ❌ Opción de actualizar fornecedor existente
- ❌ Opción de ver fornecedores actuales

#### **DESEADO:**

**Submenú**:
```
🏪 REGISTRAR FORNECEDOR

1️⃣ Criar fornecedor novo
2️⃣ Atualizar fornecedor existente
3️⃣ Ver fornecedores atuais
```

**GAP**:
- ❌ Falta submenú
- ❌ Falta opción de actualizar
- ❌ Falta opción de listar

---

### **5. FLUJO DE CONFIGURACIÓN**

#### **ACTUAL (línea 945 - Agente de Setup):**

**Captura**:
1. Prioridad (precio/calidad/equilíbrio)
2. Productos frecuentes
3. Fornecedores preferidos
4. Frecuencia de pedidos
5. Orçamento mensal

**Guarda en `restaurants`**:
- `price_sensitivity` (0.2, 0.5, 0.8)
- `preferred_suppliers` (array)
- `category_preferences` (JSON)

#### **DESEADO:**

**Configuración DETALLADA por producto en `master_list`**:

```
PRODUCTO: Arroz
├─ 1. Precio (prioridad: bajo/medio/alto)
├─ 2. Marca (preferidas)
├─ 3. Qualidade (A+/A/B/tanto faz)
├─ 4. Especificações (1kg, grande, gris...)
├─ 5. Variação (nombres diferentes)
├─ 6. Quantidade por período (ej: 10kg/semana)
├─ 7. Frecuencia (diário, semanal, quinzenal)
├─ 8. Preferencia de fluxo de caixa
└─ 9. Agent autorizado a comprar? (sí/no)
```

**Otras configuraciones**:
- `dias_compra` → Qué días hace compras
- `preferencia_compra_por_dia` → Carnes lunes, vegetales miércoles, etc.

**GAP**:
- ❌ Configuración actual es GLOBAL, no por producto
- ❌ NO hay configuración de días específicos
- ❌ NO hay autorización de compra automática
- ❌ NO hay especificaciones detalladas por producto

---

## 🔧 PROBLEMAS TÉCNICOS IDENTIFICADOS

### **A. Dependencia de `master_list`**

**Problema CRÍTICO**:
```javascript
// Si producto NO está en master_list → master_list_id = NULL
// Entonces NO se puede buscar después
const { data: masterProduct } = await $supabase
  .from('master_list')
  .select('id')
  .ilike('product_name', `%${item.produto}%`)
  .limit(1)
  .single();

const masterListId = masterProduct?.id || null; // ❌ NULL = huérfano
```

**Impacto**:
- Usuario sube "Leite Especial XYZ"
- NO está en master_list → guarda con NULL
- Usuario hace compra "preciso de leite"
- Sistema busca en master_list → NO encuentra "Leite Especial XYZ"
- Recomendación NO incluye ese producto ❌

**Solución**:
```javascript
// AUTO-POPULATE: Si no existe, crearlo
if (!masterListId) {
  const embedding = await generateEmbedding(item.produto);
  const { data: newProduct } = await $supabase
    .from('master_list')
    .insert({
      product_name: item.produto,
      category: detectCategory(item.produto),
      embedding: embedding,
      is_active: true,
      created_at: new Date().toISOString()
    })
    .select('id')
    .single();

  masterListId = newProduct.id;
  console.log('✅ Producto agregado a catálogo:', item.produto);
}
```

---

### **B. Validación de Precios**

**Problema**:
```javascript
// Acepta cualquier precio sin validar
current_unit_price: item.preco  // ❌ Puede ser 0.01 o 1000000
```

**Solución**:
```javascript
// Validar rangos razonables por categoría
const priceRanges = {
  'cereales': { min: 1.0, max: 50 },
  'carnes': { min: 5.0, max: 100 },
  'vegetales': { min: 0.5, max: 30 }
};

const category = detectCategory(item.produto);
const range = priceRanges[category] || { min: 0.1, max: 1000 };

if (item.preco < range.min || item.preco > range.max) {
  console.warn(`⚠️ Precio inusual: ${item.produto} - R$${item.preco}`);
  // Agregar flag para revisión
  verification_status: 'needs_review'
}
```

---

### **C. Normalización de Unidades**

**Problema**:
```javascript
// NO normaliza unidades
Fornecedor A: "Tomate R$5/kg"
Fornecedor B: "Tomate R$0.005/g"  // Mismo precio!

// Sistema compara: 5 vs 0.005 → ERROR
```

**Solución**:
```javascript
// Tabla de conversión
const unitConversions = {
  // Peso
  'g': { base: 'kg', factor: 0.001 },
  'kg': { base: 'kg', factor: 1 },
  'ton': { base: 'kg', factor: 1000 },
  // Volumen
  'ml': { base: 'L', factor: 0.001 },
  'L': { base: 'L', factor: 1 },
  // Cantidad
  'unidade': { base: 'unidade', factor: 1 },
  'docena': { base: 'unidade', factor: 12 },
  'caixa': { base: 'unidade', factor: 1 } // Requiere especificar unidades/caixa
};

function normalizePrice(price, unit) {
  const conversion = unitConversions[unit.toLowerCase()];
  if (!conversion) return { price, unit, normalized: false };

  return {
    price: price / conversion.factor,
    unit: conversion.base,
    original_price: price,
    original_unit: unit,
    normalized: true
  };
}
```

---

### **D. Referencias entre Nodos**

**Problema**:
```javascript
// Múltiples nodos referencian:
$('Detectar Opción del Menú').first().json.user_data.restaurant_id
// ❌ Pero "Detectar Opción del Menú" NO EXISTE!
```

**Ubicaciones**:
- Línea 675, 679, 726, 1038

**Solución**:
```javascript
// Estandarizar nombre correcto:
$('Detectar Acción del Agente').first().json.user_data.restaurant_id

// O mejor: usar variable común
const userData = $('Buscar Usuario').first().json;
const restaurantId = userData.restaurant_id;
```

---

## 📋 PLAN DE IMPLEMENTACIÓN

### **FASE 1: FIXES CRÍTICOS (Sin romper nada)**

1. ✅ **Auto-populate master_list**
   - Nodo: "Procesar y Guardar Precios" (línea 1464)
   - Nodo: "Guardar Fornecedor BD" (línea 1870)
   - Agregar función `createMasterListEntry()`

2. ✅ **Normalización de unidades**
   - Crear nodo: "Normalizar Unidades" (antes de guardar)
   - Aplicar en: "Procesar y Guardar Precios", "Guardar Fornecedor BD"

3. ✅ **Validación de precios**
   - Crear nodo: "Validar Precio" (antes de guardar)
   - Flags: `verification_status` ('verified' / 'needs_review')

4. ✅ **Estandarizar referencias**
   - Buscar y reemplazar todas las referencias incorrectas
   - Usar nombres consistentes

---

### **FASE 2: PROMPTS DETERMINISTAS**

5. ✅ **Agente de Menú Principal** (línea 1149)
   - Más explícito en detección de intenciones
   - Formato de respuesta más estructurado

6. ✅ **Agente de Compras** (línea 752)
   - Separar en fases: confirmación → análisis → recomendación
   - Output más detallado

7. ✅ **Agente Subir Precios** (línea 1371)
   - Más claro en formato esperado
   - Confirmación explícita antes de guardar

8. ✅ **Agente Registrar Fornecedor** (línea 1802)
   - Validación de datos antes de guardar
   - Detección de duplicados ANTES de INSERT

---

### **FASE 3: EXPANSIÓN DE FUNCIONALIDAD**

9. ⏳ **Submenú: Actualizar Precios**
   - Crear nodo "Router Actualizar Precios"
   - Opción 1: Ver status
   - Opción 2: Actualizar

10. ⏳ **Submenú: Registrar Fornecedor**
    - Crear nodo "Router Registrar Fornecedor"
    - Opción 1: Criar
    - Opción 2: Atualizar
    - Opción 3: Ver lista

11. ⏳ **Flujo de Compra Mejorado**
    - Análisis de ahorros (calcular promedio)
    - Segmentación por proveedor
    - Info de entrega/mínimos
    - Opciones de confirmar/modificar

12. ⏳ **Configuración Expandida**
    - Configuración por producto (9 campos)
    - Días de compra
    - Preferencias por día
    - Autorización de compra automática

---

## 🎯 PRIORIZACIÓN

### **PRIORIDAD 1 (AHORA) - Fixes Críticos:**
- Auto-populate master_list → **CRÍTICO**
- Normalización de unidades → **CRÍTICO**
- Estandarizar referencias → **CRÍTICO**

### **PRIORIDAD 2 (HOY) - Prompts:**
- Mejorar todos los prompts → **IMPORTANTE**

### **PRIORIDAD 3 (DESPUÉS) - Expansión:**
- Submenús → **DESEADO**
- Flujo de compra mejorado → **DESEADO**
- Configuración expandida → **FUTURO**

---

## ⚠️ RIESGOS Y MITIGACIÓN

### **Riesgo 1: Romper funcionalidad existente**
**Mitigación**:
- Testing exhaustivo después de cada cambio
- Mantener lógica original como fallback
- Commits incrementales

### **Riesgo 2: Cambios de schema en BD**
**Mitigación**:
- NO modificar tablas existentes
- Agregar campos nuevos como NULL (opcionales)
- Migración gradual

### **Riesgo 3: Embeddings costosos**
**Mitigación**:
- Cache de embeddings ya generados
- Batch processing
- Límite de generación diaria

---

## 📊 MÉTRICAS DE ÉXITO

**Antes de mejoras**:
- Productos huérfanos: ~30-40%
- Errores de unidades: ~15-20%
- Referencias rotas: 4 ubicaciones

**Después de mejoras**:
- Productos huérfanos: 0% ✅
- Errores de unidades: 0% ✅
- Referencias rotas: 0 ✅
- Tiempo de respuesta: < 5s por mensaje
- Tasa de error: < 2%

---

**Siguiente paso**: Comenzar con PRIORIDAD 1 (Fixes Críticos)
