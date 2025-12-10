require('dotenv').config();
const express = require('express');
const path = require('path');
const context = require('./data/data_context');
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());
const PORT = 3000;

// Servir arquivos estáticos da pasta "public"
app.use(express.static(path.join(__dirname, '../game_interface')));

// Rota padrão
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../game_interface', 'index.html'));
});

app.get('/get-nickname', async (req, res) => {
  res.send({ nicknames: await context.selectAllNickNames()});
  res.status(200)
})

app.post('/save-game', async (req, res) => {
  try{
    console.log(req.body)
    const user = await context.getUserByNickname(req.body.nickname);

    let nickname = req.body.nickname
    if (user.length != 0)
    {
      res.sendStatus(200)
      return;
    }

    const userResult = await context.insertUser(nickname);

    for (let cell of req.body.cells)
    {
      await context.insertCell(userResult[0].insertId, cell);
    }

    res.sendStatus(200)
  } catch (error) {
    res.statusCode = 400;
    res.body = error;
  }
})

app.get('/get-rank', async (req,res) => {
  try {
      res.send({ rank: await context.getRank()});
  res.status(200)
  } catch (error) {
    res.statusCode = 400;
    res.body = error;
  }
})

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});