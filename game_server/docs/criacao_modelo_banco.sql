CREATE DATABASE naval_libras

use naval_libras

--############# Creating user #############
--Step 1
CREATE USER 'naval_libras'@'localhost' IDENTIFIED BY 'naval_libras';

--Step 2
GRANT ALL PRIVILEGES ON *.* TO 'naval_libras'@'localhost';

--Step 3
FLUSH PRIVILEGES;

--############# Creating Tables #############
create table apelidos (
 id int AUTO_INCREMENT primary key,
 apelido varchar(5) not null
)

--############# Inserting Tables #############
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


INSERT INTO `apelidos` (`apelido`) VALUES
('lino'),
('toto'),
('zapi'),
('banz'),
('fifi'),
('mona'),
('lito'),
('biso'),
('tanu'),
('roro'),
('buba'),
('lero'),
('peka'),
('nixu'),
('zaro'),
('fexo'),
('meli'),
('bito'),
('julo'),
('ruba'),
('tiri'),
('xara'),
('joni'),
('miri'),
('zoku'),
('lamu'),
('topo'),
('piki'),
('zanu'),
('rero'),
('tupi'),
('badi'),
('jaxi'),
('lapi'),
('fano'),
('dimo'),
('kiko'),
('xoni'),
('pomo'),
('tuni'),
('luki'),
('zebo'),
('mini'),
('rali'),
('jilo'),
('paxi'),
('mabu'),
('tavi'),
('limo');


