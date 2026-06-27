-- Crear base de datos y usarla
CREATE DATABASE IF NOT EXISTS VerdeQR;
USE VerdeQR;

-- Estado
CREATE TABLE Estado (
    IDEstado INT AUTO_INCREMENT PRIMARY KEY,
    NombreEstado VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(100)
);

INSERT INTO Estado (IDEstado, NombreEstado, Descripcion) VALUES (1, 'Activo', 'Registro activo'), (2, 'Inactivo', 'Registro inactivo');

-- Usuario
CREATE TABLE Usuario (
    IDUsuario INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) NOT NULL,
    Telefono VARCHAR(20),
    Imagen VARCHAR(255),
    Contraseña VARCHAR(255) NOT NULL,
    Estado INT NOT NULL,
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Rol
CREATE TABLE Rol (
    IDRol INT AUTO_INCREMENT PRIMARY KEY,
    NombreRol VARCHAR(50) NOT NULL
);

INSERT INTO Rol (NombreRol) VALUES ('Administrador'), ('Visitante');

-- UsuarioRol
CREATE TABLE UsuarioRol (
    IDUsuarioRol INT AUTO_INCREMENT PRIMARY KEY,
    Usuario INT NOT NULL,
    Rol INT NOT NULL,
    FOREIGN KEY (Usuario) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (Rol) REFERENCES Rol(IDRol)
);

-- Especie
CREATE TABLE Especie (
    IDEspecie INT AUTO_INCREMENT PRIMARY KEY,
    NombreCientifico VARCHAR(150) NOT NULL,
    NombreVulgar VARCHAR(150) NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);


-- UsoArbol
CREATE TABLE UsoArbol (
    IDUso INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    Nombre VARCHAR(150),
    Categoria VARCHAR(50) NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- DetalleUso: unifica los 13 tipos de uso en una sola tabla
CREATE TABLE DetalleUso (
    IDDetalle INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    -- Maderable
    Dureza VARCHAR(50),
    Resistencia VARCHAR(50),
    UsoFinal VARCHAR(150),
    -- Comestible
    ParteComestible VARCHAR(100),
    FormaConsumo TEXT,
    ValorNutricional TEXT,
    -- Medicinal
    ParteUtilizada VARCHAR(100),
    Preparacion TEXT,
    EnfermedadesTratadas TEXT,
    -- Ornamental
    CaracteristicasEsteticas VARCHAR(255),
    UbicacionRecomendada VARCHAR(255),
    TipoJardineria VARCHAR(100),
    ColoracionEstacional TEXT,
    -- Artesanal
    TipoArtesania VARCHAR(150),
    TecnicasElaboracion TEXT,
    ComunidadesArtesanales VARCHAR(255),
    -- Agroforestal
    SistemaAgroforestal VARCHAR(100),
    BeneficiosAsociados TEXT,
    CultivosCompatibles VARCHAR(255),
    FuncionPrincipal VARCHAR(150),
    -- RestauracionEcologica
    EcosistemaObjetivo VARCHAR(150),
    FuncionEcologica TEXT,
    EspeciesAsociadas VARCHAR(255),
    TasaCrecimiento VARCHAR(50),
    -- CulturalCeremonial
    GrupoEtnico VARCHAR(100),
    TipoCeremonia VARCHAR(150),
    SignificadoCultural TEXT,
    -- Melifero
    TipoMiel VARCHAR(100),
    EpocaFloracion VARCHAR(100),
    CalidadPolen VARCHAR(50),
    AtraccionPolinizadores TEXT,
    -- ProteccionAmbiental
    TipoProteccion VARCHAR(100),
    BeneficiosAmbientales TEXT,
    ZonasAplicacion VARCHAR(255),
    CapacidadCapturaCarbon VARCHAR(100),
    -- Tintoreo
    ColorObtenido VARCHAR(100),
    MetodoExtraccion TEXT,
    UsosTintes VARCHAR(255),
    -- Oleaginoso
    TipoAceite VARCHAR(100),
    PropiedadesAceite TEXT,
    AplicacionesAceite VARCHAR(255),
    -- Biocombustible
    TipoBiocombustible VARCHAR(100),
    PoderCalorifico VARCHAR(100),
    RendimientoPorHectarea VARCHAR(100),
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- CuriosidadesArbol
CREATE TABLE CuriosidadesArbol (
    IDCuriosidad INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    Descripcion TEXT NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- InteraccionesEcologicas
CREATE TABLE InteraccionesEcologicas (
    IDInteraccion INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    TipoInteraccion VARCHAR(100),
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- TipoBosque
CREATE TABLE TipoBosque (
    IDTipoBosque INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100),
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Centro
CREATE TABLE Centro (
    IDCentro INT AUTO_INCREMENT PRIMARY KEY,
    NombreCentro VARCHAR(100),
    Direccion VARCHAR(255),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Arbol
CREATE TABLE Arbol (
    IDArbol INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    Centro INT NOT NULL,
    TipoBosque INT NOT NULL,
    Caracteristicas TEXT,
    ServiciosEcosistemicos TEXT,
    Imagen VARCHAR(255),
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Centro) REFERENCES Centro(IDCentro),
    FOREIGN KEY (TipoBosque) REFERENCES TipoBosque(IDTipoBosque),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- CodigoQR
CREATE TABLE CodigoQR (
    IDQR INT AUTO_INCREMENT PRIMARY KEY,
    Arbol INT NOT NULL,
    Codigo TEXT,
    Imagen LONGTEXT,
    FechaGeneracion DATETIME,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Arbol) REFERENCES Arbol(IDArbol),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);
-- Tabla: sugerencias
CREATE TABLE IF NOT EXISTS sugerencias (
  IDSugerencia int(11) NOT NULL AUTO_INCREMENT,
  Nombre varchar(100) NOT NULL,
  Email varchar(100) NOT NULL,
  Sugerencia text NOT NULL,
  Fecha datetime DEFAULT current_timestamp(),
  Estado int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (IDSugerencia),
  KEY Estado (Estado),
  CONSTRAINT sugerencias_ibfk_1 FOREIGN KEY (Estado) REFERENCES estado (IDEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: tokens_recuperacion
CREATE TABLE IF NOT EXISTS tokens_recuperacion (
  IDToken int(11) NOT NULL AUTO_INCREMENT,
  Usuario int(11) NOT NULL,
  Token varchar(100) NOT NULL,
  FechaExpiracion datetime NOT NULL,
  Estado int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (IDToken),
  KEY Usuario (Usuario),
  KEY Estado (Estado),
  CONSTRAINT tokens_recuperacion_ibfk_1 FOREIGN KEY (Usuario) REFERENCES Usuario (IDUsuario),
  CONSTRAINT tokens_recuperacion_ibfk_2 FOREIGN KEY (Estado) REFERENCES Estado (IDEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;