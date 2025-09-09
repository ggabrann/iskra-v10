export const broadcast=(wss,msg)=>wss.clients.forEach(c=>c.readyState===1&&c.send(JSON.stringify(msg)));
