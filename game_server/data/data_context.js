const mysql = require('mysql2/promise');
require('dotenv').config();

async function conectar() {
    return mysql.createConnection({
        host: process.env.DATABASE_HOST,
        user: process.env.DATABASE_USER,
        password: process.env.DATABASE_PASSWORD,
        database: process.env.DATABASE_NAME,
        port: process.env.DATABASE_PORT
    });
}

async function selectAllNickNames() {
    const conn = await conectar();
    try{
        const [rows] = await conn.query(
            'select * from apelidos where apelido not in (select apelido from usuario)'
        );
        return rows;
    } catch (error) {
        console.error('Error fetching nicknames:', error);
        return { error: 'Erro ao conectar ao banco de dados', details: error.message };
    } finally {
        conn.end();
    }
}

async function insertUser(nickname, time) {
    const conn = await conectar();
    try {
        const result = await conn.query(
            'INSERT INTO usuario (apelido, tempo) VALUES (?, ?)',
            [nickname, time]
        );
        return result;
    } catch (error) {
        console.error('Error inserting user:', error);
        return { error: 'Erro ao inserir usuário', details: error.message };
    } finally {
        conn.end();
    }
}

async function insertCell(userId, cell) {
    const conn = await conectar();
    try {
        const columnIndex = GetColumnIndex(cell.coluna);
        const result = await conn.query(
            'INSERT INTO celula (usuario_id, indice_coluna, indice_linha, estado_id, navio) VALUES(?, ?, ?, ?, ?)',
            [userId, columnIndex, cell.linha, cell.estadoId, cell.navio]
        );
        console.log('Cell inserted:', result[0].insertId);
        return result;
    } catch (error) {
        console.error('Error inserting cell:', error);
        return { error: 'Erro ao inserir cell', details: error.message };
    } finally {
        conn.end();
    }
}

async function getUserByNickname(nickName) {
    const conn = await conectar();
    try{
        const [rows] = await conn.query(
            'select * from usuario where apelido = ?',
            [nickName]
        );
        console.log(rows);
        return rows;
    } catch (error) {
        console.error('Error fetching nicknames:', error);
        return { error: 'Erro ao conectar ao banco de dados', details: error.message };
    } finally {
        conn.end();
    }
}

async function getRank() {
    const conn = await conectar();
    try{
        const [rows] = await conn.query(
            'select ' + 
            '    u.apelido,  ' +
            '    u.tempo,  ' +
            '    count(c.id) as total_atingido  ' +
            'from celula c  ' +
            'join usuario u on u.id = c.usuario_id  ' + 
            'where c.navio = true and c.estado_id = 1  ' +
            'group by u.apelido, u.tempo ' +
            'order by 3 desc, 2 asc '
        );
        console.log(rows);
        return rows;
    } catch (error) {
        console.error('Error fetching nicknames:', error);
        return { error: 'Erro ao conectar ao banco de dados', details: error.message };
    } finally {
        conn.end();
    }
}

function GetColumnIndex(column){
    const map = new Map([
        ['A', 1],
        ["E", 2],
        ["I", 3],
        ["O", 4],
        ["U", 5]
    ]);
    console.log(map.get(column));
    return map.get(column);
}

function GetColumnValue(column){
    const map = new Map([
        [1, "A"],
        [2, "E"],
        [3, "I"],
        [4, "O"],
        [5, "U"]
    ]);
    console.log(map.get(column));
    return map.get(column);
}

module.exports = {
    selectAllNickNames,
    getUserByNickname,
    insertUser,
    insertCell,
    getRank
};