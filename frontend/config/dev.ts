import type { UserConfigExport } from "@tarojs/cli"

export default {
  logger: {
    quiet: false,
    stats: true
  },
  defineConstants: {
    BASE_URL: JSON.stringify('http://localhost:10086')
  },
  mini: {},
  h5: {
    devServer: {
      port: 10086,
      hot: true,
      compress: true,
      proxy: {
        '/apipy': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          pathRewrite: {
            '^/apipy': '/apipy'
          }
        }
      }
    }
  }
} satisfies UserConfigExport<'webpack5'>