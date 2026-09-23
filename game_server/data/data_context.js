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
            'select * from apelidos'
        );
        return rows;
    } catch (error) {
        console.error('Error fetching nicknames:', error);
        return { error: 'Erro ao conectar ao banco de dados', details: error.message };
    } finally {
        await conn.end();
    }
}

module.exports = {
    selectAllNickNames
};