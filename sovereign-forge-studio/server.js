const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

const PORT = 3000;
const WORKSPACE_ROOT = path.join(__dirname, '..');
const BACKUPS_DIR = path.join(__dirname, '.backups');

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml'
};

// Ensure backups directory exists
if (!fs.existsSync(BACKUPS_DIR)) {
  fs.mkdirSync(BACKUPS_DIR, { recursive: true });
}

// Helper: Safely resolve paths inside the workspace root
function resolveSafePath(userPath) {
  const resolved = path.resolve(WORKSPACE_ROOT, userPath);
  if (!resolved.startsWith(WORKSPACE_ROOT)) {
    return null;
  }
  return resolved;
}

// Helper: Recursive Directory Scanner
function scanDirectoryRecursive(dirPath, relativeDir = '') {
  let results = [];
  
  // Folders to ignore during scanning
  const IGNORE_FOLDERS = ['.git', 'node_modules', '.dfx', 'dist', 'build', 'target', '.backups', 'bin'];
  
  try {
    const list = fs.readdirSync(dirPath);
    for (const file of list) {
      const fileFullPath = path.join(dirPath, file);
      const fileRelativePath = relativeDir ? `${relativeDir}/${file}` : file;
      const stat = fs.statSync(fileFullPath);
      
      if (stat.isDirectory()) {
        if (IGNORE_FOLDERS.includes(file)) continue;
        results.push({ name: file, isDir: true, path: fileRelativePath });
        results = results.concat(scanDirectoryRecursive(fileFullPath, fileRelativePath));
      } else {
        results.push({ name: file, isDir: false, path: fileRelativePath });
      }
    }
  } catch (err) {
    console.error(`Error scanning directory: ${dirPath}`, err);
  }
  
  return results;
}

// Helper: Get Shell Configuration
function getShellConfig() {
  const configPath = path.join(__dirname, 'config.json');
  let shell = 'powershell.exe';
  let shellArgs = ['-NoProfile', '-NonInteractive', '-Command'];

  // Read config.json override if it exists
  if (fs.existsSync(configPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (data.shell) shell = data.shell;
      if (data.shellArgs) shellArgs = data.shellArgs;
      return { shell, shellArgs };
    } catch (e) {
      console.error("Error reading config.json, using defaults.", e);
    }
  }

  // Auto-detect shell by process platform
  if (process.platform !== 'win32') {
    // Unix/Linux/macOS defaults
    shell = '/bin/bash';
    if (!fs.existsSync(shell)) {
      shell = '/bin/sh';
    }
    shellArgs = ['-c'];
  }

  return { shell, shellArgs };
}

const server = http.createServer((req, res) => {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.statusCode = 204;
    res.end();
    return;
  }

  console.log(`[REAL IDE] ${req.method} ${req.url}`);

  // ── API: Get Git Status ──
  if (req.url === '/api/git-status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    try {
      const output = execSync('git status -s', { cwd: WORKSPACE_ROOT }).toString();
      const changes = output.split('\n').filter(Boolean).map(line => {
        const status = line.substring(0, 2).trim();
        const filePath = line.substring(3).trim();
        return { path: filePath, status };
      });
      res.end(JSON.stringify(changes));
    } catch (e) {
      res.end(JSON.stringify([]));
    }
    return;
  }

  // ── API: Get Git Logs ──
  if (req.url === '/api/git-log') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    try {
      const output = execSync('git log -n 12 --pretty=format:"%h - %s"', { cwd: WORKSPACE_ROOT }).toString();
      const commits = output.split('\n').filter(Boolean).map(line => {
        const parts = line.split(' - ');
        const hash = parts[0];
        const msg = parts.slice(1).join(' - ');
        const branch = hash.charCodeAt(0) % 3;
        return { hash, msg, branch };
      });
      res.end(JSON.stringify(commits));
    } catch (e) {
      res.end(JSON.stringify([]));
    }
    return;
  }

  // ── API: Recursive List Workspace Files ──
  if (req.url === '/api/files') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    const files = scanDirectoryRecursive(WORKSPACE_ROOT);
    res.end(JSON.stringify(files));
    return;
  }

  // ── API: Read File Content ──
  if (req.url.startsWith('/api/file?')) {
    const urlObj = new URL(req.url, `http://${req.headers.host}`);
    const filePathParam = urlObj.searchParams.get('path');
    const safePath = resolveSafePath(filePathParam);

    if (!safePath || !fs.existsSync(safePath) || !fs.statSync(safePath).isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end("File Not Found");
      return;
    }

    res.writeHead(200, { 'Content-Type': 'text/plain' });
    fs.createReadStream(safePath).pipe(res);
    return;
  }

  // ── API: Save File Content with Backup ──
  if (req.url === '/api/file' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const safePath = resolveSafePath(payload.path);
        
        if (!safePath) {
          res.writeHead(400, { 'Content-Type': 'text/plain' });
          res.end("Bad Request: Unauthorized path");
          return;
        }

        let backupPath = null;

        // Perform file backup if it already exists
        if (fs.existsSync(safePath)) {
          const timestamp = new Date().toISOString()
            .replace(/[-:]/g, '')
            .replace(/\..+/, '')
            .replace('T', '_'); // Format: YYYYMMDD_HHMMSS
            
          const ext = path.extname(safePath);
          const baseName = path.basename(safePath, ext);
          const backupFileName = `${baseName}_${timestamp}${ext}`;
          
          backupPath = path.join(BACKUPS_DIR, backupFileName);
          fs.copyFileSync(safePath, backupPath);
          console.log(`[BACKUP] Created: ${backupFileName}`);
        }

        fs.writeFileSync(safePath, payload.content, 'utf8');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: true, 
          path: payload.path,
          backupCreated: backupPath ? path.basename(backupPath) : null 
        }));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Internal Server Error: ${err.message}`);
      }
    });
    return;
  }

  // ── API: Live Run Command (SSE with Auto-detected shell) ──
  if (req.url.startsWith('/api/run-command')) {
    const urlObj = new URL(req.url, `http://${req.headers.host}`);
    const command = urlObj.searchParams.get('cmd');

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    const sendEvent = (event, data) => {
      res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
    };

    if (!command) {
      sendEvent('error', 'No command provided');
      res.end();
      return;
    }

    const { shell, shellArgs } = getShellConfig();
    const finalArgs = [...shellArgs, command];

    sendEvent('log', { type: 'cmd', text: `Spawning shell: ${shell} ${shellArgs.join(' ')} "${command}"` });

    const proc = spawn(shell, finalArgs, { cwd: WORKSPACE_ROOT });

    proc.stdout.on('data', (data) => {
      sendEvent('log', { type: 'success', text: data.toString() });
    });

    proc.stderr.on('data', (data) => {
      sendEvent('log', { type: 'warn', text: data.toString() });
    });

    proc.on('close', (code) => {
      sendEvent('log', { type: 'info', text: `Process exited with code ${code}` });
      sendEvent('done', { code });
      res.end();
    });

    req.on('close', () => {
      proc.kill();
    });
    return;
  }

  // Static Asset Serving
  let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
  if (!filePath.startsWith(__dirname)) {
    res.statusCode = 403;
    res.end('Access Denied');
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.statusCode = 404;
        res.end('404 Not Found');
      } else {
        res.statusCode = 500;
        res.end(`Internal Error: ${err.code}`);
      }
    } else {
      res.statusCode = 200;
      res.setHeader('Content-Type', contentType);
      res.end(content);
    }
  });
});

server.listen(PORT, () => {
  console.log('=====================================================');
  console.log(`  Sovereign Forge Studio (Real-IDE Version) active!`);
  console.log(`  Access URL: http://localhost:${PORT}`);
  console.log('=====================================================');
});
