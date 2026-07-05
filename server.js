const http = require('http');
const VERSION = process.env.APP_VERSION || 'blue';
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, {'Content-Type':'application/json'});
    res.end(JSON.stringify({status:'ok', version:VERSION}));
  } else if (req.url === '/api/data') {
    res.writeHead(200, {'Content-Type':'application/json'});
    res.end(JSON.stringify({message:'Hello from DevOps assignment API', time:new Date()}));
  } else {
    res.writeHead(200, {'Content-Type':'text/html'});
    res.end('<h1>DevOps Assignment App</h1><p>Version: ' + VERSION + '</p><p>Deployed via CI/CD pipeline</p>');
  }
});
server.listen(3000, () => console.log('App running on 3000, version: ' + VERSION));
