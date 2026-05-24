import { execSync } from 'child_process';

const file = process.argv[2];

if (!file) {
  console.error('usage: npm run ipfs:pin-gguf -- <path-to-model.gguf>');
  process.exit(1);
}

try {
  const result = execSync(`ipfs add -Q ${file}`, {
    encoding: 'utf8'
  }).trim();

  console.log(JSON.stringify({
    ok: true,
    cid: result
  }, null, 2));
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
