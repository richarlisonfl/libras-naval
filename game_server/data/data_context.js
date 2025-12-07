const mysql = require('mysql2/promise');

const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: 'your_password',
    database: 'your_database',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
});

// SELECT example
async function selectUsers() {
    const connection = await pool.getConnection();
    try {
        const [rows] = await connection.query('SELECT * FROM users');
        console.log(rows);
        return rows;
    } finally {
        connection.release();
    }
}

// INSERT example
async function insertUser(name, email) {
    const connection = await pool.getConnection();
    try {
        const [result] = await connection.query(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            [name, email]
        );
        console.log('User inserted:', result.insertId);
        return result;
    } finally {
        connection.release();
    }
}

// UPDATE example
async function updateUser(id, name, email) {
    const connection = await pool.getConnection();
    try {
        const [result] = await connection.query(
            'UPDATE users SET name = ?, email = ? WHERE id = ?',
            [name, email, id]
        );
        console.log('User updated:', result.affectedRows);
        return result;
    } finally {
        connection.release();
    }
}

module.exports = {
    pool,
    selectUsers,
    insertUser,
    updateUser,
};