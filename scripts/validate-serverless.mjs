import fs from 'fs';

const requiredFiles = [
  'api/llm.js',
  'vercel.json'
];

for (const file of requiredFiles) {
  if (!fs.existsSync(file)) {
    console.error(`missing_required_file:${file}`);
    process.exit(1);
  }
}

console.log('serverless_validation_ok');
