const { spawn } = require('child_process');
const path = require('path');

const services = [
  { name: 'API GATEWAY', folder: 'APIGateway_Microservice', file: 'index.js', color: '\x1b[36m' },     // Cyan
  { name: 'REGISTRATION', folder: 'Registration_Microservice', file: 'index.js', color: '\x1b[32m' }, // Green
  { name: 'LOGIN-AUTH', folder: 'Login_Microservice', file: 'index.js', color: '\x1b[33m' },         // Yellow
  { name: 'ADMIN-SVC', folder: 'Admin_Microservice', file: 'index.js', color: '\x1b[35m' },          // Magenta
  { name: 'USER-SVC', folder: 'User_Microservice', file: 'index.js', color: '\x1b[34m' }             // Blue
];

const resetColor = '\x1b[0m';

console.log('========================================================================');
console.log(' Starting Central Identity & User Management Platform (5 Microservices)');
console.log('========================================================================');

const runningProcesses = [];

services.forEach(svc => {
  const filePath = path.join(__dirname, svc.folder, svc.file);
  const child = spawn(process.execPath, [filePath], {
    cwd: path.join(__dirname, svc.folder),
    env: { ...process.env, PORT: undefined }
  });

  child.stdout.on('data', data => {
    const lines = data.toString().trim().split('\n');
    lines.forEach(line => {
      if (line.trim()) {
        console.log(`${svc.color}[${svc.name}]${resetColor} ${line}`);
      }
    });
  });

  child.stderr.on('data', data => {
    const lines = data.toString().trim().split('\n');
    lines.forEach(line => {
      if (line.trim()) {
        console.error(`${svc.color}[${svc.name} ERROR]${resetColor} ${line}`);
      }
    });
  });

  child.on('close', code => {
    console.log(`${svc.color}[${svc.name}]${resetColor} Exited with code ${code}`);
  });

  runningProcesses.push(child);
});

process.on('SIGINT', () => {
  console.log('\nGracefully shutting down all microservices...');
  runningProcesses.forEach(proc => proc.kill());
  process.exit();
});

process.on('exit', () => {
  runningProcesses.forEach(proc => proc.kill());
});
