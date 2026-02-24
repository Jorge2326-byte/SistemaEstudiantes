-- Crear base de datos y tabla para SistemaEstudiantes
CREATE DATABASE IF NOT EXISTS sistema_estudiantes
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE sistema_estudiantes;

CREATE TABLE IF NOT EXISTS estudiantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  correo VARCHAR(100) NOT NULL
);