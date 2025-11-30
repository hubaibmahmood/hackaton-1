const fs = require('fs');
const path = require('path');

const ASSETS_DIR = path.join(__dirname, '../book/static');
const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB
const MAX_TOTAL_SIZE = 100 * 1024 * 1024; // 100MB

let totalSize = 0;
let hasError = false;

function scanDir(dir) {
  if (!fs.existsSync(dir)) return;
  
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stats = fs.statSync(filePath);

    if (stats.isDirectory()) {
      scanDir(filePath);
    } else {
      totalSize += stats.size;
      if (stats.size > MAX_FILE_SIZE) {
        console.error(`❌ File too large: ${path.relative(path.join(__dirname, '..'), filePath)} (${(stats.size / 1024 / 1024).toFixed(2)} MB > 2 MB)`);
        hasError = true;
      }
    }
  });
}

console.log(`🔍 Scanning assets in ${ASSETS_DIR}...`);
scanDir(ASSETS_DIR);

console.log(`📊 Total asset size: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);

if (totalSize > MAX_TOTAL_SIZE) {
  console.error(`❌ Total size limit exceeded: ${(totalSize / 1024 / 1024).toFixed(2)} MB > 100 MB`);
  hasError = true;
}

if (hasError) {
  console.error('❌ Asset validation failed.');
  process.exit(1);
} else {
  console.log('✅ Asset validation passed.');
}
