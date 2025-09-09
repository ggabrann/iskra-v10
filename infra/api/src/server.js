import express from 'express'; import cors from 'cors'; import bodyParser from 'body-parser';
import { createServer } from 'http'; import { WebSocketServer } from 'ws'; import routes from './routes.js';
const app=express(); app.use(cors()); app.use(bodyParser.json());
const server=createServer(app); const wss=new WebSocketServer({server});
wss.on('connection', ws=>ws.send(JSON.stringify({event:'hello'})));
routes(app,wss);
const PORT=process.env.API_PORT||7070; server.listen(PORT,()=>console.log('[API] listening on',PORT));
