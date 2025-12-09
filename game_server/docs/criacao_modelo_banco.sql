CREATE DATABASE naval_libras

use naval_libras

--############# Creating Tables #############
create table usuario (
 id int AUTO_INCREMENT primary key,
 apelido varchar(7) not null
)

create table estado (
 id int AUTO_INCREMENT primary key,
 codigo varchar(15) not null -- 1=atacado,2=atingido,3=vazio
)

create table celula (
 id int AUTO_INCREMENT primary key,
 usuario_id int not null,
 indice_coluna int not null,
 indice_linha int not null,
 estado_id int not null,
 navio bit not null default 0,
 foreign key(usuario_id) references usuario(id),
 foreign key(estado_id) references estado(id)
)

create table rank (
 id int AUTO_INCREMENT primary key,
 usuario_id int not null,
 posicao int not null,
 foreign key(usuario_id) references usuario(id)
)

create table apelidos (
 id int AUTO_INCREMENT primary key,
 apelido varchar(5) not null
)

--############# Inserting Tables #############
insert into estado (codigo) 
values ('atingido'), ('vazio');

INSERT INTO `apelidos` (`apelido`) VALUES
('pingo'),
('zuzu'),
('tico'),
('bubu'),
('leco'),
('nino'),
('pipo'),
('teco'),
('zico'),
('mimo'),
('kiki'),
('fofo'),
('bibi'),
('dudu'),
('guga'),
('ruxo'),
('lulu'),
('neco'),
('zazu'),
('poxa'),
('tito'),
('sone'),
('vovo'),
('joca'),
('fufi'),
('popo'),
('caco'),
('xico'),
('zito'),
('mico'),
('riri'),
('lolo'),
('boro'),
('fufu'),
('peta'),
('jiji'),
('keko'),
('ralo'),
('nuno'),
('yoyo'),
('pepe'),
('sissi'),
('momo'),
('tobi'),
('rara'),
('bico'),
('zupu'),
('lupi'),
('mumu'),
('quico');

