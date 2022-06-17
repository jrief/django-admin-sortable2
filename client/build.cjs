const { build } = require('esbuild');

build({
  entryPoints: ['client/admin-sortable2.ts'],
  bundle: true,
  minify: false,
  outfile: 'adminsortable2/static/adminsortable2/js/adminsortable2.js',
  plugins: [],
  sourcemap: true,
  target: ['es2020', 'chrome84', 'firefox84', 'safari14', 'edge84']
}).catch(() => process.exit(1));
