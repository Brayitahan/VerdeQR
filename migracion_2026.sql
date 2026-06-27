-- Migración: Normalizar 13 tablas de usos en DetalleUso
-- y agregar columnas faltantes

USE VerdeQR;

-- 1. Agregar columnas faltantes
ALTER TABLE Usuario ADD COLUMN IF NOT EXISTS FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE Estado ADD COLUMN IF NOT EXISTS Descripcion VARCHAR(100);
UPDATE Estado SET Descripcion = 'Activo' WHERE IDEstado = 1;
UPDATE Estado SET Descripcion = 'Inactivo' WHERE IDEstado = 2;

-- 2. Crear DetalleUso (si no existe)
CREATE TABLE IF NOT EXISTS DetalleUso (
    IDDetalle INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    Dureza VARCHAR(50),
    Resistencia VARCHAR(50),
    UsoFinal VARCHAR(150),
    ParteComestible VARCHAR(100),
    FormaConsumo TEXT,
    ValorNutricional TEXT,
    ParteUtilizada VARCHAR(100),
    Preparacion TEXT,
    EnfermedadesTratadas TEXT,
    CaracteristicasEsteticas VARCHAR(255),
    UbicacionRecomendada VARCHAR(255),
    TipoJardineria VARCHAR(100),
    ColoracionEstacional TEXT,
    TipoArtesania VARCHAR(150),
    TecnicasElaboracion TEXT,
    ComunidadesArtesanales VARCHAR(255),
    SistemaAgroforestal VARCHAR(100),
    BeneficiosAsociados TEXT,
    CultivosCompatibles VARCHAR(255),
    FuncionPrincipal VARCHAR(150),
    EcosistemaObjetivo VARCHAR(150),
    FuncionEcologica TEXT,
    EspeciesAsociadas VARCHAR(255),
    TasaCrecimiento VARCHAR(50),
    GrupoEtnico VARCHAR(100),
    TipoCeremonia VARCHAR(150),
    SignificadoCultural TEXT,
    TipoMiel VARCHAR(100),
    EpocaFloracion VARCHAR(100),
    CalidadPolen VARCHAR(50),
    AtraccionPolinizadores TEXT,
    TipoProteccion VARCHAR(100),
    BeneficiosAmbientales TEXT,
    ZonasAplicacion VARCHAR(255),
    CapacidadCapturaCarbon VARCHAR(100),
    ColorObtenido VARCHAR(100),
    MetodoExtraccion TEXT,
    UsosTintes VARCHAR(255),
    TipoAceite VARCHAR(100),
    PropiedadesAceite TEXT,
    AplicacionesAceite VARCHAR(255),
    TipoBiocombustible VARCHAR(100),
    PoderCalorifico VARCHAR(100),
    RendimientoPorHectarea VARCHAR(100),
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- 3. Migrar datos de UsoMaderable
INSERT INTO DetalleUso (Uso, Estado, Dureza, Resistencia, UsoFinal)
SELECT Uso, Estado, Dureza, Resistencia, UsoFinal FROM UsoMaderable;

-- 4. Migrar datos de UsoComestible
INSERT INTO DetalleUso (Uso, Estado, ParteComestible, FormaConsumo, ValorNutricional)
SELECT Uso, Estado, ParteComestible, FormaConsumo, ValorNutricional FROM UsoComestible;

-- 5. Migrar datos de UsoMedicinal
INSERT INTO DetalleUso (Uso, Estado, ParteUtilizada, Preparacion, EnfermedadesTratadas)
SELECT Uso, Estado, ParteUtilizada, Preparacion, EnfermedadesTratadas FROM UsoMedicinal;

-- 6. Migrar datos de UsoOrnamental
INSERT INTO DetalleUso (Uso, Estado, CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional)
SELECT Uso, Estado, CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional FROM UsoOrnamental;

-- 7. Migrar datos de UsoArtesanal
INSERT INTO DetalleUso (Uso, Estado, TipoArtesania, TecnicasElaboracion, ComunidadesArtesanales)
SELECT Uso, Estado, TipoArtesania, TecnicasElaboracion, ComunidadesArtesanales FROM UsoArtesanal;

-- 8. Migrar datos de UsoAgroforestal
INSERT INTO DetalleUso (Uso, Estado, SistemaAgroforestal, BeneficiosAsociados, CultivosCompatibles, FuncionPrincipal)
SELECT Uso, Estado, SistemaAgroforestal, BeneficiosAsociados, CultivosCompatibles, FuncionPrincipal FROM UsoAgroforestal;

-- 9. Migrar datos de UsoRestauracionEcologica
INSERT INTO DetalleUso (Uso, Estado, EcosistemaObjetivo, FuncionEcologica, EspeciesAsociadas, TasaCrecimiento)
SELECT Uso, Estado, EcosistemaObjetivo, FuncionEcologica, EspeciesAsociadas, TasaCrecimiento FROM UsoRestauracionEcologica;

-- 10. Migrar datos de UsoCulturalCeremonial
INSERT INTO DetalleUso (Uso, Estado, GrupoEtnico, TipoCeremonia, SignificadoCultural, ParteUtilizada)
SELECT Uso, Estado, GrupoEtnico, TipoCeremonia, SignificadoCultural, ParteUtilizada FROM UsoCulturalCeremonial;

-- 11. Migrar datos de UsoMelifero
INSERT INTO DetalleUso (Uso, Estado, TipoMiel, EpocaFloracion, CalidadPolen, AtraccionPolinizadores)
SELECT Uso, Estado, TipoMiel, EpocaFloracion, CalidadPolen, AtraccionPolinizadores FROM UsoMelifero;

-- 12. Migrar datos de UsoProteccionAmbiental
INSERT INTO DetalleUso (Uso, Estado, TipoProteccion, BeneficiosAmbientales, ZonasAplicacion, CapacidadCapturaCarbon)
SELECT Uso, Estado, TipoProteccion, BeneficiosAmbientales, ZonasAplicacion, CapacidadCapturaCarbon FROM UsoProteccionAmbiental;

-- 13. Migrar datos de UsoTintoreo
INSERT INTO DetalleUso (Uso, Estado, ParteUtilizada, ColorObtenido, MetodoExtraccion, UsosTintes)
SELECT Uso, Estado, ParteUtilizada, ColorObtenido, MetodoExtraccion, UsosTintes
FROM UsoTintoreo;

-- 14. Migrar datos de UsoOleaginoso
INSERT INTO DetalleUso (Uso, Estado, TipoAceite, MetodoExtraccion, PropiedadesAceite, AplicacionesAceite, ParteUtilizada)
SELECT Uso, Estado, TipoAceite, MetodoExtraccion, PropiedadesAceite, AplicacionesAceite, ParteUtilizada
FROM UsoOleaginoso;

-- 15. Migrar datos de UsoBiocombustible
INSERT INTO DetalleUso (Uso, Estado, TipoBiocombustible, PoderCalorifico, TasaCrecimiento, RendimientoPorHectarea)
SELECT Uso, Estado, TipoBiocombustible, PoderCalorifico, TasaCrecimiento, RendimientoPorHectarea FROM UsoBiocombustible;

-- 16. Verificar migración
SELECT COUNT(*) as TotalMigrados FROM DetalleUso;
SELECT 'Maderable' as Fuente, COUNT(*) as Registros FROM UsoMaderable
UNION ALL SELECT 'DetalleUso', COUNT(*) FROM DetalleUso WHERE Dureza IS NOT NULL;

-- 17. Eliminar tablas antiguas (solo si la migración fue exitosa)
-- DROP TABLE IF EXISTS UsoBiocombustible;
-- DROP TABLE IF EXISTS UsoOleaginoso;
-- DROP TABLE IF EXISTS UsoTintoreo;
-- DROP TABLE IF EXISTS UsoProteccionAmbiental;
-- DROP TABLE IF EXISTS UsoMelifero;
-- DROP TABLE IF EXISTS UsoCulturalCeremonial;
-- DROP TABLE IF EXISTS UsoRestauracionEcologica;
-- DROP TABLE IF EXISTS UsoAgroforestal;
-- DROP TABLE IF EXISTS UsoArtesanal;
-- DROP TABLE IF EXISTS UsoOrnamental;
-- DROP TABLE IF EXISTS UsoMaderable;
-- DROP TABLE IF EXISTS UsoMedicinal;
-- DROP TABLE IF EXISTS UsoComestible;
