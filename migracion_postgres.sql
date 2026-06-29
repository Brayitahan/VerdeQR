CREATE TABLE IF NOT EXISTS Estado (
    IDEstado SERIAL PRIMARY KEY,
    NombreEstado VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(100)
);

INSERT INTO Estado (IDEstado, NombreEstado, Descripcion) VALUES (1, 'Activo', 'Registro activo'), (2, 'Inactivo', 'Registro inactivo');

CREATE TABLE IF NOT EXISTS Usuario (
    IDUsuario SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) NOT NULL,
    Telefono VARCHAR(20),
    Imagen VARCHAR(255),
    Contrasena VARCHAR(255) NOT NULL,
    Estado INTEGER NOT NULL DEFAULT 1,
    FechaRegistro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS Rol (
    IDRol SERIAL PRIMARY KEY,
    NombreRol VARCHAR(50) NOT NULL
);

INSERT INTO Rol (NombreRol) VALUES ('Administrador'), ('Visitante');

CREATE TABLE IF NOT EXISTS UsuarioRol (
    IDUsuarioRol SERIAL PRIMARY KEY,
    Usuario INTEGER NOT NULL,
    Rol INTEGER NOT NULL,
    FOREIGN KEY (Usuario) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (Rol) REFERENCES Rol(IDRol)
);

CREATE TABLE IF NOT EXISTS Especie (
    IDEspecie SERIAL PRIMARY KEY,
    NombreCientifico VARCHAR(150) NOT NULL,
    NombreVulgar VARCHAR(150) NOT NULL,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS UsoArbol (
    IDUso SERIAL PRIMARY KEY,
    Especie INTEGER NOT NULL,
    Nombre VARCHAR(150),
    Categoria VARCHAR(50) NOT NULL,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS DetalleUso (
    IDDetalle SERIAL PRIMARY KEY,
    Uso INTEGER NOT NULL,
    Estado INTEGER NOT NULL DEFAULT 1,
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

CREATE TABLE IF NOT EXISTS CuriosidadesArbol (
    IDCuriosidad SERIAL PRIMARY KEY,
    Especie INTEGER NOT NULL,
    Descripcion TEXT NOT NULL,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS InteraccionesEcologicas (
    IDInteraccion SERIAL PRIMARY KEY,
    Especie INTEGER NOT NULL,
    TipoInteraccion VARCHAR(100),
    Descripcion TEXT,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS TipoBosque (
    IDTipoBosque SERIAL PRIMARY KEY,
    Nombre VARCHAR(100),
    Descripcion TEXT,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS Centro (
    IDCentro SERIAL PRIMARY KEY,
    NombreCentro VARCHAR(100),
    Direccion VARCHAR(255),
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS Arbol (
    IDArbol SERIAL PRIMARY KEY,
    Especie INTEGER NOT NULL,
    Centro INTEGER NOT NULL,
    TipoBosque INTEGER NOT NULL,
    Caracteristicas TEXT,
    ServiciosEcosistemicos TEXT,
    Imagen VARCHAR(255),
    Descripcion TEXT,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Centro) REFERENCES Centro(IDCentro),
    FOREIGN KEY (TipoBosque) REFERENCES TipoBosque(IDTipoBosque),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS CodigoQR (
    IDQR SERIAL PRIMARY KEY,
    Arbol INTEGER NOT NULL,
    Codigo TEXT,
    Imagen TEXT,
    FechaGeneracion TIMESTAMP,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Arbol) REFERENCES Arbol(IDArbol),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS sugerencias (
    IDSugerencia SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Sugerencia TEXT NOT NULL,
    Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

CREATE TABLE IF NOT EXISTS tokens_recuperacion (
    IDToken SERIAL PRIMARY KEY,
    Usuario INTEGER NOT NULL,
    Token VARCHAR(100) NOT NULL,
    FechaExpiracion TIMESTAMP NOT NULL,
    Estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (Usuario) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);
