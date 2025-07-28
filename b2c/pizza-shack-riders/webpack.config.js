/**
 * Copyright (c) 2024, WSO2 LLC. (http://www.wso2.com).
 *
 * WSO2 LLC. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

require("dotenv").config();
const HtmlWebpackPlugin = require("html-webpack-plugin");
const path = require("path");
const { findPort } = require("dev-server-ports");
const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const HOST = process.env.HOST || "localhost";
const DEFAULT_PORT = process.env.PORT || 3000;
const devServerHostCheckDisabled =
    process.env.DISABLE_DEV_SERVER_HOST_CHECK === "true";
const https = process.env.HTTPS === "true";
const baseUrl = process.env.REACT_APP_BASE_URL || "/";

const envFile = ".env";
const envPath = path.resolve(__dirname, envFile);
const envVars = require('dotenv').config({ path: envPath }).parsed || {};

const generatePortInUsePrompt = () => {
    return `Be sure to update the following configurations if you proceed with the port change.

    1. Update the "PORT" in ".env" file in the app root.
    2. Update the signInRedirectURL & signOutRedirectURL in "src/runtime-config.json".
    3. Go to the WSO2 Identity server/Asgardeo console and navigate to the protocol tab of your application:
        - Update the Authorized Redirect URL.
        - Update the Allowed Origins.
`;
};

module.exports = async (env) => {
    const PORT = await findPort(DEFAULT_PORT, HOST, false, {
        extensions: {
            BEFORE_getProcessTerminationMessage: () => {
                return generatePortInUsePrompt();
            },
        },
    });

    const isProduction = env.production;

    return ({
        devServer: {
            static: {
                directory: path.join(__dirname, 'public'),
            },
            historyApiFallback: {
                index: `${baseUrl}/index.html`,
            },
            server: https ? "https": "http",
            host: HOST,
            allowedHosts: devServerHostCheckDisabled ? "all" : undefined,
            port: PORT,
        },
        devtool: "source-map",
        entry: [ "./src/app.tsx" ],
        mode: isProduction ? "production" : "development",
        module: {
            rules: [
                {
                    test: /\.(tsx|ts|js|jsx)$/,
                    exclude: /node_modules/,
                    use: {
                        loader: "babel-loader"
                    }
                },
                {
                    test: /\.css$/,
                    use: [ "style-loader", "css-loader" ]
                },
                {
                    test: /\.(png|jpg|cur|gif|eot|ttf|woff|woff2|webp)$/,
                    use: [ "file-loader" ]
                },
                {
                    test: /\.html$/,
                    use: [
                        {
                            loader: "html-loader"
                        }
                    ]
                },
                {
                    test: /\.js$/,
                    enforce: "pre",
                    use: [ "source-map-loader" ]
                },
                {
                    test: /\.svg$/,
                    use: ['@svgr/webpack', 'file-loader'],
                },
            ]
        },
        output: {
            path: path.resolve(__dirname, "dist"),
            filename: "[name].js",
            publicPath: baseUrl,
        },
        plugins: [
            new webpack.DefinePlugin({
                "process.env": JSON.stringify(envVars),
            }),
            new HtmlWebpackPlugin({
                template: "./public/index.html"
            }),
            new CopyWebpackPlugin({
                patterns: [
                    { 
                        from: 'public', 
                        to: '',
                        globOptions: {
                            ignore: ['**/index.html']
                        }
                    }
                ],
            }),
        ],
        resolve: {
            extensions: [ ".tsx", ".ts", ".js", ".json" ],
            fallback: {
                "crypto": require.resolve("crypto-browserify"),
                "stream": require.resolve("stream-browserify")
              }
        }
    });
};
