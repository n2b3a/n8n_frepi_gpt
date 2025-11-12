# Mapa Visual del Flujo - Workflow Frepi

## 🗺️ FLUJO PRINCIPAL

```
┌─────────────────────────────────────────────────────────────────┐
│                    INICIO: WhatsApp Trigger                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │ Config Global  │
                   └────────┬───────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Extraer Datos WhatsApp│
                └───────┬───────────────┘
                        │
                ┌───────┴────────────────────────────┐
                │ ¿Archivo No Soportado?             │
                └───┬─────────────────────────┬──────┘
           SÍ       │                         │ NO
                    ▼                         ▼
            [Enviar Respuesta]       ┌───────────────┐
                 (FIN)               │ Buscar Usuario│
                                     └───────┬───────┘
                                             │
                                             ▼
                                    ┌─────────────────────┐
                                    │ Buscar Sesión Activa│
                                    └──────────┬──────────┘
                                               │
                                               ▼
                                    ┌───────────────────────┐
                                    │ ¿Es Continuación?     │
                                    └──┬─────────────────┬──┘
                              SÍ       │                 │ NO
                                       │                 │
                ┌──────────────────────┘                 └──────────────┐
                │                                                       │
                ▼                                                       ▼
    ┌─────────────────────────┐                           ┌────────────────────┐
    │Detectar Opção Continuação│                           │ ¿Usuario Existe?   │
    └───────────┬──────────────┘                           └──┬──────────────┬──┘
                │                                         SÍ  │              │ NO
                ▼                                              │              │
        [Router Continuação]                                   │              │
         (5 salidas)                                           ▼              ▼
                                                    ┌───────────────┐  ┌──────────┐
                                                    │Calcular % Pref│  │Buscar    │
                                                    └───────┬───────┘  │Sesión    │
                                                            │          │Onboarding│
                                                            ▼          └────┬─────┘
                                                   ┌─────────────────┐      │
                                                   │Verificar Setup  │      ▼
                                                   │Completo         │  [Flujo
                                                   └────────┬────────┘  Onboarding]
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │¿Setup Completo? │
                                                   └──┬───────────┬──┘
                                            NO        │           │ SÍ
                                                      │           │
                                    ┌─────────────────┘           └─────────────────┐
                                    │                                               │
                                    ▼                                               ▼
                          ┌──────────────────┐                         ┌────────────────────┐
                          │ Crear Sesión     │                         │ Agente de Menú     │
                          │ de Setup         │                         │ Principal          │
                          └─────────┬────────┘                         └─────────┬──────────┘
                                    │                                            │
                                    ▼                                            ▼
                          ┌──────────────────┐                         ┌────────────────────┐
                          │ Agente de Setup  │                         │Detectar Acción     │
                          └─────────┬────────┘                         │del Agente          │
                                    │                                  └─────────┬──────────┘
                                    ▼                                            │
                          [Flujo de Setup]                                       ▼
                                                                       ┌────────────────────┐
                                                                       │ ¿Es Acción Real?   │
                                                                       └──┬──────────────┬──┘
                                                                   SÍ    │              │ NO
                                                                          │              │
                                                                          ▼              ▼
                                                                  [Router de      [Enviar
                                                                   Acciones]      Respuesta]
                                                                   (4 salidas)
```

---

## 🎯 DETALLE DE ACCIONES (Router de Acciones)

```
                         ┌────────────────┐
                         │ Router de      │
                         │ Acciones       │
                         └───┬───┬───┬───┬┘
            ┌────────────────┘   │   │   └────────────────┐
            │                    │   │                    │
            ▼                    ▼   ▼                    ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ 0: HACER     │    │ 1: CONFIGURAR│    │ 2: ENVIAR    │    │ 3: CADASTRAR │
    │    PEDIDO    │    │              │    │    PREÇOS    │    │   FORNECEDOR │
    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
           │                   │                    │                    │
           ▼                   ▼                    ▼                    ▼
    [Flujo Compras]     [Submenú Pref]    [Submenú Preços]      [Flujo Fornecedor]
```

---

## 🛒 FLUJO DE COMPRAS (Hacer Pedido)

```
    ┌─────────────────────┐
    │ Crear Sesión        │
    │ de Compra           │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Vector Search       │ ⚠️ Requiere RPC: match_products_v2
    │ Products            │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Agente de Compras   │ 🤖 Usa: gpt-4o-mini
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Extraer Respuesta   │
    │ Agente Compras      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Detectar Pedido     │
    │ Completo            │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Enviar Respuesta]
           ▼
    ┌─────────────────────┐
    │ ¿Pedido Completo?   │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Enviar Respuesta]
           ▼
    ┌─────────────────────┐
    │ Validar             │
    │ Disponibilidad      │
    │ Precios             │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Generar Mensaje     │
    │ Aviso               │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ ¿Mostrar Aviso?     │
    └──┬──────────────┬───┘
  SÍ   │              │ NO
       │              │
       ▼              ▼
   [Enviar      ┌─────────────────────┐
   Respuesta]   │ Buscar Precios      │
                │ Todos Proveedores   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Generar             │
                │ Recomendación       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Continuation        │
                │ Handler             │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Update Session DB   │
                └──────────┬──────────┘
                           │
                           ▼
                   [Enviar Respuesta]
```

---

## 💰 FLUJO DE PREÇOS (Atualizar Preços)

```
    ┌─────────────────────┐
    │ Preparar Datos      │
    │ Subir Precios       │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Generar Submenú     │ ⚠️ CREA ESTADO EN BD:
    │ Precios             │    awaiting_submenu: 'precos'
    └──────────┬──────────┘
               │
               ▼
        [Enviar Respuesta]
               │
        (Usuario responde)
               │
               ▼
    ┌─────────────────────┐
    │ Detectar Opción     │ 🧹 LIMPIA ESTADO EN BD
    │ Submenú Precios     │
    └──────┬──────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Router Submenú      │
    │ Precios             │
    └──┬────────────────┬─┘
  0:   │                │ 1:
  VER  │                │ ACTUALIZAR
       │                │
       ▼                ▼
  ┌──────────┐   ┌─────────────────────┐
  │Ver Status│   │ Crear Sesión        │
  │Preços    │   │ Subir Precios       │
  └────┬─────┘   └──────────┬──────────┘
       │                    │
       └────────┬───────────┘
                ▼
    ┌─────────────────────┐
    │ Agente Subir        │ 🤖 Usa: gpt-4o-mini
    │ Precios             │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Detectar Precios    │
    │ Completos           │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Continuation Handler]
           ▼
    ┌─────────────────────┐
    │ ¿Precios Completos? │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Continuation Handler]
           ▼
    ┌─────────────────────┐
    │ Procesar y Guardar  │ ✅ AUTO-POPULATE:
    │ Precios             │    Crea productos si no existen
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Continuation        │
    │ Handler             │
    └──────────┬──────────┘
               │
               ▼
        [Enviar Respuesta]
```

---

## 🆕 FLUJO ONBOARDING (Nuevo Usuario)

```
    ┌─────────────────────┐
    │ Buscar Sesión       │
    │ de Onboarding       │
    └──────┬──────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ ¿Existe Sesión      │
    │  Onboarding?        │
    └──┬────────────────┬─┘
  SÍ   │                │ NO
       │                │
       ▼                ▼
  ┌──────────┐    ┌──────────────┐
  │Preparar  │    │ Crear Nueva  │
  │Contexto  │    │ Sesión       │
  │de Sesión │    └──────┬───────┘
  └────┬─────┘           │
       │                 ▼
       │          ┌──────────────┐
       │          │ Preparar     │
       │          │ Input para   │
       │          │ Onboarding   │
       └────┬─────┴──────┬───────┘
            │            │
            └─────┬──────┘
                  ▼
         ┌─────────────────┐
         │ Onboarding      │ 🤖 Usa: gpt-4o-mini
         │ Agent           │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Detectar        │
         │ Onboarding      │
         │ Completo        │
         └────┬──────────┬─┘
         SÍ   │          │ NO
              │          │
              ▼          ▼
    ┌──────────────┐  ┌─────────────────┐
    │ ¿Onboarding  │  │ Actualizar      │
    │  Completo?   │  │ Sesión Parcial  │
    └──┬────────┬──┘  └────────┬────────┘
  SÍ   │        │ NO           │
       │        └──────────────┼──────────┐
       │                       │          │
       ▼                       ▼          ▼
  ┌──────────┐          ┌──────────┐  [Preparar Output
  │Guardar   │          │Preparar  │   Onboarding]
  │Restaurant│          │Output    │       │
  └────┬─────┘          │Onboarding│       ▼
       │                └────┬─────┘  [Enviar
       ▼                     │         Respuesta]
  ┌──────────────┐          │
  │Buscar        │          │
  │Restaurante   │          │
  │Recién Creado │ ⚠️ BUG   │
  └──────┬───────┘          │
         │                  │
         ▼                  │
  ┌──────────────┐          │
  │Extraer ID    │          │
  │Restaurante   │          │
  └──────┬───────┘          │
         │                  │
         ▼                  │
  ┌──────────────┐          │
  │Guardar       │          │
  │Contacto      │          │
  └──────┬───────┘          │
         │                  │
         ▼                  │
  ┌──────────────┐          │
  │Marcar Sesión │          │
  │Completa      │          │
  └──────┬───────┘          │
         │                  │
         ▼                  │
  ┌──────────────┐          │
  │Preparar      │          │
  │Mensaje Final │          │
  └──────┬───────┘          │
         │                  │
         └─────┬────────────┘
               ▼
        [Enviar Respuesta]
```

---

## ⚙️ FLUJO DE SETUP (Configurar Preferencias)

```
    ┌─────────────────────┐
    │ Crear Sesión        │
    │ de Setup            │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Agente de Setup     │ 🤖 Usa: gpt-4o-mini
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Detectar Setup      │
    │ Completo            │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Enviar Respuesta]
           ▼
    ┌─────────────────────┐
    │ ¿Setup Finalizado?  │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Enviar Respuesta]
           ▼
    ┌─────────────────────┐
    │ Extraer Preferencias│
    │ del Setup           │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Extraer JSON de     │ 🤖 Usa LLM para parsear
    │ Preferencias        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Preparar Datos      │
    │ para Guardar        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Actualizar          │
    │ Restaurante con     │
    │ Preferencias        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Limpiar Output      │
    │ Después de Guardar  │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Agente de Menú      │
    │ Principal           │
    └──────────┬──────────┘
               │
               ▼
        [Enviar Respuesta]
```

---

## 📦 FLUJO FORNECEDOR (Cadastrar Fornecedor)

```
    ┌─────────────────────┐
    │ Agente Registrar    │ 🤖 Usa: gpt-4o-mini
    │ Fornecedor          │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Detectar Fornecedor │
    │ Completo            │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Enviar Respuesta]
           ▼
    ┌─────────────────────┐
    │ ¿Fornecedor         │
    │  Completo?          │
    └──────┬────────┬─────┘
      SÍ   │        │ NO
           │        └────────► [Enviar Respuesta]
           ▼
    ┌─────────────────────┐
    │ Guardar Fornecedor  │ ✅ AUTO-POPULATE:
    │ BD                  │    Crea productos si no existen
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Check If Duplicate  │
    └──────┬────────┬─────┘
      NO   │        │ SÍ
           │        │
           │        ▼
           │   ┌─────────────────────┐
           │   │ Router: ¿Es         │
           │   │ Decisión Duplicado? │
           │   └──┬────────────────┬─┘
           │  SÍ  │                │ NO
           │      │                └───► [Volver a Detectar]
           │      │
           └──┬───┘
              ▼
    ┌─────────────────────┐
    │ Continuation        │
    │ Handler             │
    └──────────┬──────────┘
               │
               ▼
        [Enviar Respuesta]
```

---

## 🔄 FLUJO DE CONTINUACIÓN

```
    ┌─────────────────────────────────────┐
    │ CUALQUIER FLUJO TERMINA CON:        │
    │ Continuation Handler                │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ 1. Prepara mensaje de continuación  │
    │ 2. Marca session_completed = true   │
    │ 3. Setea awaiting_continuation=true │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ Update Session DB                   │
    │ - session_end = NOW                 │
    │ - awaiting_continuation = true      │
    └──────────────┬──────────────────────┘
                   │
                   ▼
            [Enviar Respuesta]
                   │
                   │ (Mensaje: "Posso te ajudar com algo mais?
                   │           1️⃣ Fazer outra compra
                   │           2️⃣ Atualizar preços...")
                   │
            (Usuario responde)
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ ¿Es Continuación?                   │
    │ (Verifica: awaiting_continuation)   │
    └──────────────┬──────────────────────┘
              SÍ   │
                   ▼
    ┌─────────────────────────────────────┐
    │ Detectar Opção Continuação          │
    │ - Analiza mensaje del usuario       │
    │ - Verifica si hay submenú activo    │
    │ - Timeout de 30 minutos             │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ Router Continuação                  │
    │ 0: FAZER_COMPRA                     │
    │ 1: ATUALIZAR_PRECOS                 │
    │ 2: REGISTRAR_FORNECEDOR             │
    │ 3: MOSTRAR_MENU                     │
    │ 4: SUBMENU_PRECOS (si está activo)  │
    └─────────────────────────────────────┘
```

---

## ⚠️ PUNTOS PROBLEMÁTICOS IDENTIFICADOS

### 1. ❌ NODO "Enviar Respuesta" - Punto único de salida
**Problema:** Recibe de 14+ fuentes diferentes
**Riesgo:** Mensajes duplicados si múltiples flujos se activan

### 2. ⚠️ FLUJO Onboarding → "Extraer ID Restaurante"
**Problema:** Acceso a `restaurants[0]` sin validar que exista
**Riesgo:** Crash si no hay resultados

### 3. 🔴 TODOS los agentes con modelo inválido
**Problema:** `gpt-4.1-mini` no existe
**Riesgo:** Workflow NO FUNCIONAL

### 4. ❓ Vector Search → RPC `match_products_v2`
**Problema:** No hay verificación de que la función exista
**Riesgo:** Error si no está configurada en Supabase

### 5. 🔄 Lógica de Continuación compleja
**Problema:** Múltiples estados, timeouts, submenús
**Riesgo:** Difícil de debuggear, posibles race conditions

### 6. 🗄️ Estado en BD con limpieza manual
**Problema:** `awaiting_submenu` se limpia en código, no automáticamente
**Riesgo:** Estado inconsistente si el flujo se interrumpe

---

## 📊 ESTADÍSTICAS DEL WORKFLOW

```
Total de nodos:           108
Nodos Code:               ~30
Nodos Supabase:           ~20
Nodos AI (Agent):         8
Nodos IF:                 12
Nodos Switch:             3
Nodos WhatsApp:           2

Puntos de decisión:       15
Flujos paralelos:         4
Profundidad máxima:       15 niveles
Complejidad ciclomática:  ALTA

Uso estimado de tokens:   ~500-1000 por conversación
Llamadas a OpenAI:        1-10 por flujo
Queries a Supabase:       5-20 por flujo
```

---

## 🎯 RECOMENDACIONES DE REFACTORING

### Prioridad ALTA:
1. **Separar en sub-workflows**
   - Onboarding.json
   - Compras.json
   - Precios.json
   - Fornecedor.json
   - Menu.json

2. **Centralizar "Enviar Respuesta"**
   - Agregar nodo de deduplicación
   - Implementar queue de mensajes

3. **Simplificar estado de sesiones**
   - Usar enum para estados
   - Implementar state machine

### Prioridad MEDIA:
4. Renombrar todos los nodos a inglés o portugués (consistencia)
5. Crear biblioteca de funciones reutilizables
6. Implementar logging estructurado global

### Prioridad BAJA:
7. Agregar tests automatizados
8. Implementar monitoring y alertas
9. Crear documentación interactiva
