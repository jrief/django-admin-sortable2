const { build } = require('esbuild');
const buildOptions = require('yargs-parser')(process.argv.slice(2), {
  boolean: ['debug', 'sourcemap'],
});

build({
  entryPoints: ['client/admin-sortable2.ts'],
  bundle: true,
  minify: !buildOptions.debug,
  sourcemap: buildOptions.sourcemap,
  outfile: 'adminsortable2/static/adminsortable2/js/adminsortable2' + (buildOptions.debug ? '' : '.min') + '.js',
  plugins: [],
  target: ['es2020', 'chrome84', 'firefox84', 'safari14', 'edge84']
}).catch(() => process.exit(1));
