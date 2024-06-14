const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = [
    {
        mode: 'production',
        resolve: {
            modules: ['./node_modules']
        },
        entry: {
            'design': {
                import: './design/style/js/design.js',
            },
            'editor': {
                import: './design/style/js/editor.js',
            },
        },
        //devtool: 'source-map',
        output: {
            filename: '[name].bundle.js',
            path: path.resolve(__dirname, 'design/static/design/js'),
            library: {
                name: '[name]',
                type: 'var',
            },
            clean: true,
        }
    },
    {
        mode: 'production',
        resolve: {
            modules: ['./node_modules']
        },
        entry: {
            'style': './design/style/css/style.scss'
        },
        output: {
            filename: '[name].css.js',
            path: path.resolve(__dirname, 'design/static/design/css'),
        },
        module: {
            rules: [
                {
                    test: /\.scss$/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        'css-loader',
                        'sass-loader'
                    ],
                },
            ],
        },
        plugins: [
            new MiniCssExtractPlugin({
                filename: '[name].min.css',
            }),
        ],
        optimization: {
            minimizer: [
                `...`,
                new CssMinimizerPlugin(),
            ],
        },
    }
];
