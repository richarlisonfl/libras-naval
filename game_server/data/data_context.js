const mysql = require('mysql2/promise');

async function conectar() {
  try {
    const conn = await mysql.createConnection({
      host: 'localhost',
      user: 'seu_usuario',
      password: 'sua_senha',
      database: 'nome_do_banco',
      port: 3306
    });

    console.log('Conectado ao MariaDB!');

    const [rows] = await conn.query('SELECT NOW() AS data');
    console.log(rows);

    await conn.end();
  } catch (err) {
    console.error('Erro:', err);
  }
}

//conectar();

async function selectAllNickNames() {
    const conn = await mysql.createConnection({
        host: '127.0.0.1',
        user: 'seu_usuario',
        password: 'sua_senha',
        database: 'nome_do_banco',
        port: 3306
    });
    try {

        const rows = await conn.query(
            'select * from apelidos where apelido not in (select apelido from usuario)'
        );
        console.log(rows);
        return rows;
    } catch (error) {
        console.error('Error fetching nicknames:', error);
        return { error: 'Erro ao conectar ao banco de dados', details: error.message };
    } finally {
        await conn.end();
    }
}

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