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
    try{
        const conn = await conectar();
        const [rows] = await conn.query(
            'select * from apelidos where apelido not in (select apelido from usuario)'
        );
        console.log(rows);
        return rows;
    } catch (error) {
        console.error('Error fetching nicknames:', error);
        return { error: 'Erro ao conectar ao banco de dados', details: error.message };
    }
}

// selectAllNickNames()

// SELECT example
async function selectUsers() {
    try {
        const rows = await query('SELECT * FROM users');
        console.log(rows);
        return rows;
    } catch (error) {
        console.error('Error selecting users:', error);
        return { error: 'Erro ao selecionar usuários', details: error.message };
    }
}

// INSERT example
async function insertUser(name, email) {
    try {
        const result = await query(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            [name, email]
        );
        console.log('User inserted:', result.insertId);
        return result;
    } catch (error) {
        console.error('Error inserting user:', error);
        return { error: 'Erro ao inserir usuário', details: error.message };
    }
}

// UPDATE example
async function updateUser(id, name, email) {
    try {
        const result = await query(
            'UPDATE users SET name = ?, email = ? WHERE id = ?',
            [name, email, id]
        );
        console.log('User updated:', result.affectedRows);
        return result;
    } catch (error) {
        console.error('Error updating user:', error);
        return { error: 'Erro ao atualizar usuário', details: error.message };
    }
}

module.exports = {
    selectAllNickNames,
    selectUsers,
    insertUser,
    updateUser,
};