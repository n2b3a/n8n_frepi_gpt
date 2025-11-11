# 📋 Documentación Completa - Frepi MVP1

**Sistema**: Frepi MVP1 - Main | SA - Enhanced
**Plataforma**: n8n Workflow Automation
**Canal**: WhatsApp Business API
**IA**: OpenAI GPT-4.1-mini (Agentes conversacionales)
**Base de Datos**: Supabase (PostgreSQL)

---

## 🎯 ¿Qué es Frepi?

**Frepi** es un **asistente inteligente de compras para restaurantes** que funciona a través de WhatsApp. Su objetivo es ayudar a dueños y encargados de restaurantes a:

- ✅ **Comparar precios** entre múltiples proveedores
- ✅ **Encontrar los mejores productos** según sus necesidades
- ✅ **Ahorrar tiempo y dinero** en el proceso de compras
- ✅ **Recibir recomendaciones inteligentes** basadas en sus preferencias

### **Propuesta de Valor:**

En lugar de:
- Llamar a 5-10 proveedores diferentes
- Comparar precios manualmente en Excel
- Perder horas cada semana en gestión de compras

**Con Frepi:**
- Envía tu lista de compras por WhatsApp
- Recibe recomendaciones instantáneas de dónde comprar cada producto
- Ahorra hasta 20-30% en costos y 80% en tiempo

---

## 🏗️ Arquitectura del Sistema

### **Componentes Principales:**

```
┌─────────────────────────────────────────────────────────────┐
│                      WhatsApp Business API                   │
│                  (Canal de comunicación)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      n8n Workflow Engine                     │
│                    (Orquestador principal)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Onboarding  │  │   Menu       │  │  Agentes de  │     │
│  │   Agent      │  │   Principal  │  │   Acción     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Compras     │  │  Registrar   │  │  Subir       │     │
│  │   Agent      │  │  Fornecedor  │  │  Precios     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    OpenAI GPT-4.1-mini                       │
│              (Motor de procesamiento de lenguaje)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Supabase Database                       │
│                     (PostgreSQL + Vector)                    │
│                                                              │
│  • restaurant_people     • suppliers                        │
│  • restaurants           • supplier_mapped_products         │
│  • line_sessions         • pricing_history                  │
│  • master_list           • (búsqueda vectorial)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Flujos Principales

### **1. FLUJO DE ONBOARDING (Usuario Nuevo)**

**Objetivo**: Registrar un nuevo restaurante en el sistema

**Pasos**:

```
Usuario: "Hola"
   ↓
Bot: Bienvenida cálida + Explicación de Frepi
     "Sou o Frepi, seu assistente inteligente de compras...
      Para começar, preciso cadastrar seu restaurante (4 perguntas). Pode ser?"
   ↓
Usuario: "Sim"
   ↓
Bot: "Qual é o nome do seu restaurante?" 🍽️
Usuario: "Restaurante Sabor"
   ↓
Bot: "E qual é o seu nome (pessoa de contato)?" 👤
Usuario: "João Silva"
   ↓
Bot: "Em qual cidade fica o restaurante?" 📍
Usuario: "São Paulo"
   ↓
Bot: "Que tipo de estabelecimento?" 🏪
Usuario: "Restaurante"
   ↓
Bot: "✅ Perfeito! Cadastro completo!

     🍽️ Bem-vindo ao Frepi!

     Escolha uma opção:
     1️⃣ Fazer uma compra
     2️⃣ Atualizar preços de fornecedor
     3️⃣ Registrar/Atualizar fornecedor
     4️⃣ Configurar preferências ⬅️ Recomendado!"
```

**Datos guardados**:
- `restaurants`: restaurant_name, restaurant_type, city
- `restaurant_people`: first_name, last_name, whatsapp_number, restaurant_id
- `line_sessions`: sesión de onboarding completada

**Duración**: 2-3 minutos
**Nodos involucrados**:
- Onboarding Agent (línea 133)
- Detectar Onboarding Completo (línea 358)
- Guardar Restaurante (línea 437)
- Guardar Contacto (línea 533)

---

### **2. FLUJO DE MENÚ PRINCIPAL (Usuario Existente)**

**Objetivo**: Identificar qué quiere hacer el usuario y rutear a la acción correcta

**Escenario A - Usuario saluda:**
```
Usuario: "Oi" / "Bom dia"
   ↓
Bot: "Olá! Como posso te ajudar hoje? 😊

     Escolha uma opção:
     1️⃣ Fazer uma compra
     2️⃣ Atualizar preços de fornecedor
     3️⃣ Registrar/Atualizar fornecedor
     4️⃣ Configurar preferências

     💬 Digite o número ou descreva o que precisa."
```

**Escenario B - Usuario selecciona opción:**
```
Usuario: "1" o "fazer uma compra"
   ↓
Sistema: ACAO:FAZER_PEDIDO detectada
   ↓
Router → Flujo de Compras
```

**Nodos involucrados**:
- Agente de Menú Principal (línea 1149)
- Detectar Acción del Agente (línea 1204)
- Router de Acciones (línea 1218)

**Acciones disponibles**:
1. **FAZER_PEDIDO** → Flujo de Compras
2. **ENVIAR_PRECOS** → Flujo de Subir Precios
3. **CADASTRAR_FORNECEDOR** → Flujo de Registrar Fornecedor
4. **CONFIGURAR** → Flujo de Configuración de Preferencias

---

### **3. FLUJO DE CONFIGURACIÓN DE PREFERENCIAS (Setup)**

**Objetivo**: Capturar las preferencias del usuario para hacer mejores recomendaciones

**Pasos**:

```
Usuario: "4" (Configurar preferências)
   ↓
Bot: "O que você prioriza nas compras?
     - Preço baixo (economizar)
     - Qualidade (melhor produto)
     - Equilíbrio (balanceado)"
   ↓
Usuario: "Preço baixo"
   ↓
Bot: "Quais produtos você compra com mais frequência?"
Usuario: "Tomate, cebola, arroz, feijão, óleo"
   ↓
Bot: "Tem algum fornecedor preferido?"
Usuario: "Fornecedor ABC, Fornecedor XYZ"
   ↓
Bot: "Com que frequência faz pedidos?"
Usuario: "Duas vezes por semana"
   ↓
Bot: "Qual é o orçamento mensal aproximado?"
Usuario: "R$ 5000"
   ↓
Bot: "SETUP_FINALIZADO
     Pronto! Suas preferências foram salvas. ✅"
```

**Datos guardados en `restaurants`**:
- `price_sensitivity`: 0.2 (precio), 0.5 (equilíbrio), 0.8 (calidad)
- `preferred_suppliers`: ["Fornecedor ABC", "Fornecedor XYZ"]
- `category_preferences`: JSON con productos frecuentes
- `brand_loyalties`: JSON con marcas preferidas

**Importancia**: Estos datos son CRÍTICOS para el motor de recomendaciones.

**Nodos involucrados**:
- Agente de Setup (línea 945)
- Extraer JSON de Preferencias (línea 1077)
- Preparar Datos para Guardar (línea 1244)
- Actualizar Restaurante con Preferencias (línea 1287)

---

### **4. FLUJO DE REGISTRO DE FORNECEDOR**

**Objetivo**: Agregar un nuevo proveedor al sistema con sus productos y precios

**Pasos**:

```
Usuario: "3" (Registrar fornecedor)
   ↓
Bot: "Qual é o nome do fornecedor?" 📦
Usuario: "Fornecedor ABC"
   ↓
Bot: "Qual é o telefone/WhatsApp do fornecedor?"
Usuario: [Envía contacto de WhatsApp] o "+5511999999999"
   ↓
Bot: "Em quais dias ele entrega?" 🚚
Usuario: "Segunda, quarta e sexta"
   ↓
Bot: "Quais produtos ele fornece?"
Usuario: "Tomate R$5/kg
         Cebola R$3/kg
         Arroz R$25/saco"
   ↓
Bot: "FORNECEDOR_CADASTRADO
     ✅ Fornecedor ABC cadastrado com sucesso!"
```

**Datos guardados**:
- `suppliers`: company_name, whatsapp_number, delivery_days, is_active
- `supplier_mapped_products`: productos con precios actuales
- `pricing_history`: historial de precios para tracking

**Características especiales**:
- ✅ Acepta contactos de WhatsApp directamente
- ✅ Matching inteligente con catálogo maestro (`master_list`)
- ✅ Detección de duplicados
- ✅ Guarda historial de precios

**Nodos involucrados**:
- Agente Registrar Fornecedor (línea 1802)
- Detectar Fornecedor Completo (línea 1857)
- Guardar Fornecedor BD (línea 1870)

---

### **5. FLUJO DE SUBIR PRECIOS**

**Objetivo**: Actualizar precios de un proveedor existente

**Pasos**:

```
Usuario: "2" (Atualizar preços)
   ↓
Bot: "Me envie a lista de preços atualizada do fornecedor."
Usuario: "Fornecedor XYZ:
         Tomate R$5.50/kg
         Cebola R$3.20/kg
         Arroz R$26/saco"
   ↓
Sistema: Procesa lista, hace matching con catálogo
   ↓
Bot: "PRECOS_CONFIRMADOS
     ✅ Preços atualizados com sucesso!"
```

**Datos guardados**:
- `supplier_mapped_products`: actualiza `current_unit_price`
- `pricing_history`: registra snapshot con fecha

**Importancia**: Mantener precios actualizados (< 30 días) es crítico para buenas recomendaciones.

**Nodos involucrados**:
- Agente Subir Precios (línea 1371)
- Detectar Precios Completos (línea 1426)
- Procesar y Guardar Precios (línea 1473)

---

### **6. FLUJO DE HACER COMPRA (⭐ CORE FEATURE)**

**Objetivo**: Recibir lista de compras y recomendar dónde comprar cada producto

**Pasos**:

```
Usuario: "1" (Fazer uma compra)
   ↓
Bot: "Ótimo! Me diga o que você precisa comprar."
Usuario: "Preciso de:
         - 5kg de tomate
         - 3kg de cebola
         - 2 sacos de arroz
         - 1 garrafa de óleo"
   ↓
Sistema:
  1. Busca vectorial en catálogo (OpenAI Embeddings)
  2. Consulta precios en BD
  3. Aplica algoritmo de scoring
  4. Genera recomendaciones
   ↓
Bot: "📋 RECOMENDAÇÕES DE COMPRA:

🍅 Tomate (5kg):
   → Fornecedor ABC - R$5.00/kg = R$25.00 ⭐
   → Fornecedor XYZ - R$5.50/kg = R$27.50

🧅 Cebola (3kg):
   → Fornecedor XYZ - R$3.20/kg = R$9.60 ⭐
   → Fornecedor ABC - R$3.50/kg = R$10.50

🍚 Arroz (2 sacos):
   → Fornecedor ABC - R$25.00/saco = R$50.00 ⭐
   (Seu fornecedor preferido!)

💰 TOTAL ESTIMADO: R$84.60
💡 Economia de 15% vs. comprar todo em um lugar!

✅ Compre em Fornecedor ABC: tomate, arroz
✅ Compre em Fornecedor XYZ: cebola, óleo"
```

**Algoritmo de Scoring** (línea ~1546):

```javascript
// Para cada producto:
const priceScore = 1 - ((price - minPrice) / priceRange);
const preferredBonus = preferredSuppliers.includes(supplier_id) ? 0.2 : 0;
const freshBonus = daysOld < 7 ? 0.1 : 0;

const finalScore = (priceScore * (1 - priceSensitivity)) +
                   (preferredBonus * priceSensitivity) +
                   freshBonus;

// Si price_sensitivity = 0.2 → Prioriza precio bajo
// Si price_sensitivity = 0.8 → Prioriza proveedores preferidos/calidad
```

**Nodos involucrados**:
- Agente de Compras (línea 752)
- Vector Search Products (línea 735) - OpenAI Embeddings
- Validar Disponibilidad Precios (línea 1619)
- Buscar Precios Todos Proveedores (línea 1533)
- Generar Recomendación (línea 1546)

**Características especiales**:
- ✅ Búsqueda semántica (entiende "jitomate" = "tomate")
- ✅ Valida frescura de precios (avisa si > 30 días)
- ✅ Considera preferencias del usuario
- ✅ Optimiza costo total vs. conveniencia

---

## 🗄️ Modelo de Datos (Supabase)

### **Tabla: `restaurants`**
```sql
id (uuid, PK)
restaurant_name (text)
restaurant_type (text) -- restaurant, cafe, hotel, etc.
city (text)
street_address (text)
is_active (boolean)
customer_since (timestamp)
price_sensitivity (numeric) -- 0.2 a 0.8
category_preferences (jsonb)
preferred_suppliers (text[])
brand_loyalties (jsonb)
created_at (timestamp)
updated_at (timestamp)
```

### **Tabla: `restaurant_people`**
```sql
id (uuid, PK)
restaurant_id (uuid, FK → restaurants.id)
first_name (text)
last_name (text)
whatsapp_number (text, UNIQUE)
is_primary_contact (boolean)
is_active (boolean)
created_at (timestamp)
```

### **Tabla: `line_sessions`** (Tracking de conversaciones)
```sql
session_id (text, PK)
channel_id (text) -- phone number
restaurant_id (uuid, FK)
person_id (uuid, FK)
channel_type (text) -- 'whatsapp'
session_type (text) -- 'discovery' o 'transactional'
session_start (timestamp)
session_end (timestamp)
is_completed (boolean)
session_goal_achieved (boolean)
primary_intent (text) -- 'fazer_pedido', 'registro_nuevo', etc.
awaiting_continuation (boolean)
last_activity_at (timestamp)
preferences_captured (jsonb)
products_discussed (text[])
```

### **Tabla: `suppliers`** (Proveedores)
```sql
id (uuid, PK)
company_name (text)
whatsapp_number (text)
delivery_days (text[])
is_active (boolean)
created_at (timestamp)
updated_at (timestamp)
```

### **Tabla: `supplier_mapped_products`** (Productos por proveedor)
```sql
id (uuid, PK)
supplier_id (uuid, FK → suppliers.id)
master_list_id (uuid, FK → master_list.id)
supplier_product_name (text)
current_unit_price (numeric)
price_per_unit_type (text) -- 'kg', 'liter', 'unit', etc.
currency (text) -- 'BRL'
mapping_confidence (numeric) -- 0.0 a 1.0
mapping_method (text) -- 'manual', 'llm', 'vector_search'
is_active (boolean)
created_at (timestamp)
```

### **Tabla: `pricing_history`** (Historial de precios)
```sql
id (uuid, PK)
supplier_id (uuid, FK)
master_list_id (uuid, FK)
supplier_mapped_product_id (uuid, FK)
unit_price (numeric)
currency (text)
price_per_unit_type (text)
effective_date (date)
snapshot_date (timestamp)
data_source (text) -- 'whatsapp_user', 'api', 'manual'
verification_status (text) -- 'pending', 'verified', 'outdated'
created_at (timestamp)
```

### **Tabla: `master_list`** (Catálogo maestro de productos)
```sql
id (uuid, PK)
product_name (text)
category (text)
subcategory (text)
brand (text)
alternative_names (text[])
standard_unit_type (text)
embedding (vector) -- Para búsqueda semántica
is_active (boolean)
created_at (timestamp)
```

**Función de búsqueda vectorial**:
```sql
match_products_v2(query_embedding, match_threshold, match_count)
-- Retorna productos similares usando cosine similarity
```

---

## 🔧 Nodos Clave y Funciones

### **Nodos de Gestión de Estado:**

1. **Config Global** (línea 10)
   - Define constantes: PRICE_VALIDITY_DAYS (30), timeouts, mensajes

2. **Extraer Datos WhatsApp** (línea 53)
   - Parsea mensajes entrantes
   - ✅ Soporte para contactos de WhatsApp
   - Filtra notificaciones de estado

3. **Buscar Usuario** (línea 76)
   - Query: `restaurant_people WHERE whatsapp_number = ?`

4. **¿Usuario Existe?** (línea 116)
   - Decisión: Usuario nuevo → Onboarding | Usuario existente → Menu

5. **Buscar Sesión Activa** (línea 236)
   - Query: `line_sessions WHERE channel_id = ? AND session_type = 'discovery' AND session_goal_achieved IS NULL`

6. **¿Es Continuación?** (línea 2051)
   - Verifica si usuario está respondiendo a prompt de continuación

### **Nodos de Agentes IA:**

Todos usan **OpenAI GPT-4.1-mini** con parámetros:
- `temperature`: 0.3-0.5 (respuestas consistentes)
- `maxRetries`: 3
- `timeout`: 30000ms
- `frequencyPenalty`: 1.5 (evita repetición)

**Memoria**:
- Tipo: Buffer Window Memory
- Aislamiento: sessionKey único por flujo
- Contexto: 5-10 mensajes previos

### **Nodos de Procesamiento:**

1. **Vector Search Products** (línea 735)
   - OpenAI Embeddings (text-embedding-ada-002)
   - Supabase function: `match_products_v2`
   - Threshold: 0.65 similarity

2. **Buscar Precios Todos Proveedores** (línea 1533)
   - Query con JOINs: pricing_history + suppliers + master_list
   - Filtro: is_active = true

3. **Generar Recomendación** (línea 1546)
   - Algoritmo de scoring multi-criterio
   - Consideraciones: precio, preferencias, frescura

4. **Validar Disponibilidad Precios** (línea 1619)
   - Verifica precios < 30 días
   - Genera warnings si desactualizados

---

## 🎯 Alcance Actual (MVP1)

### **✅ Funcionalidades Implementadas:**

#### **Gestión de Usuarios**
- ✅ Onboarding conversacional de nuevos restaurantes
- ✅ Captura de datos básicos (4 campos)
- ✅ Bienvenida cálida con explicación del servicio
- ✅ Validación y prevención de duplicados

#### **Gestión de Preferencias**
- ✅ Captura de prioridad (precio vs calidad vs equilíbrio)
- ✅ Registro de proveedores preferidos
- ✅ Productos comprados frecuentemente
- ✅ Frecuencia de pedidos y presupuesto

#### **Gestión de Proveedores**
- ✅ Registro de nuevos proveedores
- ✅ Captura de contacto (acepta contactos de WhatsApp)
- ✅ Días de entrega
- ✅ Productos y precios del proveedor
- ✅ Detección de duplicados

#### **Gestión de Precios**
- ✅ Subida de listas de precios
- ✅ Parsing inteligente de mensajes de texto
- ✅ Matching con catálogo maestro
- ✅ Historial de precios con timestamps
- ✅ Validación de frescura (< 30 días)

#### **Motor de Recomendaciones**
- ✅ Búsqueda semántica de productos (vectorial)
- ✅ Comparación de precios entre proveedores
- ✅ Scoring basado en preferencias del usuario
- ✅ Recomendaciones optimizadas (costo vs conveniencia)
- ✅ Cálculo de ahorros

#### **Experiencia de Usuario**
- ✅ Conversaciones naturales en portugués brasileño
- ✅ Menú automático después del registro
- ✅ Sistema de continuación (¿algo más?)
- ✅ Manejo de errores con mensajes amigables
- ✅ Logging estructurado para debugging

---

## ⚠️ Limitaciones Conocidas

### **1. Procesamiento de Mensajes**
- ❌ NO procesa imágenes (fotos de listas de precios)
- ❌ NO procesa PDFs
- ❌ NO procesa audios
- ✅ Solo acepta: texto y contactos de WhatsApp

### **2. Matching de Productos**
- ⚠️ Depende de la calidad del catálogo `master_list`
- ⚠️ Si el producto no está en el catálogo, no se puede buscar
- ⚠️ Nombres muy diferentes pueden no hacer match (ej: "jitomate" vs "tomate" funciona, pero "produto X" vs "produto ABC" puede fallar)

### **3. Validación de Precios**
- ⚠️ No verifica si el precio es "realista" (puede aceptar R$0.01 o R$1000000)
- ⚠️ No valida unidades de medida (puede mezclar kg con litros)

### **4. Multi-mensaje**
- ⚠️ Si el usuario envía varios mensajes muy rápido, pueden procesarse en orden incorrecto
- ⚠️ No hay sistema de cola para mensajes

### **5. Memoria de Agentes**
- ⚠️ Memoria se almacena en n8n (volátil)
- ⚠️ Si se reinicia n8n, se pierde el contexto
- ⚠️ No hay persistencia de conversaciones completas

### **6. Escalabilidad**
- ⚠️ Workflow síncrono (un mensaje a la vez por usuario)
- ⚠️ Sin sistema de rate limiting
- ⚠️ Sin métricas de performance

---

## 📊 Métricas y KPIs (No implementadas aún)

**Métricas sugeridas para implementar**:

### **Uso del Sistema**
- Usuarios activos diarios/semanales/mensuales
- Mensajes procesados por día
- Tiempo promedio de respuesta
- Tasa de error

### **Conversiones**
- % de onboarding completado
- % de setup de preferencias completado
- Proveedores registrados por usuario
- Precios registrados por proveedor

### **Engagement**
- Frecuencia de compras por usuario
- Productos más consultados
- Proveedores más recomendados

### **Business Impact**
- Ahorro promedio por compra
- Tiempo ahorrado por usuario
- Satisfacción del usuario (NPS)

---

## 🚀 Roadmap / Mejoras Futuras

### **Corto Plazo (1-2 meses)**

#### **Mejoras de Robustez**
- [ ] Implementar sistema de cola para mensajes
- [ ] Agregar retry logic con exponential backoff
- [ ] Persistir conversaciones en BD
- [ ] Agregar métricas y monitoring (DataDog, Sentry)

#### **Mejoras de UX**
- [ ] Procesamiento de imágenes (OCR para listas de precios)
- [ ] Confirmación antes de guardar datos
- [ ] Edición de datos ya guardados
- [ ] Búsqueda de proveedores por ubicación

#### **Motor de Recomendaciones**
- [ ] Considerar disponibilidad de stock
- [ ] Considerar tiempo de entrega
- [ ] Algoritmo de optimización de rutas (menos proveedores)
- [ ] Recomendaciones proactivas ("Precios de tomate subieron!")

### **Mediano Plazo (3-6 meses)**

#### **Integraciones**
- [ ] Integración con ERPs (Conta Azul, Bling)
- [ ] Integración con marketplaces (Mercado Livre B2B)
- [ ] API REST para partners
- [ ] Webhooks para eventos

#### **Analytics**
- [ ] Dashboard de métricas en tiempo real
- [ ] Reportes de ahorro mensual
- [ ] Insights de tendencias de precios
- [ ] Predicciones de demanda

#### **Automatización**
- [ ] Pedidos automáticos recurrentes
- [ ] Alertas de precios (por email/WhatsApp)
- [ ] Sugerencias de compra basadas en historial

### **Largo Plazo (6-12 meses)**

#### **Expansión**
- [ ] Soporte para múltiples idiomas (español, inglés)
- [ ] Expansión a otros canales (Telegram, Web, App)
- [ ] Marketplace B2B completo
- [ ] Sistema de pagos integrado

#### **IA Avanzada**
- [ ] Predicción de necesidades de compra
- [ ] Detección de fraude/precios anormales
- [ ] Negociación automática con proveedores
- [ ] Chatbot con voz (llamadas telefónicas)

---

## 🔐 Seguridad y Privacidad

### **Datos Sensibles**
- Números de WhatsApp
- Información de restaurantes
- Precios de proveedores
- Preferencias de compra

### **Medidas Actuales**
- ✅ Conexión HTTPS a Supabase
- ✅ Credenciales en variables de entorno
- ✅ Validación de input en nodos críticos

### **Mejoras Necesarias**
- [ ] Encriptación de datos sensibles en BD
- [ ] Auditoría de accesos
- [ ] LGPD/GDPR compliance
- [ ] Rate limiting para prevenir abuso
- [ ] Sistema de permisos por rol

---

## 📚 Documentación Técnica

### **Archivos Principales**
- `Frepi MVP1 - Main _ SA - Enhanced.json` - Workflow principal (3200+ líneas)
- `MEJORAS_IMPLEMENTADAS.md` - Changelog de mejoras
- `DOCUMENTACION_FREPI_MVP1.md` - Este documento

### **Configuración Necesaria**

**Variables de Entorno (n8n)**:
- `OPENAI_API_KEY` - Para GPT-4.1-mini
- `SUPABASE_URL` - URL del proyecto Supabase
- `SUPABASE_API_KEY` - Service role key de Supabase
- `WHATSAPP_PHONE_NUMBER_ID` - ID del número de WhatsApp Business
- `WHATSAPP_ACCESS_TOKEN` - Token de acceso a WhatsApp API

**Supabase Setup**:
```sql
-- 1. Crear tablas (ver modelo de datos arriba)
-- 2. Habilitar Row Level Security (RLS)
-- 3. Crear función de búsqueda vectorial
CREATE OR REPLACE FUNCTION match_products_v2(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  product_name text,
  category text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    master_list.id,
    master_list.product_name,
    master_list.category,
    1 - (master_list.embedding <=> query_embedding) as similarity
  FROM master_list
  WHERE 1 - (master_list.embedding <=> query_embedding) > match_threshold
  ORDER BY master_list.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### **Testing**

**Casos de Prueba Principales**:

1. **Onboarding Completo**
   - Usuario nuevo completa registro
   - Verifica datos en `restaurants` y `restaurant_people`

2. **Setup de Preferencias**
   - Usuario configura prioridades
   - Verifica `price_sensitivity` en `restaurants`

3. **Registro de Proveedor**
   - Usuario registra proveedor con productos
   - Verifica `suppliers`, `supplier_mapped_products`, `pricing_history`

4. **Compra con Recomendaciones**
   - Usuario pide productos
   - Verifica que recomendaciones sean correctas según preferencias

5. **Manejo de Errores**
   - Enviar mensaje inválido
   - Verificar que no rompa el flujo

---

## 📞 Soporte y Mantenimiento

### **Logs y Debugging**

**Logging Estructurado**:
Todos los nodos críticos usan prefijos:
```
[Extraer Datos WhatsApp] 📱
[Detectar Onboarding Completo] ✅
[Agente de Menú Principal] 🤖
[Buscar Precios] 🔍
[Generar Recomendación] 💡
```

**Verificar en n8n**:
- Executions → Ver historial de ejecuciones
- Workflow → Click en nodos → Ver output JSON

**Verificar en Supabase**:
```sql
-- Ver usuarios registrados hoy
SELECT * FROM restaurant_people
WHERE created_at::date = CURRENT_DATE;

-- Ver sesiones activas
SELECT * FROM line_sessions
WHERE is_completed = false
ORDER BY last_activity_at DESC;

-- Ver precios recientes
SELECT s.company_name, ml.product_name, ph.unit_price, ph.effective_date
FROM pricing_history ph
JOIN suppliers s ON ph.supplier_id = s.id
JOIN master_list ml ON ph.master_list_id = ml.id
WHERE ph.effective_date > CURRENT_DATE - INTERVAL '30 days'
ORDER BY ph.effective_date DESC;
```

### **Monitoreo Recomendado**

1. **Healthcheck diario**:
   - ¿Workflow está activo?
   - ¿Hay errores en executions?
   - ¿Supabase está respondiendo?

2. **Alertas**:
   - Tasa de error > 5%
   - Tiempo de respuesta > 10s
   - Cola de mensajes > 100

3. **Revisión semanal**:
   - Usuarios nuevos registrados
   - Proveedores activos
   - Precios desactualizados (> 30 días)

---

## 🎓 Conclusión

**Frepi MVP1** es un sistema robusto de asistente de compras conversacional que combina:

- 🤖 **IA Conversacional** (OpenAI GPT-4.1-mini)
- 🔍 **Búsqueda Semántica** (Vector embeddings)
- 📊 **Motor de Recomendaciones** (Scoring multi-criterio)
- 💬 **Experiencia Natural** (WhatsApp conversacional)
- 🗄️ **Persistencia Confiable** (Supabase PostgreSQL)

**Estado Actual**: MVP funcional con casos de uso principales implementados

**Próximos Pasos**: Mejoras de robustez, procesamiento de imágenes, y analytics

---

**Versión**: 1.0
**Última Actualización**: 2025-11-11
**Autor**: Claude (Anthropic) + n2b3a Team
**Branch**: claude/frepi-mvp1-enhancement-011CV2D93QuGYjUWdmq7GWNk
