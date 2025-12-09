const express = require('express');
const path = require('path');
const context = require('./data/data_context');

const app = express();
const PORT = 3000;

// Servir arquivos estáticos da pasta "public"
app.use(express.static(path.join(__dirname, '../game_interface')));

// Rota padrão
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../game_interface', 'index.html'));
});

app.get('/get-nickname', async (req, res) => {
  res.send({ nicknames: await context.selectAllNickNames()});
})

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});