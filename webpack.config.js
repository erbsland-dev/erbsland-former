const path = require('path');

module.exports = [
    {
        mode: 'production',
        resolve: {
            modules: ['./node_modules']
        },
        entry: {
            'index': './design/static/design/js_src/index.js',
        },
        devtool: 'source-map',
        output: {
            filename: '[name].bundle.js',
            path: path.resolve(__dirname, 'design/static/design/js'),
            library: 'Design',
            clean: true,
        }
    },
    {
        mode: 'development',
        resolve: {
            modules: ['./node_modules']
        },
        entry: {
            'editor': {
                import: './design/static/design/js_src/editor.js',
            },
        },
        devtool: 'source-map',
        output: {
            filename: '[name].bundle.js',
            path: path.resolve(__dirname, 'design/static/design/js'),
            library: 'Editor',
            clean: false
        }
    }
];
