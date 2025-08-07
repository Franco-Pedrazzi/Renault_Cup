DROP database IF EXISTS RenaultCup;
create database RenaultCup;
use RenaultCup;
DROP TABLE IF EXISTS `Equipo`;
		
CREATE TABLE `Equipo` (
  `id_equipo` int AUTO_INCREMENT,
  `Deporte` VARCHAR(10) NULL DEFAULT '-',
  `Categoria` VARCHAR(10) NULL DEFAULT '-',
  `Sexo` VARCHAR(10) NULL DEFAULT '-',
  `Colegio` VARCHAR(50) NULL DEFAULT '-' COMMENT 'Agregar A o B si los demás campos son iguales',
  PRIMARY KEY (`id_equipo`)
);

CREATE TABLE `jugador` (
  `id_jugador` int AUTO_INCREMENT,
  `id_equipo` int NULL DEFAULT NULL,
  `Nombre` VARCHAR(50) NULL DEFAULT '-',
  `DNI` Varchar(10) NULL DEFAULT NULL,
  `Telefono` Varchar(15) NULL DEFAULT NULL,
  `Email` VARCHAR(40) NULL DEFAULT NULL,
  `Comida_especial` VARCHAR(3) NULL DEFAULT 'N',
  `Fecha_nacimiento` DATE NULL DEFAULT NULL,
  `Infracciones` VARCHAR(10) NULL DEFAULT '0',
  PRIMARY KEY (`id_jugador`)
);
		
CREATE TABLE `Responsable` (
  `id_profesor`int AUTO_INCREMENT,
  `id_equipo` int NULL DEFAULT NULL,
  `Nombre` VARCHAR(50) NULL DEFAULT '-',
  `DNI` Varchar(10) NULL DEFAULT NULL,
  `Telefono` Varchar(15) NULL DEFAULT NULL,
  `Email` VARCHAR(40) NULL DEFAULT NULL,
  `Comida_especial` VARCHAR(3) NULL DEFAULT 'N',
  `Fecha_nacimiento` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`id_profesor`)
);

		
CREATE TABLE `Partido` (
  `id_partido`int AUTO_INCREMENT,
  `Deporte` VARCHAR(1) NULL DEFAULT NULL,
  `Categoria` VARCHAR(3) NULL DEFAULT NULL,
  `Sexo` VARCHAR(1) NULL DEFAULT NULL,
  `Arbitro` int NULL DEFAULT NULL,
  `Planillero` int NULL DEFAULT NULL,
  `Equipo_1` int NULL DEFAULT NULL,
  `Equipo_2` int NULL DEFAULT NULL,
  `Fase` VARCHAR(25) NULL DEFAULT NULL,
  `Horario_inicio` TIME NULL DEFAULT NULL,
  `Horario_final` TIME NULL DEFAULT NULL,
  PRIMARY KEY (`id_partido`)
);

CREATE TABLE `Resultado` (
  `id_partido` int AUTO_INCREMENT,
  `Puntaje_e1` int NULL DEFAULT 0,
  `Puntaje_e2` int NULL DEFAULT 0,
  `Resultado` int NULL DEFAULT NULL COMMENT '0 no jugado, 3 empate',
  `Infracciones_e1` int(3) NULL DEFAULT NULL,
  `Infracciones_e2` int(3) NULL DEFAULT NULL,
  PRIMARY KEY (`id_partido`)
);

		
CREATE TABLE `Cuenta_habilitada` (
  `Nombre` VARCHAR(40) not NULL,
  `Email` VARCHAR(40) not NULL,
  `Contraseña` VARCHAR(200) not NULL,
  `rango`  VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`Email`)
);

		
CREATE TABLE `Staff` (
  `id_staff` int AUTO_INCREMENT,
  `Nombre` VARCHAR(40) NULL DEFAULT NULL,
  `DNI` int(8) NULL DEFAULT NULL,
  `Telefono` int(20) NULL DEFAULT NULL,
  `Email` VARCHAR(40) NULL DEFAULT NULL,
  `Trabajo` VARCHAR(15) NULL DEFAULT NULL,
  `Sector` VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`id_staff`)
);

CREATE TABLE `Verificacion` (
  `id` int not NULL auto_increment,
  `Email` VARCHAR(40) not NULL,
  `codigo` VARCHAR(20) not NULL,
  `contra_codificada`  VARCHAR(200) not null,
  `nombre` VARCHAR(40) not NULL,
  `rango` VARCHAR(20) not NULL,
  PRIMARY KEY (`id`)
);

ALTER TABLE `jugador` ADD FOREIGN KEY (id_equipo) REFERENCES `Equipo` (`id_equipo`);
ALTER TABLE `Responsable` ADD FOREIGN KEY (id_equipo) REFERENCES `Equipo` (`id_equipo`);
ALTER TABLE `Partido` ADD FOREIGN KEY (Arbitro) REFERENCES `Staff` (`id_staff`);
ALTER TABLE `Partido` ADD FOREIGN KEY (Planillero) REFERENCES `Staff` (`id_staff`);
ALTER TABLE `Partido` ADD FOREIGN KEY (Equipo_1) REFERENCES `Equipo` (`id_equipo`);
ALTER TABLE `Partido` ADD FOREIGN KEY (Equipo_2) REFERENCES `Equipo` (`id_equipo`);
ALTER TABLE `Resultado` ADD FOREIGN KEY (id_partido) REFERENCES `Partido` (`id_partido`);

-- ---
-- Table Properties
-- ---

-- ALTER TABLE `Equipo` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `jugador` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `Responsable` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `Partido` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `Resultado` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `Cuenta_habilitada` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `Staff` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ---
-- Test Data
-- ---

-- INSERT INTO `Equipo` (`id_equipo`,`Deporte`,`Categoria`,`Sexo`,`Colegio`) VALUES
-- ('','','','','');
-- INSERT INTO `jugador` (`id_jugador`,`id_equipo`,`Nombre`,`DNI`,`Telefono`,`Email`,`Comida_especial`,`Fecha_nacimiento`,`Infracciones`) VALUES
-- ('','','','','','','','','');
-- INSERT INTO `Responsable` (`id_profesor`,`id_equipo`,`Nombre`,`DNI`,`Telefono`,`Email`,`Comida_especial`) VALUES
-- ('','','','','','','');
-- INSERT INTO `Partido` (`id_partido`,`Deporte`,`Categoria`,`Sexo`,`id_staff`,`Planillero`,`Equipo_1`,`Equipo_2`,`Fase`,`Horario_inicio`,`Horario_final`) VALUES
-- ('','','','','','','','','','','');
-- INSERT INTO `Resultado` (`id_partido`,`Puntaje_e1`,`Puntaje_e2`,`Resultado`,`Infracciones_e1`,`Infracciones_e2`) VALUES
-- ('','','','','','');
-- INSERT INTO `Cuenta_habilitada` (`id_cuenta`,`Nombre`,`Email`,`Contraseña`) VALUES
-- ('','','','');
-- INSERT INTO `Staff` (`id_staff`,`Nombre`,`DNI`,`Telefono`,`Email`,`Trabajo`,`Sector`) VALUES
-- ('','','','','','','');

insert into Equipo (Deporte,Categoria,Sexo,Colegio) values("a","b","c","b");
select * from Equipo;