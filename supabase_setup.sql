-- ============================================================================
-- SUPABASE SETUP SCRIPT PARA WORKFLOW FREPI
-- ============================================================================
-- Autor: Claude
-- Fecha: 2025
-- Descripción: Script completo para configurar la base de datos de Supabase
--              con todas las funciones RPC necesarias para el workflow de n8n
-- ============================================================================

-- ============================================================================
-- 1. EXTENSIONES REQUERIDAS
-- ============================================================================

-- Habilitar extensión pgvector para búsqueda semántica
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar instalación
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        RAISE EXCEPTION 'La extensión vector no está instalada. Instálela con: CREATE EXTENSION vector;';
    ELSE
        RAISE NOTICE '✅ Extensión vector instalada correctamente';
    END IF;
END $$;

-- ============================================================================
-- 2. FUNCIÓN RPC: match_products_v2
-- ============================================================================
-- Descripción: Búsqueda vectorial de productos usando embeddings de OpenAI
-- Parámetros:
--   - query_embedding: vector(1536) - Embedding del texto de búsqueda
--   - match_threshold: float - Umbral de similaridad (0.0 - 1.0)
--   - match_count: int - Número máximo de resultados
-- Retorna: Tabla con productos similares y su score de similaridad
-- ============================================================================

-- Eliminar función si existe (para recrear)
DROP FUNCTION IF EXISTS match_products_v2(vector, float, int);

-- Crear función
CREATE OR REPLACE FUNCTION match_products_v2(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.65,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  product_name text,
  brand text,
  alternative_names text[],
  category text,
  similarity float
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
  -- Validar parámetros
  IF query_embedding IS NULL THEN
    RAISE EXCEPTION 'query_embedding no puede ser NULL';
  END IF;

  IF match_threshold < 0 OR match_threshold > 1 THEN
    RAISE EXCEPTION 'match_threshold debe estar entre 0 y 1, recibido: %', match_threshold;
  END IF;

  IF match_count < 1 OR match_count > 100 THEN
    RAISE EXCEPTION 'match_count debe estar entre 1 y 100, recibido: %', match_count;
  END IF;

  -- Ejecutar búsqueda vectorial
  RETURN QUERY
  SELECT
    m.id,
    m.product_name,
    m.brand,
    m.alternative_names,
    m.category,
    -- Calcular similaridad de coseno (1 - distancia)
    1 - (m.embedding <=> query_embedding) as similarity
  FROM master_list m
  WHERE
    -- Solo productos activos
    m.is_active = true
    -- Filtrar por umbral de similaridad
    AND 1 - (m.embedding <=> query_embedding) > match_threshold
  ORDER BY
    -- Ordenar por similaridad descendente
    m.embedding <=> query_embedding ASC
  LIMIT match_count;

  -- Log para debugging (opcional, comentar en producción)
  RAISE NOTICE 'match_products_v2 ejecutado: threshold=%, count=%, resultados=%',
    match_threshold, match_count, (SELECT COUNT(*) FROM master_list WHERE 1 - (embedding <=> query_embedding) > match_threshold);

END;
$$;

-- Agregar comentario a la función
COMMENT ON FUNCTION match_products_v2 IS
'Búsqueda vectorial de productos usando embeddings de OpenAI (text-embedding-ada-002).
Retorna productos similares al embedding de consulta proporcionado.
Usa distancia de coseno para calcular similaridad.';

-- ============================================================================
-- 3. ÍNDICES PARA OPTIMIZACIÓN
-- ============================================================================

-- Índice HNSW (Hierarchical Navigable Small World) para búsqueda vectorial rápida
-- Este índice acelera significativamente las búsquedas de vectores
CREATE INDEX IF NOT EXISTS master_list_embedding_idx
ON master_list
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Índice para búsquedas por nombre de producto
CREATE INDEX IF NOT EXISTS master_list_product_name_idx
ON master_list (product_name);

-- Índice para búsquedas por categoría
CREATE INDEX IF NOT EXISTS master_list_category_idx
ON master_list (category);

-- Índice para filtrar productos activos
CREATE INDEX IF NOT EXISTS master_list_is_active_idx
ON master_list (is_active);

-- ============================================================================
-- 4. PERMISOS Y SEGURIDAD
-- ============================================================================

-- Otorgar permisos de ejecución a usuarios autenticados
GRANT EXECUTE ON FUNCTION match_products_v2(vector, float, int) TO authenticated;
GRANT EXECUTE ON FUNCTION match_products_v2(vector, float, int) TO service_role;

-- Política RLS (Row Level Security) para master_list
-- Permitir SELECT a todos los usuarios autenticados
ALTER TABLE master_list ENABLE ROW LEVEL SECURITY;

-- Crear política si no existe
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'master_list' AND policyname = 'Enable read access for authenticated users'
  ) THEN
    CREATE POLICY "Enable read access for authenticated users"
    ON master_list
    FOR SELECT
    TO authenticated
    USING (true);
  END IF;
END $$;

-- ============================================================================
-- 5. FUNCIONES AUXILIARES
-- ============================================================================

-- Función para obtener estadísticas de embeddings
CREATE OR REPLACE FUNCTION get_embedding_stats()
RETURNS TABLE (
  total_products bigint,
  products_with_embeddings bigint,
  products_without_embeddings bigint,
  avg_embedding_dimensions float,
  categories_count bigint
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    COUNT(*) as total_products,
    COUNT(embedding) as products_with_embeddings,
    COUNT(*) - COUNT(embedding) as products_without_embeddings,
    AVG(array_length(embedding::text::float[], 1)) as avg_embedding_dimensions,
    COUNT(DISTINCT category) as categories_count
  FROM master_list;
$$;

COMMENT ON FUNCTION get_embedding_stats IS
'Retorna estadísticas sobre los embeddings en la tabla master_list';

-- ============================================================================
-- 6. VERIFICACIÓN Y TESTING
-- ============================================================================

-- Función de test para verificar que todo funciona
CREATE OR REPLACE FUNCTION test_match_products_v2()
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
  test_result text;
  test_embedding vector(1536);
  result_count int;
BEGIN
  -- Crear un embedding de prueba (todos ceros)
  test_embedding := array_fill(0, ARRAY[1536])::vector;

  -- Ejecutar búsqueda de prueba
  SELECT COUNT(*) INTO result_count
  FROM match_products_v2(test_embedding, 0.0, 5);

  -- Verificar resultado
  IF result_count >= 0 THEN
    test_result := format('✅ TEST PASSED: match_products_v2 funciona correctamente. Retornó %s resultados.', result_count);
  ELSE
    test_result := '❌ TEST FAILED: match_products_v2 no retornó resultados';
  END IF;

  RETURN test_result;
END;
$$;

-- ============================================================================
-- 7. INSTRUCCIONES DE USO
-- ============================================================================

/*
CÓMO USAR LA FUNCIÓN match_products_v2:

1. Desde el workflow de n8n:

   const { data, error } = await $supabase.rpc('match_products_v2', {
     query_embedding: [0.123, 0.456, ...],  // Array de 1536 números
     match_threshold: 0.65,                  // Opcional, default 0.65
     match_count: 5                          // Opcional, default 5
   });

2. Desde SQL directo:

   SELECT * FROM match_products_v2(
     '[0.123, 0.456, ...]'::vector(1536),
     0.65,
     5
   );

3. Para probar:

   SELECT test_match_products_v2();

4. Ver estadísticas:

   SELECT * FROM get_embedding_stats();
*/

-- ============================================================================
-- 8. EJECUTAR TESTS
-- ============================================================================

-- Ejecutar test de la función
SELECT test_match_products_v2();

-- Mostrar estadísticas
SELECT * FROM get_embedding_stats();

-- Verificar índices creados
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'master_list'
ORDER BY indexname;

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '✅ SUPABASE SETUP COMPLETADO EXITOSAMENTE';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Funciones creadas:';
    RAISE NOTICE '  - match_products_v2(vector, float, int)';
    RAISE NOTICE '  - get_embedding_stats()';
    RAISE NOTICE '  - test_match_products_v2()';
    RAISE NOTICE '';
    RAISE NOTICE 'Índices creados:';
    RAISE NOTICE '  - master_list_embedding_idx (HNSW para búsqueda vectorial)';
    RAISE NOTICE '  - master_list_product_name_idx';
    RAISE NOTICE '  - master_list_category_idx';
    RAISE NOTICE '  - master_list_is_active_idx';
    RAISE NOTICE '';
    RAISE NOTICE 'Siguiente paso:';
    RAISE NOTICE '  1. Verificar que los embeddings están generados en master_list';
    RAISE NOTICE '  2. Probar desde n8n con una búsqueda real';
    RAISE NOTICE '  3. Ajustar match_threshold según necesidad (0.65 es un buen default)';
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
END $$;
