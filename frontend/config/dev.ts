import type { UserConfigExport } from "@tarojs/cli"

export default {
  logger: {
    quiet: false,
    stats: true
  },
  defineConstants: {
    BASE_URL: JSON.stringify('')
  },
  mini: {},
  h5: {
    devServer: {
      port: 10086,
      hot: true,
      compress: true,
      proxy: {
        '/apipy': {
          target: 'http://haoguozhi.com',
          changeOrigin: true,
          pathRewrite: {
            '^/apipy': '/apipy'
          }
        }
      }
    }
  }
} satisfies UserConfigExport<'webpack5'>